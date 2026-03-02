# CLAUDE.md

This file provides guidance for AI assistants (Claude Code and similar tools) working in this repository. Keep it up to date as the project evolves.

## Project Overview

**Repository:** `alistairjosephdmonte-a11y/claudecode`

This repository is focused on accessibility (a11y) improvements and tooling for Claude Code. The goal is to ensure that Claude Code is usable and inclusive for developers with disabilities, covering areas such as screen reader support, keyboard navigation, color contrast, and ARIA compliance.

---

## Repository Structure

As the project grows, the expected structure is:

```
claudecode/
├── CLAUDE.md              # This file — AI assistant guidance
├── README.md              # Human-facing project overview
├── .github/
│   ├── workflows/         # CI/CD pipelines (GitHub Actions)
│   └── ISSUE_TEMPLATE/    # Standardized issue templates
├── src/                   # Primary source code
├── tests/                 # Unit and integration tests
├── docs/                  # Extended documentation
└── scripts/               # Utility and automation scripts
```

Update this section once the actual structure is established.

---

## Development Workflow

### Branching Strategy

- **Main branch:** `main` — stable, production-ready code only
- **Feature branches:** `feature/<short-description>`
- **Bug fixes:** `fix/<short-description>`
- **Claude AI branches:** Always prefixed with `claude/` (e.g., `claude/task-id-xyz`)

> **Important for AI agents:** All AI-generated changes must be developed and pushed to a `claude/`-prefixed branch. Never push directly to `main` without explicit user permission.

### Typical Development Flow

```bash
# 1. Create a feature branch
git checkout -b feature/my-feature

# 2. Make changes, commit incrementally
git add <specific-files>
git commit -m "feat: describe the change"

# 3. Push branch
git push -u origin feature/my-feature

# 4. Open a Pull Request for review
```

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `docs:` | Documentation only changes |
| `style:` | Formatting, no logic change |
| `refactor:` | Code restructuring without behavior change |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks, dependency updates |
| `a11y:` | Accessibility-specific improvements |

**Examples:**
```
feat: add keyboard navigation support to command palette
fix: correct contrast ratio on dark mode tooltips
a11y: add ARIA labels to icon-only buttons
docs: update CLAUDE.md with testing instructions
```

---

## Key Commands

> Update this section with actual commands once the tech stack is decided.

```bash
# Install dependencies (example — update for actual package manager)
npm install          # Node.js
# or
pip install -e .     # Python
# or
cargo build          # Rust

# Run tests
npm test
# or
pytest
# or
cargo test

# Lint and format
npm run lint
# or
ruff check . && ruff format .
# or
cargo clippy && cargo fmt

# Build
npm run build
# or
cargo build --release
```

---

## Code Conventions

### General

- Prefer small, focused functions over large monolithic ones
- Avoid premature abstraction — three similar lines is better than a poorly designed helper
- Do not add comments unless the logic is genuinely non-obvious
- Do not add error handling for impossible states
- Only validate at system boundaries (user input, external APIs)

### Accessibility (a11y) Standards

Since this project focuses on accessibility, adhere to these standards:

- **WCAG 2.1 AA** minimum; target **AAA** where feasible
- All interactive elements must be keyboard accessible
- Use semantic HTML where applicable
- Provide ARIA labels for icon-only or non-obvious controls
- Maintain a minimum **4.5:1 contrast ratio** for normal text; **3:1** for large text
- Support screen readers (test with NVDA, JAWS, VoiceOver)
- Avoid `aria-*` attributes that override native semantics unnecessarily
- Focus indicators must be visible and not suppressed with `outline: none` without a replacement

### Naming Conventions

- Files: `kebab-case` for most languages; follow language conventions (e.g., `snake_case.py` for Python)
- Variables/functions: follow the primary language's idioms (`camelCase` for JS/TS, `snake_case` for Python/Rust)
- Constants: `UPPER_SNAKE_CASE`
- Types/Classes: `PascalCase`

---

## Testing

- Write tests for all non-trivial logic
- Unit tests live alongside source code or in `tests/`
- Accessibility-specific tests should use automated a11y checkers (e.g., `axe-core`, `pa11y`) as a first pass — but automated checks catch only ~30% of issues; manual testing is required
- All tests must pass before merging to `main`

---

## Security

- Never commit secrets, tokens, or credentials
- Use environment variables for configuration (e.g., `.env` files, never committed)
- Add `.env` and similar files to `.gitignore` immediately
- Be cautious with `eval`, dynamic code execution, and shell injection vectors
- Validate and sanitize all external input

---

## AI Assistant Guidelines

When working in this repository as an AI assistant:

### Do
- Read files before modifying them
- Make minimal, targeted changes that directly address the task
- Stage specific files (`git add <file>`) rather than `git add .` to avoid accidentally committing secrets
- Commit changes with descriptive conventional commit messages
- Push to the designated `claude/` branch only
- Update this CLAUDE.md if you discover new conventions or structures

### Do Not
- Push to `main` without explicit user permission
- Create new files unless strictly necessary
- Add unrelated refactors, cleanups, or improvements alongside a focused task
- Add docstrings, comments, or type annotations to code you did not change
- Use force push (`--force`) without explicit instruction
- Skip pre-commit hooks (`--no-verify`) without explicit instruction
- Introduce over-engineered abstractions for single-use operations

### Git Operations for AI Agents

```bash
# Always specify branch explicitly when pushing
git push -u origin claude/<branch-name>

# If push fails due to network error, retry with backoff
# 2s → 4s → 8s → 16s (max 4 retries)

# Fetch a specific branch, not everything
git fetch origin <branch-name>
```

---

## Contributing

1. Open an issue describing the problem or feature before starting large changes
2. Keep PRs focused — one logical change per PR
3. Ensure all tests pass and no linting errors before requesting review
4. Add a test for every bug fix to prevent regressions
5. For accessibility changes, document what assistive technologies were tested

---

## Resources

- [WCAG 2.1 Guidelines](https://www.w3.org/TR/WCAG21/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Anthropic Claude Code Documentation](https://docs.anthropic.com/claude/docs/claude-code)
- [axe-core accessibility testing](https://github.com/dequelabs/axe-core)
- [pa11y CLI accessibility testing](https://github.com/pa11y/pa11y)
