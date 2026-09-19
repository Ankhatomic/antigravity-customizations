# Advanced Skill Writing Guide

Reference for writing high-quality Antigravity skills. Focus on triggering
accuracy, progressive disclosure, and meta-prompting principles.

---

## 1. The Triggering Problem

The single most common failure mode for skills is **undertriggering**: the agent
has the skill available but never activates it because the `description` doesn't
match the user's phrasing.

The agent reads only the `name` and `description` fields to decide whether to
activate a skill. The body of SKILL.md is invisible until activation.

**This means the description field is load-bearing. Treat it like an API contract.**

---

## 2. Description Anatomy

A strong description answers three questions:
1. **What** does the skill do?
2. **When** should it trigger? (specific contexts + user phrases)
3. **Why** use it instead of the agent's general knowledge?

### Template
```yaml
description: >-
  [What it does in one sentence]. Use this skill when [specific trigger
  contexts]. Activate even when the user says [indirect phrasings] — not just
  when they explicitly name the skill. [Optional: what NOT to use it for.]
```

---

## 3. Weak vs. Strong Descriptions

### Example: A dashboard-building skill

❌ **Weak (undertriggering risk):**
```yaml
description: "How to build a simple fast dashboard to display internal data."
```
Problems:
- Passive voice ("How to build")
- Only triggers if user says "dashboard"
- No mention of related concepts (metrics, visualization, charts)

✅ **Strong:**
```yaml
description: >-
  Build fast internal dashboards for data visualization. Use this skill
  whenever the user mentions dashboards, data visualization, internal metrics,
  charts, or wants to display any kind of company data — even if they don't
  explicitly ask for a "dashboard". Activate for prompts like "show me our
  sales data", "I want to track KPIs", or "create a view for this CSV".
```

---

### Example: A Git commit message formatter

❌ **Weak:**
```yaml
description: "Formats Git commit messages according to Conventional Commits."
```

✅ **Strong:**
```yaml
description: >-
  Format Git commit messages following the Conventional Commits specification.
  Use this skill when the user asks to write, format, or review a commit
  message, or when they say things like "help me commit this", "what should I
  write for the commit", or "review my git history". Activate whenever changes
  are being staged or committed, even if "commit message" isn't mentioned.
```

---

## 4. Overtriggering (the other failure)

The opposite problem: the description is so broad the skill activates
inappropriately, wasting context and producing irrelevant output.

**Signs of overtriggering:**
- Description uses only generic terms ("helps with data", "assists with files")
- No specificity about domain, tool, or workflow
- Missing exclusion clauses when the scope is narrow

**Fix:** Add scope boundaries:
```yaml
description: >-
  ... Use ONLY for internal Anthropic data pipelines. Do not activate for
  general CSV processing or external data sources.
```

---

## 5. Progressive Disclosure Patterns

### Pattern 1: Single-domain skill (flat structure)
Best for skills under 200 lines. Keep everything in SKILL.md.

### Pattern 2: Reference offload (2-level)
Best for skills with large lookup tables, schemas, or reference docs.

```
skill-name/
├── SKILL.md          ← core workflow; references point to below
└── references/
    └── api-docs.md   ← read only when relevant
```

In SKILL.md, signal when to load:
```markdown
For the full API response schema, read
[`references/api-docs.md`](./references/api-docs.md) before continuing.
```

### Pattern 3: Multi-domain branching (3-level)
Best for skills that vary significantly by context (e.g., cloud deployment
across AWS/GCP/Azure).

```
cloud-deploy/
├── SKILL.md          ← detects which cloud and routes
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

SKILL.md contains a routing decision:
```markdown
## Step 1: Identify Target Cloud
Determine the deployment target from the user's request or config files.
Then read ONLY the relevant reference:
- AWS → [`references/aws.md`](./references/aws.md)
- GCP → [`references/gcp.md`](./references/gcp.md)
- Azure → [`references/azure.md`](./references/azure.md)
```

### Pattern 4: Script delegation
Best for deterministic or computationally intensive steps.

```
data-processor/
├── SKILL.md
└── scripts/
    └── transform.py
```

In SKILL.md, reference the script explicitly:
```markdown
## Step 2: Run Transformation
Execute the transformation script:
```bash
python3 ./scripts/transform.py --input <file> --output <output_dir>
```
The script prints a summary on completion. Check for "SUCCESS" in the output.
```

Scripts run without being loaded into context — they're just executed.

---

## 6. Writing Style Principles

### Imperative form
Write instructions as direct commands to the agent, not passive descriptions.

❌ `The user's files should be backed up before any changes are made.`
✅ `Back up the user's files before making any changes.`

### Explain the why
Don't just say what to do — briefly explain why, especially for non-obvious steps.
The agent is more reliable when it understands intent.

❌ `Always create a snapshot before iterating.`
✅ `Always create a snapshot before iterating — this lets you use the old version as a baseline in A/B comparisons.`

### Theory of mind
The agent reads your skill without your context. Assume it knows nothing specific
about your project, tooling, or conventions unless you state it.

State the obvious if it's domain-specific:
```markdown
Note: In this codebase, "feature flags" are managed through LaunchDarkly,
NOT through environment variables. The SDK client is initialized in `src/flags.ts`.
```

### Avoid duplication
Don't explain general coding practices or things the agent already knows well.
Focus strictly on what's unique to your workflow.

❌ `Write clean, readable code with comments.`
✅ `Follow the naming convention in `src/types.ts` — use `PascalCase` for entity types and `snake_case` for raw DB column names.`

---

## 7. Output Format Specification

When precision matters, use an explicit template that the agent must follow:

```markdown
## Report Structure
ALWAYS use this exact template. Do not add or remove sections.

# [Skill Name] Evaluation Report — [Date]

## Summary
[2–3 sentence overview of results]

## Test Results

| Eval | With Skill | Without Skill | Delta |
|:-----|:-----------|:--------------|:------|
| ...  | X/Y passed | A/B passed    | +Z%   |

## Qualitative Findings
[Narrative comparison of output quality]

## Recommended Changes
1. [Change 1]
2. [Change 2]
```

For structured data outputs (JSON, CSV), include a minimal example showing the
exact schema — not just a description.

---

## 8. Validation Steps (Anti-Pattern Alert)

Every skill should tell the agent how to verify success. Without this, the agent
may report "done" when something silently failed.

**Good validation pattern:**
```markdown
## Verification
After running the script:
1. Check for "SUCCESS" in the script output (not just exit code 0)
2. Confirm the output file exists: `ls -la outputs/<expected-file>`
3. Spot-check 3 random rows in the output CSV match the expected format
4. If any check fails, re-run with `--verbose` flag and report the error
```

**Bad (vague):**
```markdown
Make sure it worked correctly.
```

---

## 9. Skill Description Self-Test Checklist

Before finalizing a skill description, run through this checklist:

- [ ] Does it state **what** the skill does in the first sentence?
- [ ] Does it list **specific trigger contexts** (not just the skill name)?
- [ ] Does it include **indirect phrasing examples** the user might say?
- [ ] Is it in **third-person** (Antigravity convention)?
- [ ] Does it have a **"pushy" nudge** for undertriggering prevention?
- [ ] Is it **under ~100 words** (descriptions get truncated in some contexts)?
- [ ] Does it avoid being so broad it triggers **inappropriately**?
- [ ] Does it clearly scope **what it does NOT handle** (if relevant)?

---

## 10. Anti-Patterns Catalog

| Anti-Pattern | Problem | Fix |
|:---|:---|:---|
| Passive description ("How to X") | Agent doesn't see it as actionable | Use imperative or declarative ("Does X", "Use to X") |
| Single-keyword trigger ("Use for dashboards") | Misses synonyms and indirect requests | List 3–5 trigger contexts and indirect phrasings |
| No output format | Agent improvises format inconsistently | Add explicit template or example output |
| No verification step | Silent failures go undetected | Add checklist or command to confirm success |
| 500+ line SKILL.md | Context window bloat on every activation | Offload to references/ or scripts/ |
| Duplicating general knowledge | Wastes token budget | Only document what's unique to your workflow |
| Missing edge cases | Skill fails on unusual inputs | Add a dedicated edge cases section |
| Jargon without definition | Non-technical users can't follow | Define on first use or add a glossary |
