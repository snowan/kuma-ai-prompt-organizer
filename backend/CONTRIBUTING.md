# Contributing to AI Prompt Manager

First off, thanks for taking the time to contribute! :tada: :+1:

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/your-username/ai-prompt-manager/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/your-username/ai-prompt-manager/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior.

### Suggesting Enhancements
- Open a new issue with a clear title and provide as much detail as possible about the feature/enhancement.
- Include step-by-step descriptions with specific examples of the suggested enhancement.

### Your First Code Contribution
1. **Fork** the repository on GitHub.
2. **Clone** the project to your own machine.
3. **Commit** changes to your own branch.
4. **Push** your work back up to your fork.
5. Submit a **Pull Request** so that we can review your changes.

## Development Setup

### Prerequisites
- Python 3.8+
- pip
- Git

### Setup
1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file as needed
   ```
5. Initialize the database:
   ```bash
   python init_db.py
   ```

## Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Use [Black](https://black.readthedocs.io/) for code formatting.
- Use [isort](https://pycqa.github.io/isort/) for import sorting.
- Run `make format` to automatically format your code.

## Testing
- Write tests for new features and bug fixes.
- Run tests with `make test`.
- Ensure all tests pass before submitting a pull request.
- Aim for good test coverage (use `make test-cov` to check).

## Pull Request Process
1. Update the README.md with details of changes if needed.
2. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
3. Update the CHANGELOG.md with details of changes to the interface.
4. Your pull request should be linked to an issue if one exists.
5. Ensure all tests pass and there are no merge conflicts.
6. Request review from one of the maintainers.

## Code Review Process
- All pull requests require at least one approving review before being merged.
- A maintainer will review your pull request and provide feedback.
- Once approved, your pull request will be merged by a maintainer.

## License
By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## Questions?
If you have any questions, feel free to open an issue or contact the maintainers.
