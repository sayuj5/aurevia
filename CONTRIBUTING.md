# Contributing to Aurevia

Thank you for your interest in contributing to Aurevia! 

## Development Workflow

1. **Fork and Clone**: Fork the repository and clone it locally.
2. **Setup**: Follow the installation instructions in the `README.md` to set up the frontend, backend, and AI service.
3. **Branch**: Create a new branch for your feature or bug fix.
4. **Develop**: Write your code, adhering to our code quality standards.
5. **Test**: Run the test suites for the respective services.
6. **Submit**: Open a Pull Request against the `develop` branch.

## Branching Strategy
We use a standard feature-branch workflow:
- `main` / `master`: Stable release branch.
- `develop`: Integration branch for active development.
- `feature/<name>`: New features.
- `bugfix/<name>`: Bug fixes.
- `docs/<name>`: Documentation updates.

## Pull Requests
- Base your PR against the `develop` branch.
- Keep PRs focused on a single feature or fix.
- Provide a clear description of the changes.
- Ensure all tests pass before requesting a review.

## Commit Conventions
Please write clear, concise commit messages. While we don't strictly enforce a format, prefixing with the area (e.g., `frontend:`, `backend:`, `ai:`, `docs:`) is highly encouraged.

## Code Quality
- **Frontend**: Run `npm run lint` (uses Oxlint).
- **Backend/AI**: Follow PEP 8 guidelines. Use type hints where appropriate.

## Testing Expectations
- Write tests for new features.
- For the backend, use `pytest` (e.g., `pytest app/tests -v`). Tests run against an isolated in-memory DB and mock external calls.
- Do not introduce regressions.

## Documentation Expectations
Update `README.md` and related documentation files if you change core architecture, add dependencies, or modify setup instructions.

## Security Expectations
Do not commit secrets, API keys, or `.env` files. Ensure any new dependencies do not introduce known security vulnerabilities.
