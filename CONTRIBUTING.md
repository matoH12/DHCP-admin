# Contributing to DHCP Admin Panel

Thank you for your interest in contributing to DHCP Admin Panel! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitLab
2. **Clone your fork** locally
3. **Create a branch** for your changes
4. **Make your changes** and test them
5. **Submit a pull request**

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose (optional, but recommended)
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Using Docker (Recommended)

```bash
docker compose up -d
```

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear, descriptive title
- Steps to reproduce the problem
- Expected vs actual behavior
- Screenshots (if applicable)
- Environment details (OS, Docker version, etc.)

### Suggesting Features

Feature requests are welcome! Please provide:

- Clear description of the feature
- Use case and benefits
- Potential implementation approach (if you have ideas)
- Any relevant examples or mockups

### Code Contributions

1. **Find or create an issue** describing what you want to work on
2. **Comment on the issue** to let others know you're working on it
3. **Fork and create a branch** from `main`
4. **Write code** following our standards
5. **Write tests** for your changes
6. **Update documentation** as needed
7. **Submit a pull request**

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and return values
- Write **docstrings** for all public functions and classes
- Use **meaningful variable names**
- Keep functions **small and focused**

```python
def calculate_available_ips(network: str, cidr: int, exclude: List[str]) -> List[str]:
    """
    Calculate available IP addresses in a network range.

    Args:
        network: Network address (e.g., "192.168.1.0")
        cidr: CIDR notation (e.g., 24)
        exclude: List of IP addresses to exclude

    Returns:
        List of available IP addresses
    """
    # Implementation here
    pass
```

#### Code Quality Tools

```bash
# Format code
black app/

# Check style
flake8 app/

# Type checking
mypy app/

# Sort imports
isort app/
```

### TypeScript (Frontend)

- Use **TypeScript** for all new code
- Follow **React best practices**
- Use **functional components** with hooks
- Define **interfaces** for all props and data structures
- Use **meaningful component names**

```typescript
interface DeviceFormProps {
  device?: Device;
  onSubmit: (device: DeviceCreate) => Promise<void>;
  onCancel: () => void;
}

export function DeviceForm({ device, onSubmit, onCancel }: DeviceFormProps) {
  // Implementation here
}
```

#### Code Quality Tools

```bash
# Type check
npm run type-check

# Lint
npm run lint

# Format
npm run format
```

### General Guidelines

- **DRY (Don't Repeat Yourself)** - Extract common code into reusable functions
- **KISS (Keep It Simple, Stupid)** - Prefer simple solutions over complex ones
- **YAGNI (You Aren't Gonna Need It)** - Don't add functionality until needed
- **Write self-documenting code** - Code should be readable without extensive comments
- **Comment complex logic** - But prefer refactoring to make code clearer

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring (no functionality changes)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks, dependency updates

### Examples

```bash
feat(devices): add bulk import functionality

- Add CSV import endpoint
- Create import validation logic
- Add progress tracking

Closes #123
```

```bash
fix(dhcp): correct subnet mask calculation

The netmask was incorrectly calculated for CIDR values above 24.
Fixed by using proper bitwise operations.

Fixes #456
```

```bash
docs(readme): update installation instructions

- Add Docker installation steps
- Update environment variable examples
- Fix broken links
```

## Pull Request Process

1. **Update documentation** for any changed functionality
2. **Add tests** for new features
3. **Ensure all tests pass** locally
4. **Update CHANGELOG.md** with your changes
5. **Keep PRs focused** - one feature or fix per PR
6. **Write a clear description** of your changes

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review
- [ ] I have commented complex code
- [ ] I have updated documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests
- [ ] All tests pass locally
- [ ] I have updated CHANGELOG.md

## Screenshots (if applicable)
```

### Review Process

- All PRs require at least one review
- Address review comments promptly
- Be open to feedback and suggestions
- Maintainers may request changes or improvements

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_devices.py

# Run specific test
pytest tests/test_devices.py::test_create_device
```

### Writing Tests

- Write unit tests for all new functions
- Write integration tests for API endpoints
- Aim for >80% code coverage
- Use descriptive test names

```python
def test_create_device_with_valid_data():
    """Test creating a device with valid input data."""
    # Arrange
    device_data = {
        "hostname": "test-device",
        "mac_address": "00:11:22:33:44:55",
        "ip_address": "192.168.1.10"
    }

    # Act
    response = client.post("/api/v1/devices/", json=device_data)

    # Assert
    assert response.status_code == 200
    assert response.json()["hostname"] == "test-device"
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

## Documentation

### Code Documentation

- **Backend**: Use docstrings for all public functions and classes
- **Frontend**: Use JSDoc comments for complex functions
- **API**: Update OpenAPI schema when changing endpoints

### Documentation Files

Update relevant documentation when making changes:

- `README.md` - Overview and quick start
- `DEPLOYMENT.md` - Deployment instructions
- `SECURITY.md` - Security features and best practices
- `FLEXIBLE-DEPLOYMENT.md` - Various deployment scenarios
- `API.md` - API documentation (if not covered by OpenAPI)

### Writing Good Documentation

- Be clear and concise
- Include examples
- Keep it up to date
- Use proper formatting (headings, lists, code blocks)
- Add screenshots for UI changes

## Project Structure

Understanding the project structure helps with contributions:

```
dhcp-admin/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   ├── middleware/      # Security middleware
│   │   └── utils/           # Utility functions
│   ├── tests/               # Backend tests
│   └── alembic/             # Database migrations
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API calls
│   │   ├── types/           # TypeScript types
│   │   └── hooks/           # Custom hooks
│   └── tests/               # Frontend tests
├── scripts/                 # Deployment scripts
├── nginx/                   # Nginx configuration
└── docs/                    # Additional documentation
```

## Getting Help

- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitLab discussions for questions
- **Documentation**: Check the docs/ directory
- **Examples**: Look at existing code for patterns

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes for their contributions
- Project README (for significant contributions)

## License

By contributing to DHCP Admin Panel, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
