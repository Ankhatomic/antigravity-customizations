#!/usr/bin/env python3
"""
sanitize_and_export.py — Export and sanitize Antigravity customizations for GitHub

Copies skills, prompts, or rules into a publication repository, sanitizing
machine-specific user paths (e.g. /home/<user>/) and generating catalog entries in README.md.

Usage:
  python3 sanitize_and_export.py --source <path> --type {skill,prompt,rule} --dest-repo <path>
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path

DEFAULT_LICENSE = """MIT License

Copyright (c) {year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def sanitize_text(text: str) -> str:
    """Replace local user home paths with portable standard paths."""
    home = os.path.expanduser("~")
    # Replace ~/.gemini/config with ~/.gemini/config
    sanitized = text.replace(f"{home}/.gemini/config", "~/.gemini/config")
    sanitized = sanitized.replace(f"{home}/", "~/")
    # Generic regex for /home/[^/]+/.gemini/
    sanitized = re.sub(r"/home/[^/\s'\"]+/\.gemini/", "~/.gemini/", sanitized)
    return sanitized

def sanitize_file(file_path: Path):
    """Sanitizes a single text file in place."""
    try:
        content = file_path.read_text(encoding="utf-8")
        sanitized = sanitize_text(content)
        if sanitized != content:
            file_path.write_text(sanitized, encoding="utf-8")
    except UnicodeDecodeError:
        pass  # Binary file, skip

def export_skill(source_dir: Path, dest_repo: Path) -> dict:
    skill_name = source_dir.name
    dest_skill_dir = dest_repo / "skills" / skill_name
    dest_skill_dir.parent.mkdir(parents=True, exist_ok=True)

    if dest_skill_dir.exists():
        shutil.rmtree(dest_skill_dir)

    # Copy tree ignoring __pycache__, .git, and temp files
    def ignore_patterns(path, names):
        return [n for n in names if n in {"__pycache__", ".git", ".DS_Store"} or n.endswith((".pyc", ".db", ".wal", ".tmp"))]

    shutil.copytree(source_dir, dest_skill_dir, ignore=ignore_patterns)

    # Sanitize all text files in destination
    for root, _, files in os.walk(dest_skill_dir):
        for f in files:
            sanitize_file(Path(root) / f)

    # Extract description from SKILL.md
    desc = ""
    skill_md = dest_skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8")
        m = re.search(r"^description:\s*[>|]?[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", content, re.MULTILINE)
        if m:
            desc = " ".join([l.strip() for l in m.group(1).splitlines() if l.strip()])
        else:
            m2 = re.search(r"^description:\s*[\"']?(.+?)[\"']?\s*$", content, re.MULTILINE)
            if m2:
                desc = m2.group(1).strip()

    return {"name": skill_name, "type": "skill", "description": desc, "path": f"skills/{skill_name}"}

def update_root_readme(dest_repo: Path):
    """Updates the catalog README.md in the repo root."""
    readme_path = dest_repo / "README.md"
    skills_dir = dest_repo / "skills"
    skills = []

    if skills_dir.exists():
        for s in sorted(skills_dir.iterdir()):
            if s.is_dir() and (s / "SKILL.md").exists():
                skill_md = s / "SKILL.md"
                content = skill_md.read_text(encoding="utf-8")
                desc = "No description provided."
                m = re.search(r"^description:\s*[>|]?[^\n]*\n((?:[ \t]+[^\n]*\n?)+)", content, re.MULTILINE)
                if m:
                    desc = " ".join([l.strip() for l in m.group(1).splitlines() if l.strip()])
                else:
                    m2 = re.search(r"^description:\s*[\"']?(.+?)[\"']?\s*$", content, re.MULTILINE)
                    if m2:
                        desc = m2.group(1).strip()
                skills.append((s.name, desc))

    content = [
        "# 🚀 Antigravity Customizations",
        "",
        "A curated collection of skills, prompts, and customizations for [Google Antigravity IDE](https://gemini.google.com).",
        "",
        "---",
        "",
        "## 📦 Available Skills",
        "",
    ]

    if not skills:
        content.append("_No skills published yet._\n")
    else:
        content.append("| Skill | Description |")
        content.append("|:---|:---|")
        for name, desc in skills:
            # Shorten description if too long
            short_desc = desc[:140] + ("..." if len(desc) > 140 else "")
            content.append(f"| [`{name}`](./skills/{name}) | {short_desc} |")
        content.append("")

    # Detect remote origin url if available
    repo_url = "https://github.com/<username>/antigravity-customizations.git"
    try:
        import subprocess
        res = subprocess.run(["git", "-C", str(dest_repo), "config", "--get", "remote.origin.url"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            detected = res.stdout.strip()
            # Clean if contains token
            clean_url = re.sub(r'https://[^@]+@github\.com/', 'https://github.com/', detected)
            repo_url = clean_url
    except Exception:
        pass

    content.extend([
        "## 🛠️ How to Install",
        "",
        "### Option 1: Global Installation (Available across all projects)",
        "Copy the desired skill into your global Antigravity configuration:",
        "```bash",
        "# Clone this repository",
        f"git clone {repo_url} /tmp/antigravity-customizations",
        "",
        "# Install a specific skill (example: skill-creator)",
        "mkdir -p ~/.gemini/config/skills",
        "cp -r /tmp/antigravity-customizations/skills/<skill-name> ~/.gemini/config/skills/",
        "```",
        "",
        "### Option 2: Project-Only Installation (Workspace scope)",
        "Copy into your project's `.agents/skills/` directory:",
        "```bash",
        "mkdir -p .agents/skills",
        "cp -r /path/to/skill .agents/skills/<skill-name>",
        "```",
        "",
        "---",
        "",
        "## 📄 License",
        "This collection is open-sourced under the [MIT License](./LICENSE).",
    ])

    readme_path.write_text("\n".join(content) + "\n", encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Sanitize and export Antigravity customizations.")
    parser.add_argument("--source", required=True, help="Source path of the skill, prompt, or rule")
    parser.add_argument("--type", choices=["skill", "prompt", "rule"], default="skill", help="Type of customization")
    parser.add_argument("--dest-repo", required=True, help="Destination git repository path")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    dest_repo = Path(args.dest_repo).expanduser().resolve()

    if not source.exists():
        print(f"Error: Source does not exist: {source}", file=sys.stderr)
        sys.exit(1)

    dest_repo.mkdir(parents=True, exist_ok=True)

    # Ensure LICENSE exists
    license_file = dest_repo / "LICENSE"
    if not license_file.exists():
        import datetime
        license_file.write_text(DEFAULT_LICENSE.format(year=datetime.date.today().year), encoding="utf-8")

    if args.type == "skill":
        info = export_skill(source, dest_repo)
        print(f"✅ Skill exported: {info['name']} -> {dest_repo}/skills/{info['name']}")
    elif args.type in {"prompt", "rule"}:
        target_dir = dest_repo / (f"{args.type}s")
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_file = target_dir / source.name
        shutil.copy2(source, dest_file)
        sanitize_file(dest_file)
        print(f"✅ {args.type.capitalize()} exported: {source.name} -> {dest_file}")

    # Update root catalog
    update_root_readme(dest_repo)
    print(f"✅ Catalog updated: {dest_repo}/README.md")

if __name__ == "__main__":
    main()
