# Contributing to CompliQ

Thank you for considering contributing to CompliQ! This guide explains the workflow.

## Branching Strategy

We use a simplified **GitHub Flow**:

| Branch | Purpose |
|--------|---------|
| `main` | Stable, production-ready code |
| `dev` | Integration branch — merge features here first |
| `feature/<name>` | New features (e.g. `feature/cross-encoder-reranker`) |
| `fix/<name>` | Bug fixes (e.g. `fix/faiss-index-loading`) |
| `chore/<name>` | Non-functional tasks (e.g. `chore/update-deps`) |

## Workflow

```bash
# 1. Always branch off dev
git checkout dev
git pull origin dev
git checkout -b feature/my-feature

# 2. Make your changes, commit often
git add .
git commit -m "feat: add cross-encoder reranking step"

# 3. Push and open a PR against dev (not main)
git push origin feature/my-feature
```

## Commit Message Convention (Conventional Commits)

```
<type>(<scope>): <short description>

Types: feat | fix | docs | style | refactor | test | chore
```

**Examples:**
- `feat(retriever): add cross-encoder reranking`
- `fix(pipeline): handle empty query edge case`
- `docs(readme): update setup instructions`
- `chore(deps): pin faiss-cpu to 1.8.0`

## Code Standards

- Python 3.10+
- All functions must have docstrings
- All `print()` in pipeline code must go to `sys.stderr`
- No hardcoded paths — use `pathlib.Path` and `argparse`
- No IS numbers in LLM output unless they appear in retrieved context

## Running Tests (Coming Soon)

```bash
pytest tests/ -v
```
