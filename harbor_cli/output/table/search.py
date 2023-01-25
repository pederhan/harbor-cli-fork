from __future__ import annotations

from typing import Sequence

from harborapi.models.models import ChartVersion
from harborapi.models.models import Search
from harborapi.models.models import SearchRepository
from harborapi.models.models import SearchResult
from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from ...logs import logger
from ..formatting.builtin import bool_str
from .project import project_table


def search_panel(search: Sequence[Search]) -> Panel:
    """Display one or more repositories in a table."""
    if len(search) > 1:
        logger.warning("Can only display one search result at a time.")
    s = search[0]  # guaranteed to be at least one result

    tables = []
    # Re-use the project table function
    if s.project:
        tables.append(project_table(s.project))

    if s.repository:
        tables.append(searchrepo_table(s.repository))

    if s.chart:
        tables.append(searchresult_table(s.chart))

    # TODO: chart results when they are available

    return Panel(Group(*tables), title=f"Search Results", expand=True)


def searchrepo_table(repos: Sequence[SearchRepository]) -> Table:
    table = Table(show_header=True, title="Repositories", header_style="bold magenta")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Artifacts")
    table.add_column("Public")
    for repo in repos:
        table.add_row(
            str(repo.project_name),
            str(repo.repository_name),
            str(repo.artifact_count),
            bool_str(repo.project_public),
        )
    return table


def searchresult_table(results: Sequence[SearchResult]) -> Table:
    """Table of Helm chart search results."""
    table = Table(title="Charts", show_header=True, header_style="bold magenta")
    table.add_column("Project")
    table.add_column("Match")  # ??
    table.add_column("Digest")
    # TODO: sort by score
    for result in results:
        if not result.chart:
            result.chart = ChartVersion()
        table.add_row(
            str(result.name),
            str(result.score),
            str(result.chart.digest),
        )
    return table