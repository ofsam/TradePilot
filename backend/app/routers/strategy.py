"""Strategy routes (recovered bytecode) with a real EXECUTION_ENABLED gate."""

from __future__ import annotations

from functools import wraps

from fastapi import HTTPException

from app._pyc_boot import load_into
from app.execution_gate import is_execution_enabled

load_into(globals(), "app_routers___pycache___strategy.cpython-311.pyc")


def _stamp(value):
    if isinstance(value, dict):
        out = {key: _stamp(item) for key, item in value.items()}
        if "execution_enabled" in out:
            out["execution_enabled"] = is_execution_enabled()
        return out
    if isinstance(value, list):
        return [_stamp(item) for item in value]
    return value


def _wrap(endpoint, *, require_enabled: bool = False):
    @wraps(endpoint)
    def wrapped(*args, **kwargs):
        if require_enabled and not is_execution_enabled():
            raise HTTPException(
                status_code=409,
                detail="Execution is disabled. Set EXECUTION_ENABLED=true in backend/.env and restart.",
            )
        return _stamp(endpoint(*args, **kwargs))

    return wrapped


for _route in router.routes:  # noqa: F821 — provided by load_into
    endpoint = getattr(_route, "endpoint", None)
    if endpoint is None:
        continue
    require = getattr(_route, "path", "") == "/strategy/execute"
    wrapped = _wrap(endpoint, require_enabled=require)
    _route.endpoint = wrapped
    dependant = getattr(_route, "dependant", None)
    if dependant is not None:
        dependant.call = wrapped
