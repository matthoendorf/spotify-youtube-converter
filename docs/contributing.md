# Contributing Guide

Thank you for your interest in contributing to the Spotify to YouTube Music Converter! This guide will help you get started with contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Areas for Contribution](#areas-for-contribution)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project follows a simple code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Keep discussions relevant to the project

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- GitHub account
- Basic knowledge of Python and Streamlit

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/spotify-youtube-converter.git
   cd spotify-youtube-converter
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/matthoendorf/spotify-youtube-converter.git
   ```

## Development Setup

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --dev

# Install pre-commit hooks
uv run pre-commit install
```

### Using pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Environment Setup

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Set up API credentials** (see setup guides in `docs/`)
3. **Test the setup**:
   ```bash
   streamlit run streamlit_app.py
   ```

## Making Changes

### Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the style guidelines

3. **Test your changes** thoroughly

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Guidelines

Use clear, descriptive commit messages:

- **Add**: New features or functionality
- **Fix**: Bug fixes
- **Update**: Changes to existing features
- **Refactor**: Code improvements without functionality changes
- **Docs**: Documentation changes
- **Test**: Adding or updating tests

Examples:
```
Add: Apple Music integration support
Fix: YouTube thumbnail caching issue
Update: Improve matching algorithm accuracy
Docs: Add deployment guide for Railway
```

## Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=services --cov=utils --cov=config

# Run specific test file
uv run pytest tests/test_spotify.py

# Run with verbose output
uv run pytest -v
```

### Writing Tests

- Add tests for new functionality
- Use descriptive test names
- Test both success and error cases
- Mock external API calls

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch
from services.spotify import SpotifyService

class TestSpotifyService:
    def test_get_playlist_info_success(self):
        # Test successful playlist info retrieval
        pass
    
    def test_get_playlist_info_invalid_url(self):
        # Test error handling for invalid URLs
        pass
```

### Manual Testing

Before submitting:

1. **Test the UI** - Ensure all features work in the Streamlit app
2. **Test API integrations** - Verify Spotify and YouTube APIs work
3. **Test error handling** - Try invalid inputs and edge cases
4. **Test different browsers** - Ensure compatibility

## Submitting Changes

### Pull Request Process

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Push your changes**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Explain what changes you made and why
   - Reference any related issues
   - Include screenshots for UI changes

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Manual testing completed
- [ ] New tests added (if applicable)

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## Areas for Contribution

### High Priority

1. **Additional Music Services**
   - Apple Music integration
   - Deezer support
   - Tidal integration
   - SoundCloud support

2. **Enhanced Matching**
   - Improve track matching algorithms
   - Add fuzzy string matching
   - Support for remixes and covers
   - Duration-based matching

3. **Performance Improvements**
   - Optimize API calls
   - Implement better caching
   - Reduce memory usage
   - Faster search algorithms

### Medium Priority

4. **UI/UX Improvements**
   - Better responsive design
   - Dark mode support
   - Improved error messages
   - Progress indicators

5. **Export Features**
   - Additional export formats (JSON, XML)
   - Playlist metadata export
   - Batch processing
   - Scheduled exports

6. **Analytics and Monitoring**
   - Usage analytics
   - Performance monitoring
   - Error tracking
   - API quota monitoring

### Low Priority

7. **Advanced Features**
   - User accounts and saved playlists
   - Playlist collaboration
   - Music recommendations
   - Social sharing features

## Style Guidelines

### Python Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Code Formatting

```bash
# Format code with Black
uv run black .

# Sort imports with isort
uv run isort .

# Check linting with flake8
uv run flake8

# Type checking with mypy
uv run mypy services/ utils/ config/
```

### Code Standards

1. **Type Hints**: Use type hints for all functions
   ```python
   def process_playlist(url: str) -> pd.DataFrame:
       pass
   ```

2. **Docstrings**: Document all public functions
   ```python
   def extract_playlist_data(url: str) -> pd.DataFrame:
       """Extract track data from a Spotify playlist.
       
       Args:
           url: Spotify playlist URL
           
       Returns:
           DataFrame with track information
           
       Raises:
           ValueError: If URL is invalid
       """
   ```

3. **Error Handling**: Use appropriate exception handling
   ```python
   try:
       result = api_call()
   except APIError as e:
       logger.error(f"API call failed: {e}")
       raise
   ```

4. **Logging**: Use structured logging
   ```python
   import logging
   
   logger = logging.getLogger(__name__)
   logger.info("Processing playlist", extra={"url": url})
   ```

### Streamlit Guidelines

1. **Session State**: Use session state for data persistence
2. **Caching**: Use `@st.cache_data` for expensive operations
3. **Error Handling**: Show user-friendly error messages
4. **Performance**: Minimize API calls and processing

## Documentation

### Updating Documentation

- Update README.md for major changes
- Add docstrings for new functions
- Update setup guides for new features
- Add examples for new functionality

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up to date

## Getting Help

### Resources

- **Project Documentation**: Check the `docs/` folder
- **GitHub Issues**: Search existing issues first
- **GitHub Discussions**: For questions and ideas

### Asking Questions

When asking for help:

1. **Search existing issues** first
2. **Provide context** about what you're trying to do
3. **Include error messages** and relevant code
4. **Describe what you've already tried**

### Reporting Bugs

When reporting bugs:

1. **Use the bug report template**
2. **Include steps to reproduce**
3. **Provide error messages and logs**
4. **Include environment information**

## Recognition

Contributors will be recognized in:

- README.md acknowledgments
- Release notes for significant contributions
- GitHub contributor statistics

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (GPL-3.0-or-later).

## Thank You!

Thank you for contributing to the Spotify to YouTube Music Converter! Your contributions help make this tool better for everyone.
