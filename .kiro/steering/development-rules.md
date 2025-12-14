---
inclusion: always
---

# Development Rules and Guidelines

## Git Commands - IMPORTANT RESTRICTIONS

### ❌ NEVER use these interactive commands:
- `git log --oneline` (opens pager, requires manual exit)
- `git log` without limits
- `less`, `more`, `cat` for large files
- `vim`, `nano`, or any interactive editors
- `git rebase -i` (interactive rebase)

### ✅ USE these alternatives instead:
- `git log --oneline -n 5` (limit to 5 lines)
- `git log --oneline --no-pager -10` (no pager, limit lines)
- `git show --name-only HEAD` (show last commit)
- `git status --porcelain` (machine-readable status)
- `git diff --name-only` (just file names)

### 🚫 CRITICAL: Git Commit Policy
- **NEVER make git commits unless explicitly requested**
- Only use `git add` and `git commit` when user specifically asks for it
- Do not automatically commit changes after completing tasks
- User must explicitly say "commit", "make commit", "git commit" or similar
- Always ask for commit message if not provided

## Command Guidelines

### File Operations
- Always use `readFile`, `readMultipleFiles` instead of `cat`
- Use `listDirectory` instead of `ls -la`
- Use `grepSearch` instead of `grep` commands
- Use `fileSearch` for finding files

### Process Management
- Use `controlBashProcess` for long-running commands (servers, watchers)
- Never use `cd` in bash commands - use `path` parameter instead
- Avoid command chaining (`&&`, `||`, `;`) - use multiple tool calls

### Docker & Development
- Always check if containers are running before starting new ones
- Use `make` commands when available instead of direct docker commands
- Prefer local development over Docker when possible for faster iteration

## Project-Specific Rules

### Translation Workflow
1. Use `make translations` for updating all translations
2. Use `make fix-english` for English translation issues
3. Use `make translations-test` for quality checks
4. Always compile translations after changes

### Code Changes
1. Check diagnostics with `getDiagnostics` after code changes
2. Test locally before Docker builds
3. Use structured commits with clear messages
4. Squash related commits when requested

### File Structure
- Keep dev_tools organized by category
- Document all new scripts in README files
- Use consistent naming conventions
- Exclude dev_tools from Docker builds

## Communication Style
- Be concise and direct
- Focus on actionable solutions
- Explain reasoning briefly
- Avoid verbose summaries unless requested
- Use bullet points for clarity

## Error Handling
- Always check command exit codes
- Provide alternative solutions when commands fail
- Explain what went wrong and why
- Suggest preventive measures

## Performance Guidelines
- Limit output of potentially large commands
- Use specific file paths instead of wildcards when possible
- Avoid recursive operations on large directories
- Check file sizes before reading large files