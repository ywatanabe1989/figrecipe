<!-- ---
!-- Timestamp: 2025-12-23 03:28:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/figrecipe/CONTRIBUTING.md
!-- --- -->

# Contributing to FigRecipe

Thank you for your interest in contributing to FigRecipe! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git

### Development Setup

1. Fork the repository on GitHub

2. Clone your fork:
   ```bash
   git clone https://github.com/ywatanabe1989/figrecipe.git
   cd figrecipe
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or: .venv\Scripts\activate  # Windows
   ```

4. Install in development mode with all extras:
   ```bash
   pip install -e ".[all]"
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

This project uses [ruff](https://github.com/astral-sh/ruff) for linting and formatting.

- Line length: 88 characters
- Target Python version: 3.9+
- Enabled rules: E (pycodestyle errors), F (pyflakes), W (pycodestyle warnings), I (isort)

### Running the Linter

```bash
make lint
# or
ruff check src/ tests/
```

### Formatting Code

```bash
make format
# or
ruff format src/ tests/
```

## Testing

Tests are written with pytest and located in the `tests/` directory.

### Running Tests

```bash
make test
# or
pytest tests/ -v
```

### Writing Tests

- Test files should be named `test_*.py`
- Place tests in the `tests/` directory
- Follow existing test patterns in the codebase
- Ensure tests are deterministic and don't depend on external state

## Project Structure

```
figrecipe/
├── src/figrecipe/       # Main package source
│   ├── _editor/         # GUI editor components
│   ├── _signatures/     # Function signature definitions
│   ├── _utils/          # Utility functions
│   ├── _wrappers/       # Matplotlib wrappers
│   ├── styles/          # Style presets
│   ├── _recorder.py     # Recording functionality
│   ├── _reproducer.py   # Reproduction functionality
│   ├── _seaborn.py      # Seaborn integration
│   ├── _serializer.py   # YAML serialization
│   └── pyplot.py        # Drop-in pyplot replacement
├── tests/               # Test suite
├── examples/            # Example notebooks
└── docs/                # Documentation
```

## Making Changes

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add support for new plot type
fix: Correct mm-to-inch conversion
docs: Update API documentation
test: Add tests for reproducer module
refactor: Simplify serialization logic
```

### Pull Request Process

1. Ensure all tests pass: `make test`
2. Run the linter: `make lint`
3. Update documentation if needed
4. Push to your fork and create a Pull Request against `develop` branch
5. Fill in the PR template with a clear description of changes

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update the CHANGELOG.md for notable changes
- Ensure CI passes before requesting review

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- Python version
- FigRecipe version (`pip show figrecipe`)
- Operating system
- Minimal code example that reproduces the issue
- Full error traceback if applicable

### Feature Requests

For feature requests, please describe:

- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## Development Tips

### Running the Demo Notebook

```bash
make notebook
```

### Generating PDF from Notebook

```bash
make pdf
```

### Cleaning Build Artifacts

```bash
make clean
```

## License

By contributing, you agree that your contributions will be licensed under the AGPL-3.0 License.

## Questions?

If you have questions, feel free to:

- Open a [GitHub Issue](https://github.com/ywatanabe1989/figrecipe/issues)
- Check existing issues and discussions

Thank you for contributing!

<!-- EOF -->
