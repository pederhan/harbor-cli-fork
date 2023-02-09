from __future__ import annotations

from typing import Any
from typing import Sequence

from rich.table import Table

from ..formatting.builtin import plural_str


def get_table(
    title: str | None = None,
    data: Sequence[Any] | None = None,
    pluralize: bool = True,
    columns: list[str] | None = None,
    **kwargs: Any,
) -> Table:
    """Get a table with a title."""
    # NOTE: This is a bug waiting to manifest itself.
    # Maybe we should raise exception if we pass title and pluralize
    # but not data.
    if title and pluralize and data is not None:
        title = plural_str(title, data)

    # Set kwargs defaults (so we don't accidentally pass them twice)
    kwargs.setdefault("show_header", True)
    kwargs.setdefault("expand", True)
    kwargs.setdefault("header_style", "bold magenta")

    table = Table(
        title=title,
        **kwargs,
    )
    if columns is not None:
        for column in columns:
            table.add_column(column)
    return table