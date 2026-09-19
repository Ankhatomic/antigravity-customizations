---
name: skill-creator
description: >-
  Create new skills, modify and improve existing skills, and measure skill
  performance within the Antigravity IDE ecosystem. Activate this skill
  whenever the user wants to: create a skill from scratch; edit, refactor, or
  optimize an existing skill; run evaluations (evals) to test a skill; benchmark
  skill performance with variance analysis; optimize a skill's description for
  better triggering accuracy; or understand how to structure customizations for
  Antigravity. Even if the user says something loosely like "I want to capture
  this workflow", "turn this into a skill", "make the agent remember how to do
  X", or "write instructions for the agent" — use this skill.
---

# Skill Creator (Antigravity Edition)

A skill for creating new Antigravity skills and iteratively improving them.

**This skill is itself a meta-skill**: it guides you through the full lifecycle
of skill creation — from capturing intent, through writing and testing, to
optimizing trigger accuracy — using Antigravity's conventions throughout.

> **Reference files (load only when needed):**
> - Full eval schema → [`references/schemas.md`](./references/schemas.md)
> - Advanced writing patterns → [`references/writing_guide.md`](./references/writing_guide.md)
> - Example of a well-structured skill → [`examples/example_skill/SKILL.md`](./examples/example_skill/SKILL.md)

---

## Antigravity Skill Architecture (Quick Reference)

Skills live in one of two locations:

| Scope | Path | Use When |
|:---|:---|:---|
| **Global** (all projects) | `~/.gemini/config/skills/<name>/SKILL.md` | Personal workflows, shared tooling |
| **Workspace** (project-only) | `.agents/skills/<name>/SKILL.md` | Team workflows, checked into VCS |

Workspace skills override global skills with the same name.

**Directory anatomy:**
```
skill-name/
├── SKILL.md          ← required; frontmatter + instructions (<500 lines ideal)
├── scripts/          ← executable helpers (Python/Bash)
├── references/       ← large docs loaded on-demand
├── examples/         ← reference implementations
└── assets/           ← templates, icons, data files
```

**Progressive Disclosure** — the agent sees only `name` + `description` by default.
The full `SKILL.md` body loads only when the skill activates. Reference files load
only when explicitly read. Keep the main file lean.

---

## Phase 1 — Capture Intent

Start by figuring out where the user is in the process. They might be:

- Describing a brand-new idea → go through the full interview
- Showing an existing draft → skip to evals/iteration
- Asking to optimize an existing skill → skip to Phase 6

**If starting fresh**, check the current conversation first. Extract:
- What tools were used, in what sequence
- What corrections the user made
- What the expected output looked like

Then confirm with the user before proceeding. Do NOT start writing the skill
until you have answers to at minimum:

1. What should this skill enable the agent to do?
2. When should this skill trigger? (user phrases, contexts, file types)
3. What is the expected output format?
4. Does the skill need verifiable test cases?
   - Objective outputs (file transforms, data extraction, fixed workflows) → YES
   - Subjective outputs (writing style, creative work) → probably not; decide together

---

## Phase 2 — Interview and Research

Proactively ask about edge cases, input/output formats, success criteria, and
dependencies. Be adaptive — if the user is non-technical, avoid jargon; if they
mention JSON schemas or assertions naturally, they're comfortable with precision.

**Research in parallel when useful:**
- Check if a similar skill already exists (global or workspace)
- Read relevant docs/references if the skill involves a specific toolchain
- Identify available MCP servers that the skill could leverage

Come prepared. Reduce burden on the user.

---

## Phase 3 — Write the SKILL.md

### Frontmatter

```yaml
---
name: skill-name-in-kebab-case
description: >-
  One-to-three sentence description. State WHAT the skill does AND WHEN to
  trigger it. Be slightly "pushy": mention specific user phrases and contexts
  that should activate the skill, even when the user doesn't use the exact
  skill name. This combats undertriggering.
---
```

**Undertriggering** is the most common skill failure. The agent sees only the
`description` field to decide whether to activate. Write it so even an oblique
user request triggers the skill. See [`references/writing_guide.md`](./references/writing_guide.md)
for weak vs. strong description examples.

### Body Structure

Use imperative form. Explain *why* things matter, not just *what* to do.
Apply theory of mind: imagine the agent reading this without your context.

Recommended sections:
- Overview + quick reference table
- Step-by-step procedure with decision points
- Output format specification (use explicit templates when precision matters)
- Validation / verification steps
- Edge cases and failure modes

Keep the main file under 500 lines. If approaching the limit, offload to
`references/` files and add clear pointers like:
> "For the full schema, read [`references/schemas.md`](./references/schemas.md)."

### Where to Save

After writing, save to the appropriate location:
- **Global** → `~/.gemini/config/skills/<name>/SKILL.md`
- **Workspace** → `.agents/skills/<name>/SKILL.md` (relative to project root)

Create the directory first if it doesn't exist.

---

## Phase 4 — Test Cases and Evals

### Design test cases

After the draft, create 2–3 realistic test prompts — things a real user would
actually say. Share them with the user and invite additions before running.

Save to `<skill-name>-workspace/evals/evals.json`:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's actual task prompt",
      "expected_output": "Description of what success looks like",
      "files": [],
      "assertions": []
    }
  ]
}
```

See [`references/schemas.md`](./references/schemas.md) for the full schema
including assertion types.

### Run A/B evaluations

Spawn **two subagents per eval in the same turn** — one with the skill, one
without (or against the old skill version if iterating). Do NOT stagger them.

**With-skill subagent prompt template:**
```
Execute this task using the skill at <path-to-skill>:
- Task: <eval prompt>
- Input files: <files or "none">
- Save all outputs to: <workspace>/iteration-<N>/<eval-name>/with_skill/outputs/
- Save: <what matters — the file, the report, the transformed data>
```

**Baseline subagent prompt template:**
```
Execute this task WITHOUT any skill:
- Task: <eval prompt>
- Input files: <files or "none">
- Save all outputs to: <workspace>/iteration-<N>/<eval-name>/without_skill/outputs/
```

Organize results as:
```
<skill-name>-workspace/
└── iteration-1/
    ├── <eval-name>/
    │   ├── with_skill/outputs/
    │   ├── without_skill/outputs/   (or old_skill/ if iterating)
    │   └── eval_metadata.json
    └── ...
```

Write `eval_metadata.json` for each case immediately (assertions can be empty):
```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

### While runs are in progress — draft assertions

Don't wait. Use that time to draft quantitative assertions and explain them to
the user. Good assertions are objectively verifiable and clearly named.

Assertion types (see [`references/schemas.md`](./references/schemas.md)):
- `contains` — output must contain a substring
- `not_contains` — output must NOT contain a substring
- `matches_regex` — output matches a regex pattern
- `file_exists` — a specific file was created
- `custom` — human-reviewed (mark as `qualitative: true`)

Update `eval_metadata.json` and `evals.json` with assertions once drafted.

### Generate the review

After runs complete, run the review generator:

```bash
python3 ~/.gemini/config/skills/skill-creator/scripts/generate_review.py \
  --workspace <skill-name>-workspace \
  --iteration iteration-1 \
  --output review.md
```

This produces a Markdown report comparing with_skill vs. without_skill results,
assertion pass rates, and qualitative side-by-side diffs.

---

## Phase 5 — Iterate

After reviewing results with the user:

1. Identify failure patterns (not just individual failures)
2. Rewrite the relevant sections of SKILL.md
3. If making structural changes, snapshot the old version first:
   ```bash
   cp -r <skill-path> <workspace>/skill-snapshot/
   ```
4. Run another eval iteration against the snapshot as the baseline
5. Repeat until satisfied

When the skill is stable on 2–3 test cases, expand to a larger test set (5–10
cases covering more edge cases).

---

## Phase 6 — Optimize Trigger Description

Even a perfect skill body fails if it never activates. Run the trigger optimizer
to refine the `description` field:

```bash
python3 ~/.gemini/config/skills/skill-creator/scripts/run_eval.py \
  --mode trigger \
  --skill-path <path-to-skill> \
  --prompts "list of test prompts, comma-separated"
```

The script tests whether the description alone causes the agent to recognize the
skill as relevant. It produces a trigger accuracy score and suggests improved
descriptions.

**Manual trigger optimization checklist:**
- [ ] Does the description mention specific user phrases that should activate it?
- [ ] Does it cover oblique / indirect requests (not just the exact skill name)?
- [ ] Does it avoid being so broad it triggers inappropriately?
- [ ] Is it written in third-person as the Antigravity convention requires?
- [ ] Does it include a "pushy" nudge like "Use this skill even when..."?

---

## Communication Style

Adapt to the user's technical level based on context cues:

- **Non-technical users**: Avoid "JSON", "assertion", "eval" without brief explanation
- **Technical users**: Use precise terminology freely
- **Default**: "evaluation" and "benchmark" are fine; explain "assertions" briefly
  on first use unless user already used the term

Always be flexible. If the user says "just write it, I don't need all the evals",
skip to Phase 3 and write a quality draft directly.
