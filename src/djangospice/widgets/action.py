from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from djangospice.html.attributes import HTMXAttributes
from djangospice.response.response import Response

from .context import ActionContext


class Action(ABC):
    """
    Base executable widget action.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    name: ClassVar[str]
    label: ClassVar[str]

    # ------------------------------------------------------------------
    # Presentation
    # ------------------------------------------------------------------

    icon: ClassVar[str | None] = None

    description: ClassVar[str | None] = None

    css_class: ClassVar[str | None] = None

    order: ClassVar[int] = 100

    groups: ClassVar[tuple[str, ...]] = ()

    # ------------------------------------------------------------------
    # Behaviour
    # ------------------------------------------------------------------

    method: ClassVar[str] = "POST"

    permission: ClassVar[str | None] = None

    confirm: ClassVar[str | None] = None

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def visible(self, context: ActionContext) -> bool:
        return True

    def enabled(self, context: ActionContext) -> bool:
        return True

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def authorize(self, context: ActionContext) -> None:
        """
        Raise PermissionDenied if execution is not allowed.
        """

    def before_execute(self, context: ActionContext) -> None:
        """
        Hook before execute().
        """

    def after_execute(self, context: ActionContext) -> None:
        """
        Hook after execute().
        """

    # ------------------------------------------------------------------
    # HTMX
    # ------------------------------------------------------------------

    def htmx(self, context: ActionContext) -> HTMXAttributes:
        """
        Build HTMX attributes required to invoke this action.
        """

        return (
            HTMXAttributes()
            .request(
                method=self.method,
                url=context.widget.endpoint,
            )
            .with_vals(action=self.name)
        )

    # ------------------------------------------------------------------
    # Execute
    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, context: ActionContext) -> Response:
        """
        Execute the action and return a Response.
        """
        raise NotImplementedError
    
    