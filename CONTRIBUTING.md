# Contributing to Explaino RAG

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

**Before submitting a bug report**:

- Check existing issues to avoid duplicates
- Verify the bug with the latest version
- Collect relevant information (logs, config, steps to reproduce)

**Bug Report Template**:

```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:

1. Step one
2. Step two
3. ...

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:

- OS: [e.g., macOS 13.0, Ubuntu 22.04]
- Python version: [e.g., 3.9.7]
- Docker version: [e.g., 24.0.0]
- Installation method: [Docker / Local]

**Logs**:
```

Paste relevant logs here

```

**Additional Context**: Any other relevant information
```

### Suggesting Features

**Feature Request Template**:

```markdown
**Feature Description**: Clear description of the feature

**Use Case**: Why is this feature needed?

**Proposed Solution**: How should it work?

**Alternatives Considered**: Other approaches you've thought about

**Additional Context**: Mockups, examples, references
```

### Pull Requests

**Before submitting a PR**:

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Follow code style guidelines

**PR Template**:

```markdown
**Description**: What does this PR do?

**Related Issue**: Fixes #123

**Type of Change**:

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Testing**:

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

**Checklist**:

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
```

## Development Setup

### Local Development

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/Explaino_RAG_AIFounding.git
cd Explaino_RAG_AIFounding

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# 5. Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# 6. Start OpenSearch
docker run -d -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  --name opensearch \
  opensearchproject/opensearch:2.11.1

# 7. Configure environment
cp .env.example .env
# Edit .env with your settings

# 8. Run tests
pytest
```

### Docker Development

```bash
# Build development image
docker build -t explaino-rag:dev .

# Run with docker-compose
docker-compose up -d

# Access container
docker-compose exec rag-backend bash

# Run tests in container
docker-compose exec rag-backend pytest
```

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

```python
# Line length: 100 characters (not 79)
# Use Black for formatting
# Use type hints for function signatures

# Good
def process_query(query: str, max_results: int = 5) -> List[Result]:
    """Process a user query and return results.

    Args:
        query: User's question
        max_results: Maximum number of results to return

    Returns:
        List of Result objects
    """
    # Implementation
    pass

# Bad
def process_query(query, max_results=5):
    # No docstring, no type hints
    pass
```

### Formatting Tools

```bash
# Format code with Black
black src/ tests/

# Check style with flake8
flake8 src/ tests/ --max-line-length=100

# Type checking with mypy
mypy src/
```

### Docstring Style

Use **Google-style docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed. Can span multiple lines
    and include examples.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Testing Guidelines

### Writing Tests

```python
# tests/test_example.py
import pytest
from src.module import function_to_test

class TestExample:
    """Test suite for example functionality."""

    def test_basic_functionality(self):
        """Test basic use case."""
        result = function_to_test("input")
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling."""
        with pytest.raises(ValueError):
            function_to_test("")

    @pytest.mark.parametrize("input,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_multiple_inputs(self, input, expected):
        """Test with multiple inputs."""
        assert function_to_test(input) == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chunking.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_chunking.py::TestChunking::test_pdf_chunking
```

### Test Coverage

- Aim for **>80% code coverage**
- All new features must include tests
- Bug fixes should include regression tests

## Documentation Guidelines

### Code Documentation

- All public functions/classes must have docstrings
- Complex algorithms should have inline comments
- Use type hints for all function signatures

### README Updates

When adding features, update:

- Feature list
- Usage examples
- Configuration options
- Troubleshooting section (if applicable)

### Architecture Documentation

For significant changes, update `ARCHITECTURE.md`:

- Component diagrams
- Data flow descriptions
- Design decisions

## Commit Message Guidelines

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process, dependencies

**Examples**:

```bash
feat(retrieval): add hybrid search for PDFs

Implements BM25 + k-NN hybrid search to improve PDF retrieval accuracy.
Adds configurable boost weights for keyword vs semantic search.

Closes #42

---

fix(indexing): handle empty PDF pages gracefully

Previously crashed when encountering empty pages. Now logs warning
and continues processing.

Fixes #38

---

docs(readme): add troubleshooting section

Adds common issues and solutions based on user feedback.
```

## Release Process

### Version Numbering

We use **Semantic Versioning** (SemVer):

- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

### Creating a Release

1. Update version in `setup.py` (if exists)
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v1.2.3 -m "Release v1.2.3"`
4. Push tag: `git push origin v1.2.3`
5. Create GitHub release with notes

## Getting Help

- **Questions**: Use [GitHub Discussions](https://github.com/ziadalyH/Explaino_RAG_AIFounding/discussions)
- **Bugs**: Open an [Issue](https://github.com/ziadalyH/Explaino_RAG_AIFounding/issues)
- **Chat**: Join our community (link TBD)

## Recognition

Contributors will be:

- Listed in `CONTRIBUTORS.md`
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🙏
