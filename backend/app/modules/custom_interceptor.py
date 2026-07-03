from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import httpx

from app.core.constants import DEFAULT_HTTP_TIMEOUT_SECONDS
from app.database.models import CustomModule
from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity, normalize_severity
from app.schemas.modules import ModuleResult

CUSTOM_MODULE_PREFIX = "custom:"
SAFE_BUILTINS = {
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
}
SAFE_METHODS = {
    "append",
    "endswith",
    "find",
    "get",
    "items",
    "join",
    "keys",
    "lower",
    "replace",
    "split",
    "startswith",
    "strip",
    "upper",
    "values",
}
BLOCKED_NODES = (
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Delete,
    ast.Global,
    ast.Import,
    ast.ImportFrom,
    ast.Lambda,
    ast.Nonlocal,
    ast.Raise,
    ast.Try,
    ast.While,
    ast.With,
)
BLOCKED_NAMES = {
    "__builtins__",
    "__import__",
    "breakpoint",
    "compile",
    "delattr",
    "dir",
    "eval",
    "exec",
    "getattr",
    "globals",
    "help",
    "input",
    "locals",
    "memoryview",
    "open",
    "setattr",
    "vars",
}


@dataclass(frozen=True)
class InterceptorRequest:
    method: str
    url: str
    headers: Mapping[str, str]
    body: str = ""


@dataclass(frozen=True)
class InterceptorResponse:
    status_code: int
    url: str
    headers: Mapping[str, str]
    text: str
    body_preview: str


class CustomModuleValidationError(ValueError):
    pass


class CustomInterceptorModule(SecurityModule):
    category = "custom"

    def __init__(self, module: CustomModule) -> None:
        self.module = module
        self.id = module_id_for_custom(module.id)
        self.name = module.title
        self.description = module.description
        self.tags = list(dict.fromkeys(["CUSTOM", *module.tags]))
        self.default_severity = Severity(normalize_severity(module.severity))

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        validate_interceptor_code(self.module.code)
        timeout = float(options.get("timeout_seconds", DEFAULT_HTTP_TIMEOUT_SECONDS))
        request_headers = {"User-Agent": "Exodia Custom Interceptor/0.1"}
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            headers=request_headers,
        ) as client:
            response = await client.get(target)

        request_obj = InterceptorRequest(
            method="GET",
            url=target,
            headers=MappingProxyType({key.lower(): value for key, value in request_headers.items()}),
        )
        response_headers = MappingProxyType({key.lower(): value for key, value in response.headers.items()})
        response_obj = InterceptorResponse(
            status_code=response.status_code,
            url=str(response.url),
            headers=response_headers,
            text=response.text[:20_000],
            body_preview=response.text[:4000],
        )
        raw_findings = execute_interceptor_code(self.module.code, request_obj, response_obj)
        findings = [_finding_from_result(item) for item in raw_findings]
        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=findings,
            raw_data={
                "status_code": response.status_code,
                "url": str(response.url),
                "headers": dict(response.headers),
            },
        )


def module_id_for_custom(module_id: str) -> str:
    return f"{CUSTOM_MODULE_PREFIX}{module_id}"


def custom_id_from_module_id(module_id: str) -> str | None:
    if not module_id.startswith(CUSTOM_MODULE_PREFIX):
        return None
    custom_id = module_id.removeprefix(CUSTOM_MODULE_PREFIX)
    return custom_id or None


def validate_interceptor_code(code: str) -> None:
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as exc:
        raise CustomModuleValidationError(f"Invalid Python syntax: line {exc.lineno}") from exc
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    if len(functions) != 1 or functions[0].name != "analyze":
        raise CustomModuleValidationError("Code must define exactly one function named analyze")
    if [arg.arg for arg in functions[0].args.args] != ["request", "response"]:
        raise CustomModuleValidationError("analyze must receive request and response arguments")
    if len(tree.body) != 1:
        raise CustomModuleValidationError("Only the analyze function definition is allowed at module level")
    _SafeCodeVisitor().visit(tree)


def execute_interceptor_code(
    code: str,
    request: InterceptorRequest,
    response: InterceptorResponse,
) -> list[dict[str, Any]]:
    validate_interceptor_code(code)
    namespace: dict[str, Any] = {}
    exec(compile(code, "<custom-module>", "exec"), {"__builtins__": SAFE_BUILTINS}, namespace)
    result = namespace["analyze"](request, response)
    if result is None:
        return []
    if isinstance(result, dict):
        return [result]
    if isinstance(result, list):
        return [item for item in result if isinstance(item, dict)]
    raise CustomModuleValidationError("analyze must return a dict, a list of dicts, or None")


def _finding_from_result(value: dict[str, Any]) -> Finding:
    title = str(value.get("title") or "Custom module finding")[:240]
    description = str(value.get("description") or value.get("detail") or title)
    severity = Severity(normalize_severity(str(value.get("severity") or "info")))
    raw_evidence = value.get("evidence")
    evidence = {str(key): item for key, item in raw_evidence.items()} if isinstance(raw_evidence, dict) else {}
    recommendation = str(value.get("recommendation") or "Review the custom module result and validate remediation.")
    return Finding(
        title=title,
        description=description,
        severity=severity,
        evidence=evidence,
        recommendation=recommendation,
    )


class _SafeCodeVisitor(ast.NodeVisitor):
    def visit(self, node: ast.AST) -> Any:
        if isinstance(node, BLOCKED_NODES):
            raise CustomModuleValidationError(f"{type(node).__name__} is not allowed in custom modules")
        return super().visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if node.id in BLOCKED_NAMES or node.id.startswith("__"):
            raise CustomModuleValidationError(f"Name {node.id} is not allowed")

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if node.attr.startswith("__"):
            raise CustomModuleValidationError("Dunder attribute access is not allowed")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id not in SAFE_BUILTINS:
                raise CustomModuleValidationError(f"Function {node.func.id} is not allowed")
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr not in SAFE_METHODS:
                raise CustomModuleValidationError(f"Method {node.func.attr} is not allowed")
        else:
            raise CustomModuleValidationError("Dynamic calls are not allowed")
        self.generic_visit(node)
