# Plugin Development

Plugins can register additional defensive modules with the local registry.

## Layout

```text
plugins/
  my_plugin/
    plugin.py
```

## Example

```python
from typing import Any

from app.modules.base import Finding, SecurityModule
from app.schemas.common import Severity
from app.schemas.modules import ModuleResult


class ExampleHeaderCheck(SecurityModule):
    id = "example_header_check"
    name = "Example Header Check"
    description = "Demonstrates a safe plugin module."
    category = "web"
    default_severity = Severity.info

    async def run(self, target: str, options: dict[str, Any]) -> ModuleResult:
        return ModuleResult(
            module_id=self.id,
            target=target,
            findings=[
                Finding(
                    title="Example observation",
                    description="This is a defensive observation.",
                    severity=Severity.info,
                    evidence={"target": target},
                    recommendation="Review the observation and document the result.",
                )
            ],
        )


def register(registry):
    registry.register(ExampleHeaderCheck())
```

## Rules

- Keep modules defensive, passive, or explicitly controlled.
- Do not execute arbitrary commands.
- Do not download or execute remote code.
- Do not implement stealth, evasion, credential theft, destructive payloads, or exploitation.
- Validate options and use timeouts for network operations.

## UI-Created Interceptor Modules

The Modules page can create user-owned interceptor modules without writing plugin files. The code must define one
function:

```python
def analyze(request, response):
    return []
```

The backend performs the HTTP request and passes immutable request/response objects to the function. The validator
rejects imports, dunder access, dynamic execution, unsafe builtins, class definitions, and top-level statements outside
`analyze`.
