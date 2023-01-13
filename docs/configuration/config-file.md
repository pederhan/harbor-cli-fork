# Configuration file

In the previous section, we created a config file and went through the interactive wizard. This section will go through the configuration file in more detail.

## Sample configuration file

```toml
{% include "sample_config.toml" %}
```

**NOTE**: The name of the `output.JSON` table is case-sensitive. The reason this name is upper-case is due to a conflict with the built-in Pydantic `json` method. This will hopefully be fixed in a future release.


## Configuration file structure

The configuration file is structured as a [TOML](https://toml.io/en/) file. The TOML file is divided into tables, which are defined by square brackets. The tables are then divided into key-value pairs, where the key is the name of the setting, and the value is the value of the setting.

The configuration file is divided into the following tables:

- [harbor](#harbor)
- [logging](#logging)
- [output](#output)
- [output.table](#outputtable)
- [output.JSON](#outputjson)
- [output.schema](#outputschema)

### `harbor`

The `harbor` table contains settings related to your Harbor instance. There are 3 main ways of authenticating with Harbor:

1. Using a username and password
2. Using Base64-encoded basic access credentials (`username:password` in Base64). This is not safer than using a username and password, as it only obscures the credentials, but does not encrypt them.
3. Using a Harbor robot account with a JSON credentials file. See [Create Project Robot Accounts](https://goharbor.io/docs/2.5.0/working-with-projects/project-configuration/create-robot-accounts/) and [Create System Robot Accounts](https://goharbor.io/docs/2.2.0/administration/robot-accounts/) for more information on how to create robot accounts. Robot accounts can also be created through the API with the help of using `harborapi`, as described in [this](https://pederhan.github.io/harborapi/usage/creating-system-robot/) guide.

The order in which they are specified here is also the order they are evaluated. If multiple methods are specified, the first one that is valid will be used.


#### `harbor.url`

The URL of your Harbor instance.

```toml
[harbor]
url = "https://harbor.example.com"
```

#### `harbor.username`

One of the 3 ways to authenticate with Harbor. The username to use when authenticating with Harbor. When `username` is specified, `secret` must also be specified.

```toml
[harbor]
username = "admin"
```

#### `harbor.secret`

The secret (password) to use when authentication with a username. When `secret` is specified, `username` must also be specified.

```toml
[harbor]
secret = "password"
```

#### `harbor.basicauth`

The Base64-encoded basic access credentials to use when authenticating with Harbor. When `basicauth` is specified, `username` and `secret` must not be specified.

```toml
[harbor]
basicauth="dXNlcm5hbWU6cGFzc3dvcmQ="
```

#### `harbor.credentials_file`

The path to the JSON credentials file to use when authenticating. Typically obtained when creating a Robot Account. When `credentials_file` is specified, `username` and `secret` and `basicauth` must not be specified.

```toml
[harbor]
credentials_file = "/path/to/credentials.json"
```

### `logging`

The `logging` table contains settings related to configuring logging. Harbor CLI currently uses the [loguru](https://github.com/Delgan/loguru) logging library, but this might change in the future. None of the options pertain specifically to loguru, but are instead generic logging options.


#### `logging.enabled`

Whether or not to enable logging. The default is `true`.

```toml
[logging]
enabled = true
```

#### `logging.structlog`

Whether or not to enable [structured logging](https://loguru.readthedocs.io/en/stable/overview.html#structured-logging-as-needed). The default is `false`.

```toml
[logging]
structlog = false
```

#### `logging.level`

The logging level to use. The default is `INFO`. The available logging levels are:

- `TRACE`
- `DEBUG`
- `INFO`
- `SUCCESS`
- `WARNING`
- `ERROR`
- `CRITICAL`

```toml
[logging]
level = "INFO"
```

### `output`

The `output` table contains settings related to the output of Harbor CLI.


#### `output.format`

Harbor CLI currently supports {{ formats | length }} different output formats:

{% for format in formats %}
- `{{ format }}`
{% endfor %}

See [Formats](/configuration/formats) for more information on the different output formats.

```toml
[output]
format = "table"
```

#### `output.table`

The `output.table` table contains settings related to the `table` output format.

See [Formats: Table](/configuration/formats/#table-table) for more information.

#### `output.table.description`

Whether or not to include the descriptions of each value in the output tables. Mutually exclusive with [`output.table.compact`](#outputtablecompact). The default is `false`.

```toml
[output.table]
description = false
```

#### `output.table.compact`

Whether or not to use compact output tables. Mutually exclusive with [`output.table.description`](#outputtabledescription). The default is `false`. Takes precedence over [`output.table.description`](#outputtabledescription) if both are enabled.

```toml
[output.table]
compact = false
```

See [Formats: Compact Table](/configuration/formats/#compact-tables) for more information.