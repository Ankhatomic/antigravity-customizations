---
name: grill-with-docs
description: >-
  Conduct a rigorous, structured design interview to stress-test ideas and
  architectural plans, automatically documenting settled decisions into
  persistent project records (ADRs or DECISOES.md). Use this skill whenever the
  user wants to stress-test a plan, refine an architecture, resolve design
  dilemmas, or uses phrases like "grill me", "grill with docs", "questione meu
  plano", "faça uma sabatina", "valide minha arquitetura", "salve nossas
  decisões", or asks to think through requirements before coding.
---

# Grill With Docs

Interview the user relentlessly to stress-test plans and architectural designs,
resolving ambiguities before code is written, and persisting all accepted
decisions into project documentation.

This skill combines the **relentless design tree inquiry** of `/grill-me` with
**stateful documentation** (Architecture Decision Records — ADRs or a unified
`DECISOES.md` / `CONTEXT.md`).

---

## Core Philosophy

1. **No coding during the grill phase:** Do not create or edit code files while
   interviewing. The focus is 100% on aligning intent and resolving trade-offs.
2. **Design Tree Mapping:** Map the problem as a decision tree. Each choice
   branches into subsequent decisions.
3. **Round-based Frontier:** In each round, ask only about settled prerequisites
   (the "frontier"). Do not jump ahead to questions that depend on unresolved
   prerequisites.
4. **Persistent Memory:** Once a round of decisions is settled, immediately
   record them into documentation so future agent sessions remember the context.

---

## Step 1: Context Discovery (Codebase Grounding)

Before asking the first question, check if the project already has context:
1. Look for existing documentation: `docs/decisions/`, `DECISOES.md`, `CONTEXT.md`,
   `README.md`, or architecture files.
2. Inspect package manifests (`package.json`, `go.mod`, `Cargo.toml`,
   `pyproject.toml`) to know the current stack.
3. Acknowledge existing constraints: *"I notice we are using PostgreSQL and Go;
   I will frame our choices within this stack."*

---

## Step 2: The Grilling Rounds

Group questions into logical rounds (typically 2 to 4 questions per round).

**Format each question exactly as follows:**

```markdown
❓ **Q1 — <Question Title>**
<Clear context explaining why this decision matters, edge cases, or potential risks.>

**Opções:**
- [A] <First viable alternative>
- [B] <Second viable alternative>
- [C] <Third alternative or fallback>

➡️ **Minha recomendação:** Opção [X], porque <strong technical rationale based on project goals>.

---
```

### Rules for Questions:
- Always number questions sequentially (`Q1`, `Q2`, etc.).
- Always provide viable multiple-choice options, but allow the user to suggest a custom answer.
- Always provide a recommended answer with clear technical reasoning.
- Wait for the user's response before proceeding to the next round.

---

## Step 3: Documenting Settled Decisions

When a round or the entire session is concluded, offer to persist the decisions.

### Format Option A: Architecture Decision Records (ADRs) — Recommended for medium/large apps
Save to `docs/decisions/NNN-title-in-kebab-case.md`:

```markdown
# ADR 001: <Title of the Decision>

- **Status:** Aceito
- **Data:** YYYY-MM-DD
- **Decisores:** Usuário & Antigravity

## Contexto
<What problem or dilemma prompted this decision?>

## Alternativas Consideradas
- Opção A: <description>
- Opção B: <description>

## Decisão Aprovada
<What was chosen and why it won over the alternatives.>

## Consequências
### Positivas:
- <Benefit 1>
- <Benefit 2>

### Trade-offs / Limitações:
- <Drawback or operational complexity accepted>
```

### Format Option B: Unified `DECISOES.md` — Recommended for small/fast projects
Append to `DECISOES.md` at the project root:

```markdown
## [YYYY-MM-DD] <Title of the Decision>
- **Contexto:** <Resumo do problema>
- **Decisão:** <O que foi decidido>
- **Trade-offs aceitos:** <O que abrimos mão>
```

---

## Step 4: Final Implementation Hand-off

Once all rounds are settled and recorded:
1. Present a concise **Plano de Execução** (checklist de tarefas).
2. Ask the user: *"Deseja que comecemos a implementar agora com base nessas decisões registradas?"*
3. Only begin touching code files after explicit user confirmation.
