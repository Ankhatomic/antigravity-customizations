# 🚀 Antigravity Customizations

A curated collection of skills, prompts, and customizations for [Google Antigravity IDE](https://gemini.google.com).

---

## 📦 Available Skills

| Skill | Description |
|:---|:---|
| [`github-customizations-publisher`](./skills/github-customizations-publisher) | Publish, version, and sync Antigravity customizations (skills, prompts, rules, and workflows) to GitHub repositories so other users can disc... |
| [`skill-creator`](./skills/skill-creator) | Create new skills, modify and improve existing skills, and measure skill performance within the Antigravity IDE ecosystem. Activate this ski... |

## 🛠️ How to Install

### Option 1: Global Installation (Available across all projects)
Copy the desired skill into your global Antigravity configuration:
```bash
# Clone this repository
git clone https://github.com/<username>/antigravity-customizations.git /tmp/antigravity-customizations

# Install a specific skill (example: skill-creator)
mkdir -p ~/.gemini/config/skills
cp -r /tmp/antigravity-customizations/skills/<skill-name> ~/.gemini/config/skills/
```

### Option 2: Project-Only Installation (Workspace scope)
Copy into your project's `.agents/skills/` directory:
```bash
mkdir -p .agents/skills
cp -r /path/to/skill .agents/skills/<skill-name>
```

---

## 📄 License
This collection is open-sourced under the [MIT License](./LICENSE).
