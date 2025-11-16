# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

profit-trace is a Python 3.13+ project managed with `uv` (fast Python package manager). The project is currently in early development with a minimal codebase.

## Development Commands

This project uses `uv` for dependency management and development workflows.

### Setup
```bash
# Install dependencies (including dev dependencies)
uv sync
```

### Code Quality
```bash
# Run type checking
uv run mypy .

# Run linting and formatting
uv run ruff check .
uv run ruff format .
```

### Testing
```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest path/to/test_file.py

# Run a specific test function
uv run pytest path/to/test_file.py::test_function_name
```

### Running the Application
```bash
# Run the main script
uv run python main.py
```

## Project Structure

Currently minimal:
- `main.py` - Entry point with basic hello world functionality
- `pyproject.toml` - Project metadata and dependencies
- Dev tools configured: mypy, pytest, ruff

## Development Notes

- Python 3.13+ required
- Uses `uv` instead of pip/poetry for package management
- Type checking enforced with mypy
- Code quality tools: ruff for linting and formatting
