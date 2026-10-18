# nx-gir notes for Claude

## Code style

- Max line width is 60 characters in all code
  (Python, shell, config). The code is read on a phone.
- Configured in `pyproject.toml` (ruff) and
  `.editorconfig`.
- Before committing, run:

  ```sh
  ruff format scripts/
  ruff check scripts/
  ```

- `ruff format` cannot split long strings, comments or
  docstrings; shorten or wrap those by hand.
- Text files in `data/` are content, not code, and are
  exempt.
