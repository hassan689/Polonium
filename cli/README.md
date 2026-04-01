# Polonium CLI

Modular command-line package for interacting with Polonium backend APIs.

## Structure

```text
cli/
├── polonium_cli/
│   ├── __init__.py
│   ├── main.py
│   ├── client.py
│   └── commands/
│       ├── __init__.py
│       ├── repo.py
│       ├── file.py
│       ├── chat.py
│       └── search.py
└── setup.py
```

## Install

```bash
cd cli
pip install -e .
```

## Basic Commands

```bash
polonium repo connect https://github.com/owner/repo
polonium repo list
polonium repo overview 1
polonium file explain 1 app/main.py
```

