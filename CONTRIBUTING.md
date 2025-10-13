# Contributing to OMK Hive AI 🐝

Thank you for your interest in contributing to OMK Hive! This document provides guidelines and instructions for contributing to the project.

## 🎯 Development Philosophy

**We follow a holistic, big-picture approach:**
1. **Understand the system** before making changes
2. **Map interconnected components** to see how changes affect the whole
3. **Fix root causes**, not symptoms
4. **Test thoroughly** before committing

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/omakh-Hive.git
cd omakh-Hive
git remote add upstream https://github.com/mromk94/omakh-Hive.git
```

### 2. Set Up Development Environment

**Backend:**
```bash
cd backend/queen-ai
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure .env with your API keys
python3 main.py
```

**Frontend:**
```bash
cd omk-frontend
npm install
npm run dev
```

**Smart Contracts (optional):**
```bash
cd contracts/ethereum
npm install
npx hardhat compile
```

## 📝 Code Style

### Python (Backend)
- **Style**: Follow PEP 8
- **Formatting**: Use `black` for consistent formatting
- **Linting**: Use `flake8` and `pylint`
- **Type Hints**: Use type hints where possible
- **Docstrings**: Required for all public functions/classes

```bash
# Format code
black app/

# Lint
flake8 app/ --max-line-length=120
pylint app/
```

### TypeScript/JavaScript (Frontend)
- **Style**: Follow Airbnb style guide
- **Formatting**: Prettier (configured)
- **Linting**: ESLint (configured)
- **Components**: Use functional components with hooks

```bash
# Format and lint
npm run lint
npm run format
```

### Solidity (Smart Contracts)
- **Style**: Follow Solidity style guide
- **Version**: ^0.8.20
- **Testing**: Hardhat + Chai
- **Security**: Use OpenZeppelin contracts

## 🌳 Branch Strategy

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/updates

### Workflow
1. Create a feature branch from `main`
2. Make your changes
3. Test thoroughly
4. Commit with meaningful messages
5. Push and create a Pull Request

## 💬 Commit Messages

Follow conventional commits:

```
type(scope): brief description

Detailed explanation (optional)

Fixes #issue_number (if applicable)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(bees): add liquidity monitoring bee

fix(websocket): resolve connection timeout in Cloud Run

docs(readme): update deployment instructions

refactor(orchestrator): extract initialization logic
```

## 🧪 Testing

### Backend Tests
```bash
cd backend/queen-ai
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd omk-frontend
npm test
npm run test:e2e  # End-to-end tests
```

### Contract Tests
```bash
cd contracts/ethereum
npx hardhat test
npx hardhat coverage
```

**Required:**
- All new features must include tests
- Maintain or improve code coverage
- All tests must pass before PR

## 🔍 Code Review Process

1. **Self-Review**: Review your own changes first
2. **Description**: Provide clear PR description
3. **Screenshots**: Include UI changes screenshots
4. **Tests**: Ensure all tests pass
5. **Documentation**: Update relevant docs
6. **CI/CD**: Ensure builds pass

### PR Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests added for new features
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No merge conflicts
- [ ] PR description is clear

## 🐛 Reporting Bugs

### Before Reporting
1. Search existing issues
2. Try to reproduce consistently
3. Test with latest version

### Bug Report Should Include
- **Description**: Clear bug description
- **Steps to Reproduce**: Numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python/Node version, etc.
- **Logs**: Relevant error messages
- **Screenshots**: If applicable

## 💡 Feature Requests

### Proposal Format
1. **Problem Statement**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Impact**: Who benefits? How?
5. **Implementation**: High-level technical approach

## 🏗️ Architecture Guidelines

### Adding a New Bee Agent
1. Inherit from `BaseBee` in `app/bees/base.py`
2. Implement `execute()` method
3. Add to `BeeManager` in `app/bees/manager.py`
4. Register with message bus
5. Add tests
6. Update documentation

Example:
```python
from app.bees.base import BaseBee

class MyNewBee(BaseBee):
    """Description of what this bee does"""
    
    def __init__(self, bee_id: int):
        super().__init__(bee_id=bee_id, name="MyNewBee")
    
    async def execute(self, task_data: Dict) -> Dict:
        """Execute bee-specific task"""
        # Implementation
        return {"success": True, "result": data}
```

### Adding API Endpoints
1. Create route in `app/api/v1/`
2. Use proper HTTP methods
3. Add request/response models
4. Include authentication if needed
5. Add tests
6. Update API documentation

### Frontend Components
1. Create in `omk-frontend/components/`
2. Use TypeScript
3. Follow existing patterns
4. Make responsive
5. Add to Storybook (if applicable)
6. Test on multiple browsers

## 🚢 Deployment

### Backend (Google Cloud Run)
```bash
cd backend/queen-ai
gcloud builds submit --tag=gcr.io/omk-hive/omk-queen-ai
gcloud run deploy omk-queen-ai \
  --image gcr.io/omk-hive/omk-queen-ai \
  --region us-central1 \
  --platform managed
```

### Frontend (Netlify)
- Automatic deployment via GitHub integration
- Preview deployments for PRs
- Manual: `npm run build` then deploy `dist/`

## 📚 Documentation

### When to Update Docs
- New features added
- API changes
- Configuration changes
- Deployment process changes
- Architecture modifications

### Documentation Locations
- **README.md**: Overview and quick start
- **CONTRIBUTING.md**: This file
- **Code comments**: Complex logic explanations
- **API docs**: FastAPI auto-generated
- **Architecture docs**: System design

## 🔒 Security

### Reporting Security Issues
**DO NOT** create public issues for security vulnerabilities.

Email: security@omakhive.io (or contact maintainers privately)

### Security Checklist
- [ ] No hardcoded secrets/keys
- [ ] Use environment variables
- [ ] Validate all inputs
- [ ] Use parameterized queries
- [ ] Implement rate limiting
- [ ] Follow OWASP guidelines

## 🎓 Learning Resources

### For Backend Development
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Async Programming](https://realpython.com/async-io-python/)
- [Google Gemini API](https://ai.google.dev/docs)

### For Frontend Development
- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks](https://react.dev/reference/react)
- [TailwindCSS](https://tailwindcss.com/docs)

### For Smart Contracts
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Hardhat](https://hardhat.org/docs)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts/)

## 💬 Communication

### Channels
- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code review, technical discussion

### Response Times
- Issues: 24-48 hours
- PRs: 48-72 hours
- Security: 24 hours

## 🎖️ Recognition

Contributors will be:
- Added to CONTRIBUTORS.md
- Credited in release notes
- Mentioned in announcements (with permission)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Check existing [issues](https://github.com/mromk94/omakh-Hive/issues)
- Start a [discussion](https://github.com/mromk94/omakh-Hive/discussions)
- Review [documentation](./README.md)

---

**Thank you for contributing to OMK Hive! 🐝💛**
