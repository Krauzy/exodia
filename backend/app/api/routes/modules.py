from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_module_registry
from app.plugins.registry import ModuleRegistry
from app.schemas.modules import ModuleInfo

router = APIRouter(prefix="/modules", tags=["modules"])
RegistryDep = Annotated[ModuleRegistry, Depends(get_module_registry)]


@router.get("", response_model=list[ModuleInfo])
def list_modules(registry: RegistryDep) -> list[ModuleInfo]:
    return registry.list()
