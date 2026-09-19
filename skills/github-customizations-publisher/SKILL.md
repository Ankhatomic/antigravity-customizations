---
name: github-customizations-publisher
description: >-
  Publish, version, and sync Antigravity customizations (skills, prompts, rules,
  and workflows) to GitHub repositories so other users can discover and install
  them. Use this skill whenever the user wants to publish or push their skills,
  prompts, or rules to GitHub, share their customizations with the community, or
  sync their repository. Activate on requests like "Quero subir essa skill para o
  GitHub", "Publique meu prompt no meu repositório", "Como compartilho essa
  customização com outros usuários?", "Atualize meu repositório de skills",
  "share this skill on github", or any variation of uploading customizations to
  Git, even if the user is a first-time Git contributor.
---

# GitHub Customizations Publisher

Guide and automate the publishing of Antigravity customizations (skills, prompts,
rules) to a central or dedicated GitHub repository for public or team sharing.

This skill is designed to be beginner-friendly: it ensures Git is properly
configured, sanitizes local private machine paths, automatically generates
community-ready installation instructions in `README.md`, and guides the commit
and push workflow.

---

## Repository Architecture

The publisher maintains a clean, modular repository structure so community
members can easily browse and install customizations:

```
antigravity-customizations/        ← Root repository folder
├── README.md                      ← Catalog of skills/prompts + install guide
├── LICENSE                        ← Open-source license (e.g. MIT)
├── skills/                        ← Published skills
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── prompts/                       ← Reusable prompts and instructions (.md)
│   └── <prompt-name>.md
└── rules/                         ← Workspace or global rules
    └── <rule-name>.md
```

Default local repository directory: `~/antigravity-customizations`

---

## Publishing Workflow

```
[1. Pre-Flight Check] ──> [2. Sanitize & Export] ──> [3. Generate README] ──> [4. Commit & Push]
   (Git user/email)         (Strip local paths)       (Catalog & install)       (Sync to GitHub)
```

---

## Step 1: Pre-Flight Check (Git Identity & Setup)

Before publishing, verify if Git identity is configured:

```bash
git config --global user.name
git config --global user.email
```

1. **If missing:** Ask the user for their name/handle and public email (or GitHub
   noreply email), and run:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```
2. **Repository initialization:** Check if `~/antigravity-customizations` exists.
   If not, initialize it:
   ```bash
   mkdir -p ~/antigravity-customizations/{skills,prompts,rules}
   cd ~/antigravity-customizations && git init -b main
   ```

---

## Step 2: Sanitize and Export Customization

When publishing a skill or file, ensure it does not leak private user paths or
environment-specific secrets.

Use the bundled export helper:
```bash
python3 ~/.gemini/config/skills/github-customizations-publisher/scripts/sanitize_and_export.py \
  --source "<path-to-skill-or-file>" \
  --type "skill" \
  --dest-repo ~/antigravity-customizations
```

*(Options for `--type`: `skill`, `prompt`, `rule`)*

**Sanitization rules applied:**
- Replace local absolute home paths (e.g. `/home/username/`) with portable
  generic references (`~/.gemini/config/...` or relative paths).
- Check that no API keys, tokens, or sensitive credentials exist in the exported files.
- Preserve folder hierarchy (`scripts/`, `references/`, `examples/`).

---

## Step 3: Update Catalog & Community Documentation

Keep the repository's `README.md` updated as a catalog.

Every published item must include:
1. **Name and description**
2. **One-line installation guide** for Antigravity users:
   ```bash
   # How community users install this skill globally:
   git clone <repo-url> /tmp/repo && cp -r /tmp/repo/skills/<skill-name> ~/.gemini/config/skills/
   ```
   Or for workspace installation:
   ```bash
   cp -r skills/<skill-name> .agents/skills/
   ```

3. Ensure a `LICENSE` file exists (default: MIT License unless specified).

---

## Step 4: Commit and Push to GitHub

1. Stage all changes:
   ```bash
   cd ~/antigravity-customizations
   git add .
   git status
   ```

2. Generate a clear Conventional Commit message:
   - Adding a new skill: `feat(skills): add <skill-name> skill`
   - Updating a skill: `fix(skills): improve <skill-name> trigger description`
   - Adding a prompt: `feat(prompts): add <prompt-name>`

   ```bash
   git commit -m "feat(skills): add <skill-name> skill"
   ```

3. **Remote Configuration (First time only):**
   Check if a remote repository is configured:
   ```bash
   git remote -v
   ```
   - **If no remote exists:**
     Explain in plain language how to create the repository on GitHub:
     1. Go to [github.com/new](https://github.com/new)
     2. Name it `antigravity-customizations` (Public)
     3. Do NOT initialize with README (already created locally)
     4. Copy the repository URL (e.g., `https://github.com/<username>/antigravity-customizations.git`)
     5. Link and push:
        ```bash
        git remote add origin <repository-url>
        git push -u origin main
        ```

   - **If remote already exists:**
     ```bash
     git push origin main
     ```

---

## Step 5: Verification & Confirmation

1. Confirm `git status` is clean.
2. Provide the user with:
   - Direct link to their GitHub repository and the new skill folder.
   - The exact snippet that other users can run to install their skill.
   - Congratulations on their contribution!

---

## Troubleshooting & Common Pitfalls

- **Authentication Error on `git push`:**
  GitHub no longer accepts account passwords for Git operations. Users must use a
  **Personal Access Token (classic or fine-grained)** with `repo` scope, or an
  **SSH key**. If an authentication error occurs, guide the user warmly to create a
  token at `github.com/settings/tokens` with step-by-step instructions.
- **Large Files:**
  Never commit `.db`, `.wal`, or large binaries. Ensure `.gitignore` ignores
  workspace cache and temporary run logs.
