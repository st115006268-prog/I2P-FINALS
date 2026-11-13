"""Flet backwards-compatibility layer for Arcadia.

Bridges naming and method differences between Flet 0.x and Flet 1.0
(ft.Alignment.CENTER, ft.Border.all, page.push_route, page.show_dialog, etc.)
so all views run seamlessly without runtime AttributeErrors.
"""
import asyncio
import inspect
import sys
import flet as ft

# Silence Windows Python 3.9 ProactorBasePipeTransport.__del__ "RuntimeError: Event loop is closed" on exit
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport

        _orig_proactor_del = _ProactorBasePipeTransport.__del__

        def _silent_proactor_del(self):
            try:
                _orig_proactor_del(self)
            except RuntimeError as e:
                if "Event loop is closed" not in str(e):
                    raise
            except Exception:
                pass

        _ProactorBasePipeTransport.__del__ = _silent_proactor_del
    except Exception:
        pass

# Alignment shims
if not hasattr(ft.Alignment, "CENTER"):
    ft.Alignment.CENTER = ft.alignment.center
    ft.Alignment.CENTER_LEFT = ft.alignment.center_left
    ft.Alignment.CENTER_RIGHT = ft.alignment.center_right
    ft.Alignment.TOP_LEFT = ft.alignment.top_left
    ft.Alignment.TOP_RIGHT = ft.alignment.top_right
    ft.Alignment.TOP_CENTER = ft.alignment.top_center
    ft.Alignment.BOTTOM_LEFT = ft.alignment.bottom_left
    ft.Alignment.BOTTOM_RIGHT = ft.alignment.bottom_right
    ft.Alignment.BOTTOM_CENTER = ft.alignment.bottom_center

# Border & BorderSide shims
if not hasattr(ft.Border, "all"):
    ft.Border.all = staticmethod(ft.border.all)
    ft.Border.only = staticmethod(ft.border.only)
    ft.Border.symmetric = staticmethod(ft.border.symmetric)
if not hasattr(ft, "BorderSide"):
    ft.BorderSide = ft.border.BorderSide

# Padding shims
if not hasattr(ft.Padding, "all"):
    ft.Padding.all = staticmethod(ft.padding.all)
    ft.Padding.only = staticmethod(ft.padding.only)
    ft.Padding.symmetric = staticmethod(ft.padding.symmetric)

# Margin shims
if not hasattr(ft.Margin, "all"):
    ft.Margin.all = staticmethod(ft.margin.all)
    ft.Margin.only = staticmethod(ft.margin.only)
    ft.Margin.symmetric = staticmethod(ft.margin.symmetric)

# BorderRadius shims
if not hasattr(ft.BorderRadius, "all"):
    ft.BorderRadius.all = staticmethod(ft.border_radius.all)
    ft.BorderRadius.only = staticmethod(ft.border_radius.only)
    ft.BorderRadius.horizontal = staticmethod(ft.border_radius.horizontal)
    ft.BorderRadius.vertical = staticmethod(ft.border_radius.vertical)

# InputBorder shims
if not hasattr(ft, "NoInputBorder"):
    ft.NoInputBorder = lambda *args, **kwargs: ft.InputBorder.NONE

# Page navigation & dialog shims
if not hasattr(ft.Page, "push_route"):
    async def _push_route(self, route: str, **kwargs):
        self.go(route, **kwargs)
    ft.Page.push_route = _push_route

# Wrap page.run_task so it accepts both coroutine functions AND regular synchronous functions
_orig_run_task = getattr(ft.Page, "run_task", None)
if _orig_run_task is not None:
    def _safe_run_task(self, handler, *args, **kwargs):
        if inspect.iscoroutinefunction(handler):
            return _orig_run_task(self, handler, *args, **kwargs)
        else:
            async def _async_wrapper():
                res = handler(*args, **kwargs)
                if inspect.isawaitable(res):
                    return await res
                return res
            return _orig_run_task(self, _async_wrapper)
    ft.Page.run_task = _safe_run_task

# Dialog shims (show_dialog / pop_dialog -> open / close)
if not hasattr(ft.Page, "show_dialog"):
    def _show_dialog(self, dlg):
        # SnackBars don't block modal alerts, so keep them separate from dialog stack
        if isinstance(dlg, ft.SnackBar) or hasattr(dlg, "duration"):
            self.open(dlg)
            return
        if not hasattr(self, "_dlg_stack"):
            self._dlg_stack = []
        self._dlg_stack.append(dlg)
        self._active_dlg = dlg
        self.open(dlg)
    ft.Page.show_dialog = _show_dialog

if not hasattr(ft.Page, "pop_dialog"):
    def _pop_dialog(self, dlg=None):
        target = dlg
        if target is None:
            if hasattr(self, "_dlg_stack") and self._dlg_stack:
                target = self._dlg_stack.pop()
            else:
                target = getattr(self, "_active_dlg", None)
        else:
            if hasattr(self, "_dlg_stack") and target in self._dlg_stack:
                self._dlg_stack.remove(target)
        if target is not None:
            target.open = False
            try:
                self.close(target)
            except Exception:
                pass
            try:
                target.update()
            except Exception:
                pass
            try:
                self.update()
            except Exception:
                pass
        self._active_dlg = self._dlg_stack[-1] if (hasattr(self, "_dlg_stack") and self._dlg_stack) else None
    ft.Page.pop_dialog = _pop_dialog


