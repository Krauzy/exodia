from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database.session import get_db
from app.jobs.manager import JobManager, job_manager
from app.plugins.registry import ModuleRegistry, module_registry


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_module_registry() -> ModuleRegistry:
    return module_registry


def get_job_manager() -> JobManager:
    return job_manager
