from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from django.http import HttpRequest

from djangospice.core.payload import Payload

from .widget import BaseWidget


@dataclass(slots=True)
class ActionContext:
    """
    Runtime context passed to an Action.

    The context describes *where* and *how* an action is being executed,
    without exposing execution details.
    """

    #: Widget invoking the action.
    widget: BaseWidget

    #: Current request.
    request: HttpRequest

    #: Current object (row actions).
    object: Any | None = None

    #: Selected objects (bulk actions).
    selected: Sequence[Any] = ()

    #: Extra runtime parameters.
    kwargs: Payload = field(default_factory=Payload)

    @property
    def user(self):
        return self.request.user

    @property
    def is_bulk(self) -> bool:
        return bool(self.selected)

    @property
    def is_row(self) -> bool:
        return self.object is not None