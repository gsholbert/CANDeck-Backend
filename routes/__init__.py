# =============================
# routes/__init__.py
# =============================

# Public interface for the routes module.
# This module is responsible for handling and dispatching incoming WebSocket requests.
# It may also include functions for user commands, system commands, or configuration updates.

from .dispatcher import dispatch_message
from .handlers import get_all_routes

__all__ = ["dispatch_message", "get_all_routes"]