# Contributing to OMK Hive

Thank you for your interest in contributing to OMK Hive! This document provides guidelines and instructions for contributing.

## 🤝 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/omakh-Hive.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Run tests: `make test`
6. Commit: `git commit -m 'feat: add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Development Workflow

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build/config changes

**Examples:**
```
feat: add Gemini provider to LLM abstraction layer
fix: resolve memory leak in Queen AI orchestrator
docs: update API documentation for bee endpoints
```

## 💻 Code Style

### TypeScript/JavaScript
- Use Prettier for formatting
- Follow ESLint rules
- Use 2-space indentation
- Use single quotes
- Add JSDoc comments for public APIs

### Python
- Use Black for formatting
- Follow PEP 8
- Use 4-space indentation
- Type hints required
- Add docstrings for all functions

### Solidity
- Follow [Solidity Style Guide](https://docs.soliditylang.org/en/latest/style-guide.html)
- Use 4-space indentation
- Document all functions with NatSpec
- Use explicit visibility modifiers

## 🧪 Testing Requirements

### Required Tests
- **Unit Tests**: Required for all new features
- **Integration Tests**: Required for API endpoints
- **E2E Tests**: Required for critical user flows
- **Coverage**: Maintain >80% coverage

### Running Tests
```bash
# All tests
make test

# Specific component
make test-contracts
make test-backend
make test-frontend
make test-queen
```

## 🔍 Pull Request Process

1. **Update Documentation**
   - Update README if adding features
   - Update API docs for new endpoints
   - Add inline code comments

2. **Add Tests**
   - Write unit tests for new functions
   - Add integration tests for new endpoints
   - Ensure all tests pass

3. **Update CHANGELOG.md**
   - Add entry under `[Unreleased]`
   - Follow Keep a Changelog format

4. **Request Review**
   - Request review from 2+ team members
   - Address all review comments
   - Ensure CI passes

5. **Squash and Merge**
   - Squash commits before merge
   - Use descriptive merge commit message

## ✅ Code Review Checklist

Before submitting, ensure:

- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No sensitive data exposed
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Backward compatibility maintained
- [ ] Error handling implemented
- [ ] Logging added where appropriate
- [ ] Code is self-documenting

## 🔐 Security

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Report security vulnerabilities privately
- Follow secure coding practices

## 📝 Documentation

- Keep README up to date
- Document all public APIs
- Add inline comments for complex logic
- Update architecture docs for major changes

## 🐛 Bug Reports

When filing a bug report, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Node version, etc.
6. **Logs**: Relevant error logs
7. **Screenshots**: If applicable

## 💡 Feature Requests

When proposing a feature:

1. **Problem**: What problem does it solve?
2. **Solution**: Proposed solution
3. **Alternatives**: Alternative solutions considered
4. **Impact**: Impact on existing features
5. **Implementation**: High-level implementation approach

## 🏗️ Project Structure

Familiarize yourself with:
- [Architecture Overview](architecture/README.md)
- [Smart Contracts](architecture/contracts.md)
- [Queen AI System](architecture/queen-ai.md)
- [API Documentation](api/README.md)

## 🤔 Questions?

- Open an issue for general questions
- Join our Discord for real-time chat
- Email: dev@omkhive.io

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to OMK Hive! 🐝
