# Contributing to WilcoSS Custody Manager

Thank you for your interest in contributing to the WilcoSS Custody & Equipment Manager project! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL 14+
- Git

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/custody-manager.git
cd custody-manager
```

2. **Set up the frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

3. **Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

4. **Set up the database**
```bash
createdb custody_manager
cd backend
alembic upgrade head
```

## Development Workflow

### Branching Strategy
- `main` - Production-ready code
- `feature/[feature-name]` - New features
- `fix/[bug-name]` - Bug fixes
- `docs/[doc-name]` - Documentation updates

### Making Changes

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

3. **Test your changes**
```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest
```

4. **Commit your changes**
```bash
git add .
git commit -m "Description of your changes"
```

Follow commit message conventions:
- `feat: Add new feature`
- `fix: Fix bug in component`
- `docs: Update documentation`
- `refactor: Refactor code`
- `test: Add tests`

5. **Push and create a Pull Request**
```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference to related issues (e.g., "Fixes #42")
- Screenshots (if UI changes)

## Code Style Guidelines

### Frontend (React/JavaScript)
- Use functional components with hooks
- Follow React best practices
- Use TailwindCSS utility classes
- Use meaningful component and variable names
- Format code with Prettier

### Backend (Python/FastAPI)
- Follow PEP 8 style guide
- Use type hints for function parameters and return values
- Write docstrings for functions and classes
- Format code with Black
- Lint with Ruff

### Example Code Style

**React Component:**
```jsx
import React from 'react';

export function KitCard({ kit, onCheckout }) {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-lg font-semibold">{kit.name}</h3>
      <button 
        onClick={() => onCheckout(kit.id)}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Check Out
      </button>
    </div>
  );
}
```

**FastAPI Endpoint:**
```python
from fastapi import APIRouter, Depends, HTTPException
from app.services.custody_service import CustodyService

router = APIRouter()

@router.post("/kits/{kit_id}/checkout")
async def checkout_kit(
    kit_id: str,
    user_id: str,
    service: CustodyService = Depends()
) -> dict:
    """
    Check out a kit to a user.
    
    Args:
        kit_id: The UUID of the kit
        user_id: The UUID of the user checking out the kit
        service: The custody service dependency
        
    Returns:
        The created custody event
    """
    try:
        event = await service.checkout_kit(kit_id, user_id)
        return event
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Testing Guidelines

### Frontend Testing
- Write unit tests for utility functions
- Write component tests for UI components
- Use vitest and React Testing Library

### Backend Testing
- Write unit tests for services
- Write integration tests for API endpoints
- Use pytest and fixtures
- Aim for >80% code coverage

### Example Test
```python
def test_checkout_kit_success(test_db, test_user, test_kit):
    """Test successful kit checkout"""
    service = CustodyService(test_db)
    event = service.checkout_kit(test_kit.id, test_user.id)
    
    assert event.event_type == "checkout_onprem"
    assert event.to_user_id == test_user.id
    assert test_kit.status == "checked_out"
```

## Database Migrations

When making database schema changes:

1. **Create a migration**
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

2. **Review the generated migration**
- Check the generated file in `alembic/versions/`
- Ensure it accurately reflects your changes

3. **Apply the migration**
```bash
alembic upgrade head
```

4. **Test rollback**
```bash
alembic downgrade -1
alembic upgrade head
```

## Pull Request Guidelines

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main

### PR Description Template
```markdown
## Description
Brief description of changes

## Related Issues
Fixes #[issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes
```

## Issue Reporting

### Bug Reports
Include:
- Clear title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots/error messages
- Environment (browser, OS, etc.)

### Feature Requests
Include:
- Clear description of the feature
- Use case/user story
- Proposed implementation (optional)

## Code Review Process

1. **Submit PR** - Create pull request with clear description
2. **Automated Checks** - CI/CD runs tests and linting
3. **Code Review** - Maintainer reviews code
4. **Address Feedback** - Make requested changes
5. **Approval** - PR approved by maintainer
6. **Merge** - PR merged to main branch

## Questions or Need Help?

- Check existing issues and documentation
- Create a new issue with the "question" label
- Reach out to project maintainers

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to WilcoSS Custody Manager! 🎯