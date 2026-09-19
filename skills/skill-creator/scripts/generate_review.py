#!/usr/bin/env python3
"""
generate_review.py — Antigravity Skill Creator review generator

Reads eval results from a workspace/iteration directory and generates a
comprehensive Markdown report comparing with_skill vs. without_skill runs.

Usage:
  python3 generate_review.py --workspace <dir> --iteration <label> [--output <file>]

Example:
  python3 generate_review.py \\
    --workspace my-skill-workspace \\
    --iteration iteration-1 \\
    --output review.md

Output:
  A Markdown report with:
  - Overall pass rate comparison table
  - Per-eval breakdown with assertion details
  - Qualitative diff placeholders
  - Timing/performance comparison
  - Recommended next steps
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# ─── Helpers ──────────────────────────────────────────────────────────────────

def pct(rate) -> str:
    if rate is None:
        return "N/A"
    return f"{round(rate * 100, 1)}%"


def delta_str(with_rate, without_rate) -> str:
    if with_rate is None or without_rate is None:
        return "N/A"
    delta = (with_rate - without_rate) * 100
    sign = "+" if delta >= 0 else ""
    icon = "🟢" if delta > 5 else ("🟡" if delta >= 0 else "🔴")
    return f"{icon} {sign}{round(delta, 1)}pp"


def fmt_duration(ms) -> str:
    if ms is None:
        return "N/A"
    if ms < 1000:
        return f"{ms}ms"
    return f"{round(ms / 1000, 1)}s"


def fmt_tokens(n) -> str:
    if n is None:
        return "N/A"
    if n >= 1000:
        return f"{round(n / 1000, 1)}k"
    return str(n)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def read_output_text(run_dir: Path) -> str:
    """Try to read the agent's output from a run directory."""
    for fname in ["output.txt", "result.txt", "response.txt"]:
        f = run_dir / fname
        if f.exists():
            return f.read_text(encoding="utf-8", errors="replace").strip()
    # Concatenate all txt files
    texts = []
    for f in sorted(run_dir.glob("*.txt")):
        texts.append(f.read_text(encoding="utf-8", errors="replace").strip())
    return "\n\n---\n\n".join(texts) if texts else "_No text output found._"


# ─── Report generation ────────────────────────────────────────────────────────

def generate_report(workspace: Path, iteration: str, output_path: Path) -> str:
    iter_dir = workspace / iteration

    if not iter_dir.exists():
        print(f"ERROR: Iteration directory not found: {iter_dir}", file=sys.stderr)
        sys.exit(1)

    # Load results_summary.json if it exists (pre-computed by run_eval.py)
    summary_file = iter_dir / "results_summary.json"
    summary = load_json(summary_file) if summary_file.exists() else None

    skill_name = summary.get("skill_name", workspace.name) if summary else workspace.name
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines += [
        f"# 📊 Skill Evaluation Report: `{skill_name}`",
        f"",
        f"**Iteration:** `{iteration}`  ",
        f"**Generated:** {generated_at}  ",
        f"**Workspace:** `{workspace}`",
        f"",
        "---",
        "",
    ]

    # ── Overall Summary ───────────────────────────────────────────────────────
    if summary and "overall" in summary:
        ov = summary["overall"]
        lines += [
            "## Overall Results",
            "",
            "| Condition | Pass Rate | Improvement |",
            "|:----------|:----------|:------------|",
            f"| ✅ With Skill | **{pct(ov.get('with_skill_pass_rate'))}** | {ov.get('improvement', 'N/A')} |",
            f"| ⬜ Without Skill | {pct(ov.get('without_skill_pass_rate'))} | — |",
            "",
            "---",
            "",
        ]

    # ── Per-Eval Breakdown ────────────────────────────────────────────────────
    lines += [
        "## Per-Eval Breakdown",
        "",
    ]

    # Discover eval directories
    eval_dirs = sorted([d for d in iter_dir.iterdir() if d.is_dir()])

    if not eval_dirs:
        lines.append("_No eval directories found in this iteration._")
    else:
        for eval_dir in eval_dirs:
            meta = load_json(eval_dir / "eval_metadata.json")
            eval_name = meta.get("eval_name", eval_dir.name)
            eval_id = meta.get("eval_id", "?")
            prompt = meta.get("prompt", "_prompt not recorded_")
            assertions = meta.get("assertions", [])

            with_dir = eval_dir / "with_skill"
            without_dir = eval_dir / "without_skill"
            with_outputs = eval_dir / "with_skill" / "outputs"
            without_outputs = eval_dir / "without_skill" / "outputs"

            with_timing = load_json(with_dir / "timing.json")
            without_timing = load_json(without_dir / "timing.json")

            # Pull pre-graded results if available
            graded_with = []
            graded_without = []
            if summary:
                for ev in summary.get("evals", []):
                    if str(ev.get("eval_id")) == str(eval_id) or ev.get("eval_name") == eval_name:
                        graded_with = ev.get("with_skill", {}).get("assertions", [])
                        graded_without = ev.get("without_skill", {}).get("assertions", [])
                        break

            lines += [
                f"### Eval {eval_id}: `{eval_name}`",
                "",
                f"> **Prompt:** {prompt}",
                "",
            ]

            # Timing comparison
            if with_timing or without_timing:
                lines += [
                    "**Performance:**",
                    "",
                    "| Metric | With Skill | Without Skill |",
                    "|:-------|:-----------|:--------------|",
                    f"| Duration | {fmt_duration(with_timing.get('duration_ms'))} | {fmt_duration(without_timing.get('duration_ms'))} |",
                    f"| Tokens | {fmt_tokens(with_timing.get('total_tokens'))} | {fmt_tokens(without_timing.get('total_tokens'))} |",
                    "",
                ]

            # Assertions table
            if assertions:
                lines += [
                    "**Assertions:**",
                    "",
                    "| Assertion | With Skill | Without Skill |",
                    "|:----------|:-----------|:--------------|",
                ]

                def icon_for(graded_list, assertion_name):
                    for g in graded_list:
                        if g.get("name") == assertion_name:
                            if g.get("qualitative"):
                                return "👀 Review"
                            passed = g.get("passed")
                            return "✅ Pass" if passed else ("❌ Fail" if passed is False else "❓")
                    return "❓ N/A"

                for a in assertions:
                    name = a.get("name", "(unnamed)")
                    qualitative = a.get("qualitative", False) or a.get("type") == "custom"
                    w_icon = icon_for(graded_with, name)
                    wo_icon = icon_for(graded_without, name)
                    lines.append(f"| {name} | {w_icon} | {wo_icon} |")

                lines.append("")

            # Qualitative diff
            lines += [
                "**Output Comparison:**",
                "",
                "<details>",
                "<summary>Show outputs side by side</summary>",
                "",
                "**With Skill:**",
                "```",
            ]
            lines.append(read_output_text(with_outputs)[:2000] + ("..." if len(read_output_text(with_outputs)) > 2000 else ""))
            lines += [
                "```",
                "",
                "**Without Skill:**",
                "```",
            ]
            lines.append(read_output_text(without_outputs)[:2000] + ("..." if len(read_output_text(without_outputs)) > 2000 else ""))
            lines += [
                "```",
                "",
                "</details>",
                "",
                "---",
                "",
            ]

    # ── Qualitative Notes ──────────────────────────────────────────────────────
    lines += [
        "## Qualitative Findings",
        "",
        "> _Fill in your observations after reviewing the outputs above._",
        "",
        "- [ ] With-skill outputs are clearly better / worse / similar",
        "- [ ] Specific improvements noticed: ",
        "- [ ] Specific regressions noticed: ",
        "- [ ] Edge cases that need more coverage: ",
        "",
        "---",
        "",
    ]

    # ── Recommended Next Steps ─────────────────────────────────────────────────
    lines += [
        "## Recommended Next Steps",
        "",
    ]
    if summary:
        ov = summary.get("overall", {})
        with_rate = ov.get("with_skill_pass_rate")
        if with_rate is not None:
            if with_rate >= 0.85:
                lines += [
                    "✅ **Pass rate is strong (≥85%).** Consider:",
                    "- Expanding the eval set to 5–10 cases covering more edge cases",
                    "- Running the trigger optimizer to ensure the skill activates reliably",
                    "- Promoting to a stable release (tag the workspace directory)",
                ]
            elif with_rate >= 0.60:
                lines += [
                    "⚠️ **Pass rate is moderate (60–85%).** Consider:",
                    "- Reviewing failing assertions to find patterns",
                    "- Rewriting the sections of SKILL.md responsible for failures",
                    "- Running iteration-2 with the improved skill vs. current as baseline",
                ]
            else:
                lines += [
                    "🔴 **Pass rate is low (<60%).** Consider:",
                    "- Revisiting the skill's core approach (not just wording)",
                    "- Checking if the skill is too broad — consider splitting into smaller skills",
                    "- Re-running the user interview to clarify success criteria",
                ]
    else:
        lines += [
            "- Review outputs above and fill in qualitative findings",
            "- Run `run_eval.py` to generate quantitative assertion grades",
            "- Iterate on SKILL.md based on observed failures",
        ]

    lines += [
        "",
        "---",
        "",
        f"_Report generated by `generate_review.py` at {generated_at}_",
    ]

    report = "\n".join(lines)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)
    print(f"✅ Review report saved to: {output_path}")
    return report


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Antigravity skill-creator review generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--workspace", required=True,
                        help="Path to the skill workspace directory")
    parser.add_argument("--iteration", required=True,
                        help="Iteration label (e.g. 'iteration-1')")
    parser.add_argument("--output", default="review.md",
                        help="Output file path (default: review.md)")

    args = parser.parse_args()

    workspace = Path(args.workspace)
    output_path = Path(args.output)

    generate_report(workspace, args.iteration, output_path)


if __name__ == "__main__":
    main()
