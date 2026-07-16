from __future__ import annotations

import logging
import threading
from collections.abc import Iterator

from django.core.exceptions import ImproperlyConfigured

from djangospice.apps.discovery import ModuleDiscovery
from djangospice.widgets.base import BaseWidget

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    Thread-safe registry for dynamically discovering and storing widget classes.

    This registry uses an auto-discovery utility to scan the project for
    subclasses of `BaseWidget` inside 'widgets' modules. It utilizes reentrant
    locking (RLock) and double-checked locking patterns to guarantee absolute
    thread safety during lazy initialization, reads, and mutations.
    """

    _widgets: dict[str, type[BaseWidget]] = {}
    _initialized: bool = False
    _lock = threading.RLock()

    @classmethod
    def load(cls) -> None:
        """
        Lazily discover and register all available widget classes.

        Uses double-checked locking to ensure the project-wide discovery
        routine runs safely and exactly once.
        """
        if cls._initialized:
            return

        with cls._lock:
            if cls._initialized:
                return

            ModuleDiscovery.discover(
                module="widgets",
                base_class=BaseWidget,
                callback=cls.register,
            )

            cls._initialized = True

    @classmethod
    def register(cls, widget: type[BaseWidget]) -> None:
        """
        Register a widget class in the internal registry mapping.

        Args:
            widget: The widget class subclassing `BaseWidget`.

        Raises:
            ImproperlyConfigured: If a widget with the same name identifier 
                is already registered.
        """
        with cls._lock:
            if widget.name in cls._widgets:
                raise ImproperlyConfigured(
                    f"BaseWidget '{widget.name}' (`{widget.__name__}`) is already registered."
                )

            cls._widgets[widget.name] = widget

        logger.debug(
            "Registered widget '%s' (%s).",
            widget.name,
            widget.__module__,
        )

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Remove a widget class from the registry by its name.

        Args:
            name: The unique string identifier of the widget to remove.
        """
        cls.load()
        with cls._lock:
            cls._widgets.pop(name, None)

    @classmethod
    def get(cls, name: str) -> type[BaseWidget] | None:
        """
        Retrieve a widget class by its registered name identifier.

        Args:
            name: The string identifier of the widget.

        Returns:
            The matching widget class, or None if not found.
        """
        cls.load()
        return cls._widgets.get(name)
    

    @classmethod
    def widgets(cls) -> dict[str, type[BaseWidget]]:
        """
        Retrieve a shallow copy of all registered widget classes.

        Returns:
            A dictionary mapping widget names to their respective classes.
        """
        cls.load()
        with cls._lock:
            return cls._widgets.copy()

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """
        Retrieve the names of all currently registered widgets.

        Returns:
            A tuple containing all registered widget string identifiers.
        """
        cls.load()
        with cls._lock:
            return tuple(cls._widgets)

    @classmethod
    def values(cls) -> tuple[type[BaseWidget], ...]:
        """
        Retrieve all currently registered widget classes.

        Returns:
            A tuple containing all registered BaseWidget subclasses.
        """
        cls.load()
        with cls._lock:
            return tuple(cls._widgets.values())

    @classmethod
    def clear(cls) -> None:
        """
        Clear the registry state and reset initialization flags.

        Primarily intended to ensure test isolation across environments where 
        mocking or dynamic widget definitions are leveraged.
        """
        with cls._lock:
            cls._widgets.clear()
            cls._initialized = False

    @classmethod       
    def exists(cls, name: str) -> bool:
        """
        Check if a widget is currently registered by name.

        Args:
            name: The string identifier of the widget.
            
        Returns:
            True if the widget is registered, False otherwise.
        """
        return cls.get(name) is not None

    @classmethod
    def groups(cls) -> dict[str | None, list[type[BaseWidget]]]:
        """
        Group all registered widgets by their configured group name.

        Returns:
            A dictionary mapping group names to lists of widget classes.
            Widgets without a specified group will fall under the `None` key.
        """
        groups: dict[str | None, list[type[BaseWidget]]] = {}

        for widget in cls.values():
            groups.setdefault(widget.group, []).append(widget)

        return groups

    @classmethod
    def __iter__(cls) -> Iterator[type[BaseWidget]]:
        """
        Iterate over all registered widget classes.
        
        Note: As a classmethod, you must call `WidgetRegistry.__iter__()` 
        or `iter(WidgetRegistry.values())` explicitly.
        """
        return iter(cls.values())

    @classmethod
    def __len__(cls) -> int:
        """
        Get the total number of registered widgets.
        
        Note: As a classmethod, `len(WidgetRegistry)` will fail natively. 
        Use `WidgetRegistry.__len__()` explicitly.
        """
        cls.load()
        with cls._lock:
            return len(cls._widgets)
        
 