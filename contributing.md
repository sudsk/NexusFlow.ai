# Contributing to NexusFlow

Thank you for considering contributing to NexusFlow! This document outlines the process for contributing to the project and how to get started.

## Code of Conduct

By participating in this project, you agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

There are many ways to contribute to NexusFlow:

1. **Report bugs**: Submit issues for any bugs you encounter
2. **Suggest features**: Submit issues for any features you'd like to see
3. **Improve documentation**: Submit PRs to improve documentation
4. **Fix bugs**: Submit PRs to fix bugs
5. **Add features**: Submit PRs to add new features

## Development Workflow

1. Fork the repository
2. Clone your fork
3. Create a new branch for your changes
4. Make your changes
5. Run tests to ensure your changes work
6. Commit your changes
7. Push your changes to your fork
8. Submit a PR

## Setup Development Environment

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install the package in development mode:

```bash
pip install -e ".[dev]"
```

3. Install pre-commit hooks:

```bash
pre-commit install
```

## Running Tests

To run the tests:

```bash
pytest
```

To run the tests with coverage:

```bash
pytest --cov=nexusflow
```

## Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

You can run all of these tools at once with:

```bash
pre-commit run --all-files
```

## Pull Request Process

1. Ensure your code passes all tests and style checks
2. Update the documentation if necessary
3. Update the tests if necessary
4. Update the README.md if necessary
5. Submit a PR with a clear description of your changes

## Releasing

Releases are managed by the core team. If you'd like to suggest a release, please open an issue.

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
