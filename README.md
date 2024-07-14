# Process Data Flow - An example of flow that receive/transform/register some data.

[![Linting](https://github.com/danbailo/process-data-flow/actions/workflows/lint.yaml/badge.svg?branch=main)](https://github.com/danbailo/process-data-flow/actions/workflows/lint.yaml)

*Repository generated with [danbailo-cookiecutter-template](https://github.com/danbailo/danbailo-cookiecutter-template)*

## Make
The project uses a [Makefile](Makefile) to facilitate project installation, lint execution, typing and testing.

### Preparing virtual enviroment

It is highly recommended to use virtual environments when developing Python projects.

### Using poetry

Install [poetry](https://github.com/python-poetry/poetry) then install the project using Make.

```
make install
```

### Using pyenv

Install the [prerequisites](https://github.com/pyenv/pyenv/wiki/Common-build-problems#prerequisites) and then install [pyenv](https://github.com/pyenv/pyenv-installer). After install and configure pyenv, just install the project using Make.

```
make install_with_pyenv
```

### Checkers

`make check_format` - Checks code formatting.

`make format` - Automatically formats the code.

`make check_lint` - Checks the code lint.

`make lint` - Formats the code by automatically correcting the lint.

`make check_types` - Checks the typing hinting of the code.

`make check_all` - Runs all the project's "checkers" and tests signaling when everything is ok. This way, it is certain that the pull-request pipeline will be ready to go to main.

All settings defined in formatting, typing, lint, etc. They are defined in the Python project configuration file - [pyproject.toml](pyproject.toml).

## Running project

By first, init RabbitMQ and Redis containers using `make init_containers`, then, you can start the API's through this commands:

**Magalu API**
```bash
python -m process_data_flow api magalu
```

**Market API**
```bash
python -m process_data_flow api market
```

After start the API's, you can start the scheduler that will send the messages to RabbitMQ flow:

```bash
python -m process_data_flow scheduler send-extract-data-to-rabbitmq
```

Finally, start the consumers using the following commands:

**Product consumer**
```bash
python -m process_data_flow consumer product
```

**Market Query**
```bash
python -m process_data_flow consumer market-query
```

**Register Product**
```bash
python -m process_data_flow consumer register-product
```