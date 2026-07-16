from importlib import import_module
from django.apps import AppConfig as BaseConfig


class AppConfig(BaseConfig):
    """
    Base configuration class for custom djangospice applications.
    Extends Django's AppConfig to integrate dependency injection and lifecycle hooks.
    """

    # Human-readable metadata
    description: str | None = None
    url: str | None = None
    icon: str | None = None

    # Runtime flags
    is_default: bool = True
    is_service: bool = False

    # Djangospice namespace (e.g. "billing", "workflow")
    namespace: str | None = None

    # Django application label.
    # Defaults to the namespace if provided, otherwise Django derives it
    # from the application name.
    label: str | None = None

    def __init__(self, app_name, app_module):
        super().__init__(app_name, app_module)

        if self.namespace is None:
            self.namespace = self.name.rsplit(".", 1)[-1]

        if self.label is None:
            self.label = self.namespace
    

    def register(self) -> None:
        """
        Hook executed during the registration phase. 
        Override this method to bind dependencies or set up early-stage configurations.
        """
        pass

    def boot(self) -> None:
        """
        Hook executed during the booting phase. 
        Override this method to initialize services or execute post-registration logic.
        """
        pass

    def discover_module(self, module_name: str) -> bool:
        """
        Discover and import an internal submodule belonging to this application safely.

        Args:
            module_name (str): The dot-notated submodule path suffix (e.g., 'services').

        Raises:
            ModuleNotFoundError: If an internal import *inside* the target app fails.

        Returns:
            bool: True if imported successfully, False if the target root app is missing.
        """
        target = f"{self.name}.{module_name}"

        try:
            import_module(target)
            return True
        except ModuleNotFoundError as exc:
            # Ensure we only absorb errors if the target app itself is absent
            if exc.name == target:
                return False
            raise

    def discover_modules(self, *module_names: str) -> None:
        """
        Batch discovery and import utility for multiple submodules.

        Args:
            *module_names (str): Variadic argument list of submodule string names.
        """
        for module_name in module_names:
            self.discover_module(module_name)