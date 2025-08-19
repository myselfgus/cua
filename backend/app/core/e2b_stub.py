"""E2B Desktop Session Stub Adapter

This module provides a minimal stub implementation that mimics the interface
of an eventual E2B MCP / desktop control client. It allows the frontend and
orchestrator layers to integrate early without requiring the real E2B infra.

Replace this with a real client when the E2B endpoint becomes available.

Contract:
  - create_session(user_id: str | None) -> Session dict
  - exec_command(session_id: str, command: str) -> result dict
  - write_file(session_id: str, path: str, content: str) -> result dict
  - close_session(session_id: str) -> result dict

State is in-memory only and NOT for production use.
"""
from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional

_SESSIONS: Dict[str, Dict[str, Any]] = {}
_DEFAULT_SESSION_TTL = 30 * 60  # 30 minutes


def _now() -> float:
    return time.time()


def create_session(user_id: Optional[str] = None) -> Dict[str, Any]:
    session_id = str(uuid.uuid4())
    desktop_url = f"wss://pending-e2b-endpoint/session/{session_id}"  # placeholder
    data = {
        "session_id": session_id,
        "user_id": user_id,
        "desktop_url": desktop_url,
        "created_at": _now(),
        "expires_at": _now() + _DEFAULT_SESSION_TTL,
        "status": "active",
        "commands": [],
    }
    _SESSIONS[session_id] = data
    return data


def get_session(session_id: str) -> Dict[str, Any]:
    sess = _SESSIONS.get(session_id)
    if not sess:
        raise KeyError("session_not_found")
    if sess["expires_at"] < _now():
        sess["status"] = "expired"
    return sess


def exec_command(session_id: str, command: str) -> Dict[str, Any]:
    sess = get_session(session_id)
    if sess["status"] != "active":
        return {"error": "session_inactive", "status": sess["status"]}
    # Simulated execution result
    result = {
        "command": command,
        "stdout": f"(stub) executed: {command}",
        "stderr": "",
        "exit_code": 0,
        "ts": _now(),
    }
    sess["commands"].append(result)
    return result


def write_file(session_id: str, path: str, content: str) -> Dict[str, Any]:
    sess = get_session(session_id)
    if sess["status"] != "active":
        return {"error": "session_inactive", "status": sess["status"]}
    # We only simulate persistence by appending to commands log
    entry = {
        "action": "write_file",
        "path": path,
        "bytes": len(content.encode("utf-8")),
        "ts": _now(),
    }
    sess["commands"].append(entry)
    return {"ok": True, **entry}


def close_session(session_id: str) -> Dict[str, Any]:
    sess = get_session(session_id)
    sess["status"] = "closed"
    return {"ok": True, "session_id": session_id, "status": "closed"}


def list_sessions() -> Dict[str, Any]:
    return {
        "count": len(_SESSIONS),
        "items": [
            {k: v for k, v in s.items() if k != "commands"} for s in _SESSIONS.values()
        ],
    }
