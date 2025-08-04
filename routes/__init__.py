# =============================
# routes/__init__.py
# =============================

# Public interface for the routes module.
# This module is responsible for handling and dispatching incoming WebSocket requests.
# It may also include functions for user commands, system commands, or configuration updates.

from .router import dispatch
from .handlers import handler_map

__all__ = ["handler_map", "dispatch"]