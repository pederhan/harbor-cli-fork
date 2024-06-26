from __future__ import annotations

from typing import Callable
from typing import Dict
from typing import Literal

from harborapi.models.scanner import Severity
from strenum import StrEnum


def blue(message: str) -> str:
    return f"[blue]{message}[/]"


def cyan(message: str) -> str:
    return f"[cyan]{message}[/]"


def green(message: str) -> str:
    return f"[green]{message}[/]"


def magenta(message: str) -> str:
    return f"[magenta]{message}[/]"


def red(message: str) -> str:
    return f"[red]{message}[/]"


def yellow(message: str) -> str:
    return f"[yellow]{message}[/]"


def gold3(message: str) -> str:
    return f"[gold3]{message}[/]"


def bold(message: str) -> str:
    return f"[bold]{message}[/]"


Color = Literal[
    "blue",
    "cyan",
    "green",
    "magenta",
    "red",
    "yellow",
    "bold",
    "gold3",
]
ColorFunc = Callable[[str], str]
COLOR_FUNCTIONS: Dict[Color, ColorFunc] = {
    "blue": blue,
    "cyan": cyan,
    "green": green,
    "magenta": magenta,
    "red": red,
    "yellow": yellow,
    "bold": bold,
    "gold3": gold3,
}


def fallback_color(message: str) -> str:
    """Returns the string as-is."""
    return message


def get_color_func(color: Color) -> ColorFunc:
    try:
        return COLOR_FUNCTIONS[color]
    except KeyError:
        from harbor_cli.logs import logger

        logger.error("Invalid color: %s", color, stacklevel=2)
        return fallback_color


class HealthColor(StrEnum):
    HEALTHY = "green"
    UNHEALTHY = "red"

    @classmethod
    def from_health(cls, health: str | None) -> str:
        if health == "healthy":
            return HealthColor.HEALTHY
        else:
            return HealthColor.UNHEALTHY


class SeverityColor(StrEnum):
    CRITICAL = "dark_red"
    HIGH = "red"
    MEDIUM = "orange3"
    LOW = "green"
    NEGLIGIBLE = "blue"
    NONE = "white"
    UNKNOWN = "white"

    @classmethod
    def from_severity(cls, severity: str | Severity) -> str:
        """Return the color for the given severity level."""
        if isinstance(severity, Severity):
            severity = severity.value
        try:
            color = getattr(cls, severity.upper())
            if isinstance(color, SeverityColor):
                return color
            raise ValueError(f"Invalid severity: {severity}")
        except (AttributeError, ValueError):
            return SeverityColor.UNKNOWN

    @classmethod
    def as_markup(cls, severity: str | Severity) -> str:
        """Return the given severity as a Rich markup-formatted string.

        I.e. "[dark_red]CRITICAL[/]" for Severity.CRITICAL, etc.
        """
        color = cls.from_severity(severity)
        if isinstance(severity, Severity):
            severity = severity.value
        return f"[{color}]{severity.upper()}[/]"
