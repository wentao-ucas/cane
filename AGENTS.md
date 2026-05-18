# Safety Rules For This Repo

## Destructive operations require explicit confirmation
- Never run destructive commands without user confirmation.
- Destructive commands include (but are not limited to):
  - `git clean`, `git reset --hard`, `git checkout --`, `git restore --source ...`
  - `rm`, `del`, `Remove-Item`, `rmdir`, recursive delete operations
  - Any command that overwrites or truncates existing files

## Required workflow before deletion
1. Show a dry-run / preview list first (for example `git clean -nd`).
2. Explain exactly what will be deleted or overwritten.
3. Wait for an explicit user reply: `确认删除`.
4. Only then execute the destructive command.

## If confirmation is missing
- Stop and ask for confirmation.
- Prefer non-destructive alternatives.
