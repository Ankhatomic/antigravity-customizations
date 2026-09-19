---
name: git-commit-formatter
description: >-
  Format Git commit messages following the Conventional Commits specification.
  Use this skill when the user asks to write, review, or format a commit
  message, or when they say things like "help me commit this", "what should I
  write for the commit", or "review my git history". Activate whenever changes
  are being staged or committed, even if "commit message" isn't mentioned
  explicitly.
---

# Git Commit Formatter

Format staged changes into a Conventional Commits–compliant message.

## Commit Format

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

## Types

| Type | When to use |
|:-----|:------------|
| `feat` | New feature for the user |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change that isn't a fix or feature |
| `test` | Adding or fixing tests |
| `chore` | Build process, tooling, config |
| `perf` | Performance improvement |

## Steps

1. Run `git diff --staged` to understand what changed
2. Identify the primary type and optional scope
3. Write the short description (max 72 chars, imperative mood, no period)
4. Add a body paragraph if the change needs context (wrap at 72 chars)
5. Add `BREAKING CHANGE:` footer if applicable
6. Present the final commit message to the user for confirmation

## Output Format

Present the message in a code block:

```
feat(auth): implement JWT-based session refresh

Replace the previous cookie-based session with JWT tokens, reducing
server-side session storage requirements and enabling stateless scaling.

BREAKING CHANGE: Clients must send Authorization header; cookie auth removed.
```

## Verification

After the user confirms, offer to run:
```bash
git commit -m "<type>(<scope>): <short>" -m "<body>"
```

Or write to a temp file and use `git commit -F`.
