from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session, selectinload

from app.core.logging import app_logger
from app.database.models import CustomModule, Finding, ModuleExecutionLog, Scan
from app.database.session import SessionLocal
from app.jobs.schemas import ScanEvent
from app.modules.base import SecurityModule
from app.modules.custom_interceptor import CustomInterceptorModule, custom_id_from_module_id
from app.plugins.registry import module_registry
from app.schemas.common import risk_score_for_severities


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, set[asyncio.Queue[ScanEvent]]] = defaultdict(set)
        self._history: dict[str, list[ScanEvent]] = defaultdict(list)

    async def publish(self, event: ScanEvent) -> None:
        self._history[event.scan_id].append(event)
        self._history[event.scan_id] = self._history[event.scan_id][-500:]
        for queue in list(self._subscribers[event.scan_id]):
            await queue.put(event)

    async def stream(self, scan_id: str) -> AsyncIterator[str]:
        queue: asyncio.Queue[ScanEvent] = asyncio.Queue()
        self._subscribers[scan_id].add(queue)
        try:
            for event in self._history.get(scan_id, []):
                yield self._format_sse(event)
            while True:
                event = await queue.get()
                yield self._format_sse(event)
                if event.type in {"scan_completed", "scan_failed", "scan_canceled"}:
                    break
        finally:
            self._subscribers[scan_id].discard(queue)

    @staticmethod
    def _format_sse(event: ScanEvent) -> str:
        payload = event.model_dump(mode="json")
        return f"event: {event.type}\ndata: {json.dumps(payload)}\n\n"


class JobManager:
    def __init__(self) -> None:
        self.event_bus = EventBus()
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._options: dict[str, dict[str, dict[str, Any]]] = {}

    def start_scan(self, scan_id: str, options: dict[str, dict[str, Any]] | None = None) -> None:
        if scan_id in self._tasks and not self._tasks[scan_id].done():
            return
        self._options[scan_id] = options or {}
        self._tasks[scan_id] = asyncio.create_task(self._run_scan(scan_id))

    async def cancel_scan(self, scan_id: str) -> bool:
        task = self._tasks.get(scan_id)
        if task and not task.done():
            task.cancel()
            return True
        with SessionLocal() as db:
            scan = db.get(Scan, scan_id)
            if scan and scan.status in {"pending", "running"}:
                scan.status = "canceled"
                scan.finished_at = datetime.now(UTC)
                db.commit()
                await self._publish_and_log(db, scan_id, "scan_canceled", "Scan canceled", None)
                return True
        return False

    async def _run_scan(self, scan_id: str) -> None:
        with SessionLocal() as db:
            scan = db.query(Scan).options(selectinload(Scan.target)).filter(Scan.id == scan_id).one_or_none()
            if scan is None:
                return
            try:
                scan.status = "running"
                scan.started_at = datetime.now(UTC)
                db.commit()
                await self._publish_and_log(db, scan_id, "scan_started", "Scan started", None)

                for module_id in scan.modules:
                    module = _resolve_module(db, scan.user_id, module_id)
                    if module is None:
                        await self._publish_and_log(
                            db,
                            scan_id,
                            "scan_log",
                            f"Skipping unknown module {module_id}",
                            module_id,
                        )
                        continue

                    scan.current_module = module_id
                    db.commit()
                    await self._publish_and_log(db, scan_id, "module_started", f"Running {module.name}", module_id)

                    try:
                        module_options = self._options.get(scan_id, {}).get(module_id, {})
                        result = await module.run(scan.target.value, module_options)
                    except asyncio.CancelledError:
                        raise
                    except Exception as exc:
                        app_logger.exception("Module {} failed", module_id)
                        await self._publish_and_log(
                            db,
                            scan_id,
                            "scan_log",
                            f"Module {module_id} failed safely: {type(exc).__name__}",
                            module_id,
                            {"error_type": type(exc).__name__},
                        )
                        await self._publish_and_log(
                            db,
                            scan_id,
                            "module_completed",
                            f"{module.name} completed with errors",
                            module_id,
                        )
                        continue

                    for finding in result.findings:
                        db_finding = Finding(
                            scan_id=scan_id,
                            module_id=module_id,
                            title=finding.title,
                            description=finding.description,
                            severity=(
                                finding.severity.value
                                if hasattr(finding.severity, "value")
                                else str(finding.severity)
                            ),
                            evidence=finding.evidence,
                            recommendation=finding.recommendation,
                        )
                        db.add(db_finding)
                        db.commit()
                        await self._publish_and_log(
                            db,
                            scan_id,
                            "finding_detected",
                            finding.title,
                            module_id,
                            {
                                "finding": {
                                    "id": db_finding.id,
                                    "title": db_finding.title,
                                    "severity": db_finding.severity,
                                    "module_id": db_finding.module_id,
                                }
                            },
                        )

                    await self._publish_and_log(
                        db,
                        scan_id,
                        "module_completed",
                        f"{module.name} completed",
                        module_id,
                        {"findings": len(result.findings), "raw_data": result.raw_data},
                    )

                db.refresh(scan)
                severities = [finding.severity for finding in scan.findings]
                scan.risk_score = risk_score_for_severities(severities)
                scan.current_module = None
                scan.status = "completed"
                scan.finished_at = datetime.now(UTC)
                db.commit()
                await self._publish_and_log(
                    db,
                    scan_id,
                    "scan_completed",
                    "Scan completed",
                    None,
                    {"risk_score": scan.risk_score},
                )
            except asyncio.CancelledError:
                scan.status = "canceled"
                scan.finished_at = datetime.now(UTC)
                scan.current_module = None
                db.commit()
                await self._publish_and_log(db, scan_id, "scan_canceled", "Scan canceled", None)
            except Exception as exc:
                app_logger.exception("Scan {} failed", scan_id)
                scan.status = "failed"
                scan.finished_at = datetime.now(UTC)
                scan.current_module = None
                db.commit()
                await self._publish_and_log(
                    db,
                    scan_id,
                    "scan_failed",
                    f"Scan failed safely: {type(exc).__name__}",
                    None,
                    {"error_type": type(exc).__name__},
                )
            finally:
                self._tasks.pop(scan_id, None)
                self._options.pop(scan_id, None)

    async def _publish_and_log(
        self,
        db: Session,
        scan_id: str,
        event_type: str,
        message: str,
        module_id: str | None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        event = ScanEvent(
            type=event_type,
            scan_id=scan_id,
            module_id=module_id,
            message=message,
            payload=payload or {},
        )
        db.add(
            ModuleExecutionLog(
                scan_id=scan_id,
                module_id=module_id,
                event_type=event_type,
                message=message,
                payload=payload or {},
                created_at=event.timestamp,
            )
        )
        db.commit()
        await self.event_bus.publish(event)


job_manager = JobManager()


def _resolve_module(db: Session, user_id: str | None, module_id: str) -> SecurityModule | None:
    module = module_registry.get(module_id)
    if module is not None:
        return module
    custom_id = custom_id_from_module_id(module_id)
    if custom_id is None or user_id is None:
        return None
    custom = (
        db.query(CustomModule)
        .filter(CustomModule.id == custom_id, CustomModule.user_id == user_id, CustomModule.active.is_(True))
        .one_or_none()
    )
    return CustomInterceptorModule(custom) if custom is not None else None
