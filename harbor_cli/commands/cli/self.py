from __future__ import annotations

import itertools
import os
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

import typer
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError

from ...config import DEFAULT_CONFIG_FILE
from ...config import EnvVar
from ...config import HarborCLIConfig
from ...models import BaseModel
from ...output.console import error
from ...output.console import exit_err
from ...output.console import exit_ok
from ...output.console import info
from ...output.console import print_toml
from ...output.console import success
from ...output.formatting.path import path_link
from ...output.render import render_result
from ...output.table._utils import get_table
from ...output.table.anysequence import AnySequence
from ...state import get_state
from ...style import render_cli_command
from ...style import render_cli_value
from ...style import render_config_option
from ...style.style import render_cli_option

if TYPE_CHECKING:
    from rich.table import Table

# Create a command group
app = typer.Typer(
    name="self",
    help="Manage the CLI itself.",
    no_args_is_help=True,
)

config_cmd = typer.Typer(
    name="config",
    help="CLI configuration.",
    no_args_is_help=True,
)
app.add_typer(config_cmd)

keyring_cmd = typer.Typer(
    name="keyring",
    help="Manage keyring credentials.",
    no_args_is_help=True,
)
app.add_typer(keyring_cmd)


def render_config(config: HarborCLIConfig, as_toml: bool) -> None:
    if as_toml:
        print_toml(config.toml(expose_secrets=False))
    else:
        render_result(config)


@config_cmd.callback()
def callback(ctx: typer.Context) -> None:
    state = get_state()
    # Every other command than "path" and "write" requires a config file
    if ctx.invoked_subcommand not in ["path", "write", "env"]:
        # if not hasattr(state.config, "config_file") or state.config.config_file is None:
        if state.config.config_file is None or not state.is_config_loaded:
            exit_err(
                "No configuration file loaded. A configuration file must exist to use this command."
            )


@config_cmd.command("get")
def get_cli_config(
    ctx: typer.Context,
    # TODO: Add support for fetching keys with dot notation
    key: Optional[str] = typer.Argument(
        None, help="Specific config key to get value of."
    ),
    as_toml: bool = typer.Option(
        True,
        "--toml/--no-toml",
        help="Show the current configuration in TOML format after setting the value. Overrides --format.",
    ),
) -> None:
    """Show the current CLI configuration."""
    state = get_state()
    if key:
        try:
            if (attrs := key.split(".")) and len(attrs) > 1:
                obj = getattr(state.config, attrs[0])
                for attr in attrs[1:-1]:
                    obj = getattr(obj, attr)
                value = getattr(obj, attrs[-1])
            else:
                value = getattr(state.config, key)
        except AttributeError:
            exit_err(f"Invalid config key: {render_cli_value(key)}")
        else:
            render_result(value)
    else:
        render_config(state.config, as_toml)
        if state.config.config_file is not None:
            info(
                f"[bold]Source:[/bold] {path_link(state.config.config_file)}",
                panel=True,
            )


@config_cmd.command(
    "keys",
    help=f"Show all config keys that can be modified with {render_cli_command('set')}.",
)
def get_cli_config_keys(ctx: typer.Context) -> None:
    state = get_state()

    def get_fields(field: dict[str, Any], current: str) -> list[str]:
        fields: List[str] = []
        for sub_key, sub_value in field.items():
            if isinstance(sub_value, dict):
                fields.extend(
                    get_fields(
                        sub_value,  # pyright: ignore[reportUnknownArgumentType]
                        f"{current}.{sub_key}",
                    )
                )
            else:
                fields.append(f"{current}.{sub_key}")
        return fields

    d = state.config.model_dump()
    keys = itertools.chain.from_iterable(
        get_fields(value, key) for key, value in d.items()
    )
    render_result(AnySequence(values=list(keys), title="Config Keys"))


@config_cmd.command(
    "set",
    no_args_is_help=True,
    help=f"Modify a CLI configuration value. Use {render_cli_command('keys')} to see all available keys.",
)
def set_cli_config(
    ctx: typer.Context,
    key: str = typer.Argument(
        help="Key to set. Subkeys can be specified using dot notation. e.g. [green]'harbor.url'[/]",
    ),
    value: str = typer.Argument(help="Value to set."),
    path: Path = typer.Option(None, "--path", help="Path to save configuration file."),
    session: bool = typer.Option(
        False,
        "--session",
        help="Set the value in the current session only. The value will not be saved to disk. Only useful in REPL mode.",
    ),
    show_config: bool = typer.Option(
        False,
        "--show/--no-show",
        help="Show the current configuration after setting the value.",
    ),
    as_toml: bool = typer.Option(
        True,
        "--toml/--no-toml",
        help="Render updated config as TOML in terminal if [green]--show[/] is set. Overrides global option [green]--format[/].",
    ),
) -> None:
    if not key:
        exit_err("No key specified.")

    state = get_state()

    try:
        if (attrs := key.split(".")) and len(attrs) > 1:
            obj = getattr(state.config, attrs[0])
            for attr in attrs[1:-1]:
                obj = getattr(obj, attr)
            assert isinstance(obj, PydanticBaseModel)
            to_set = attrs[-1]
            if to_set not in obj.model_fields:
                raise AttributeError
            setattr(obj, attrs[-1], value)
        else:
            # Top-level primitive keys are supported, but we shouldn't have any!
            # It's just here in case we do add it in the future.
            # Overwriting top-level model keys is not allowed.
            obj = getattr(state.config, key)
            if isinstance(obj, PydanticBaseModel):
                raise AttributeError("Overwriting config tables is not allowed.")
            setattr(state.config, key, value)
    except ValidationError as e:
        # There should be at least one error, but we play it safe
        errors = e.errors()
        error = errors[0]["msg"] if errors else str(e)
        exit_err(f"Invalid value for key {key!r}: {error}")
    except (
        ValueError,  # setattr failed for unknown model field (Pydantic)
        AttributeError,  # getattr failed
    ):
        exit_err(f"Invalid config key: {key!r}")

    if not session:
        state.config.save(path=path)

    if show_config:
        render_config(state.config, as_toml)

    success(f"Set {render_config_option(key)} to {render_cli_value(value)}")


@config_cmd.command(
    "write",
    short_help="Write the current session configuration to disk.",
    help=(
        "Write the current [bold]session[/] configuration to disk. "
        f"Used to save changes made with {render_cli_command('set --session')} in REPL mode."
    ),
)
def write_session_config(
    ctx: typer.Context,
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        help="Path to save configuration file. Uses current config file path if not specified.",
    ),
) -> None:
    state = get_state()
    save_path = path or state.config.config_file
    if save_path is None:
        exit_err(
            f"No path specified and no path found in current configuration. Use {render_cli_option('--path')} to specify a path."
        )
    state.config.save(path=save_path)
    success(f"Saved configuration to [green]{save_path}[/]")


@config_cmd.command(
    "path",
    help="Show the path to the current configuration file, or default path if no config is loaded.",
)
def show_config_path(ctx: typer.Context) -> None:
    state = get_state()
    path = state.config.config_file or DEFAULT_CONFIG_FILE
    if not path.exists():
        info("File does not exist.")
    elif path.is_dir():
        # this branch should be unreachable since HarborCLIConfig.from_file()
        # should fail if the path is a directory
        error(
            "Path is a directory. Delete the directory so a config file can be created."
        )
    elif not path.read_text().strip():
        info("File exists, but is empty.")
    render_result(path, ctx)


# TODO: add reload config command


class EnvVars(BaseModel):
    envvars: Dict[str, str] = {}

    def as_table(self, **kwargs: Any) -> Iterable[Table]:  # type: ignore
        table = get_table("Environment Variables", columns=["Variable", "Value"])
        for envvar, value in self.envvars.items():
            table.add_row(envvar, value)
        yield table


@config_cmd.command()
def env(
    ctx: typer.Context,
    all: bool = typer.Option(
        False, "-a", "--all", help="List all environment variables."
    ),
) -> None:
    """Show active Harbor CLI environment variables."""
    active: Dict[str, str] = {}
    for env_var in sorted(EnvVar):
        val = os.environ.get(env_var)
        if not all and val is None:
            continue
        active[str(env_var)] = val or ""

    if not active:
        exit_ok("No environment variables set.")

    render_result(EnvVars(envvars=active))


@keyring_cmd.command("status")
def keyring_status(ctx: typer.Context) -> None:
    """Show the current keyring backend and its status."""
    from harbor_cli.utils.keyring import get_backend
    from harbor_cli.utils.keyring import keyring_supported

    if keyring_supported():
        info(f"Keyring backend: {get_backend()}")
    else:
        error("Keyring is not supported on this platform.")
