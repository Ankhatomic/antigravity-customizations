#!/usr/bin/env python3
"""
run_eval.py — Antigravity Skill Creator eval runner

Runs skill evaluations in two modes:
  - eval:    Execute evals.json test cases and grade assertions
  - trigger: Test how well a skill description triggers on a set of prompts

Usage:
  python3 run_eval.py --mode eval --evals <evals.json> --workspace <dir> --iteration <n>
  python3 run_eval.py --mode trigger --skill-path <path> --prompts "prompt1,prompt2,..."

Output:
  - eval mode:    results_summary.json in the workspace/iteration directory
  - trigger mode: trigger_report.md with accuracy score and suggestions
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ─── Assertion grading ────────────────────────────────────────────────────────

def grade_assertion(assertion: dict, output_text: str, output_dir: Path) -> dict:
    """Grade a single assertion. Returns dict with passed, name, reason."""
    atype = assertion.get("type", "")
    name = assertion.get("name", "(unnamed)")

    # Qualitative assertions — always flag for human review
    if assertion.get("qualitative", False) or atype == "custom":
        return {
            "name": name,
            "type": atype,
            "passed": None,  # None = needs human review
            "reason": assertion.get("description", "Human review required"),
            "qualitative": True,
        }

    target = assertion.get("target", "output")

    # Determine what text to check
    if target == "output":
        text = output_text
    elif target == "file":
        file_path = output_dir / assertion.get("path", "")
        if not file_path.exists():
            return {
                "name": name,
                "type": atype,
                "passed": False,
                "reason": f"Target file not found: {file_path}",
                "qualitative": False,
            }
        text = file_path.read_text(encoding="utf-8", errors="replace")
    else:
        text = output_text

    # Grade by type
    try:
        if atype == "contains":
            value = assertion.get("value", "")
            passed = value in text
            reason = f"Found '{value}'" if passed else f"'{value}' not found in output"

        elif atype == "not_contains":
            value = assertion.get("value", "")
            passed = value not in text
            reason = f"'{value}' correctly absent" if passed else f"Output unexpectedly contains '{value}'"

        elif atype == "matches_regex":
            pattern = assertion.get("pattern", "")
            match = re.search(pattern, text)
            passed = match is not None
            reason = f"Pattern matched: {match.group(0)!r}" if passed else f"Pattern '{pattern}' not found"

        elif atype == "file_exists":
            file_path = output_dir / assertion.get("path", "")
            passed = file_path.exists()
            reason = f"File found: {file_path}" if passed else f"File not found: {file_path}"

        elif atype == "file_contains":
            file_path = output_dir / assertion.get("path", "")
            if not file_path.exists():
                passed = False
                reason = f"File not found: {file_path}"
            else:
                value = assertion.get("value", "")
                content = file_path.read_text(encoding="utf-8", errors="replace")
                passed = value in content
                reason = f"Found '{value}' in file" if passed else f"'{value}' not in file"

        elif atype == "json_valid":
            try:
                json.loads(text)
                passed = True
                reason = "Valid JSON"
            except json.JSONDecodeError as e:
                passed = False
                reason = f"Invalid JSON: {e}"

        else:
            passed = None
            reason = f"Unknown assertion type: {atype}"

    except Exception as e:
        passed = False
        reason = f"Error during grading: {e}"

    return {
        "name": name,
        "type": atype,
        "passed": passed,
        "reason": reason,
        "qualitative": False,
    }


def grade_eval(eval_meta: dict, with_skill_dir: Path, without_skill_dir: Path) -> dict:
    """Grade all assertions for one eval case. Returns graded result dict."""
    assertions = eval_meta.get("assertions", [])

    # Read outputs
    def read_output(run_dir: Path) -> str:
        # Try common output file names
        for fname in ["output.txt", "result.txt", "response.txt"]:
            f = run_dir / fname
            if f.exists():
                return f.read_text(encoding="utf-8", errors="replace")
        # Fall back to concatenating all .txt files
        texts = []
        for f in run_dir.glob("*.txt"):
            texts.append(f.read_text(encoding="utf-8", errors="replace"))
        return "\n".join(texts)

    with_text = read_output(with_skill_dir) if with_skill_dir.exists() else ""
    without_text = read_output(without_skill_dir) if without_skill_dir.exists() else ""

    graded = {
        "eval_id": eval_meta.get("eval_id"),
        "eval_name": eval_meta.get("eval_name", f"eval-{eval_meta.get('eval_id', '?')}"),
        "with_skill": [],
        "without_skill": [],
    }

    for assertion in assertions:
        graded["with_skill"].append(grade_assertion(assertion, with_text, with_skill_dir))
        graded["without_skill"].append(grade_assertion(assertion, without_text, without_skill_dir))

    return graded


# ─── Timing data ──────────────────────────────────────────────────────────────

def load_timing(run_dir: Path) -> dict:
    timing_file = run_dir / "timing.json"
    if timing_file.exists():
        try:
            return json.loads(timing_file.read_text())
        except json.JSONDecodeError:
            pass
    return {}


# ─── Summary generation ───────────────────────────────────────────────────────

def compute_pass_rate(assertions_result: list) -> dict:
    automated = [a for a in assertions_result if not a.get("qualitative", False) and a.get("passed") is not None]
    qualitative = [a for a in assertions_result if a.get("qualitative", False)]
    total = len(automated)
    passed = sum(1 for a in automated if a["passed"])
    return {
        "passed": passed,
        "total": total,
        "rate": round(passed / total, 4) if total > 0 else None,
        "qualitative_count": len(qualitative),
    }


def run_eval_mode(args):
    evals_path = Path(args.evals)
    workspace = Path(args.workspace)
    iteration = args.iteration or f"iteration-{int(time.time())}"
    iter_dir = workspace / iteration

    if not evals_path.exists():
        print(f"ERROR: evals file not found: {evals_path}", file=sys.stderr)
        sys.exit(1)

    evals_data = json.loads(evals_path.read_text())
    skill_name = evals_data.get("skill_name", "unknown-skill")
    evals = evals_data.get("evals", [])

    all_results = []
    overall_with = {"passed": 0, "total": 0}
    overall_without = {"passed": 0, "total": 0}

    for ev in evals:
        eval_id = ev["id"]
        eval_name = (
            ev.get("eval_name")
            or f"eval-{eval_id}-" + re.sub(r"[^a-z0-9]+", "-", ev["prompt"][:30].lower()).strip("-")
        )
        eval_dir = iter_dir / eval_name
        with_dir = eval_dir / "with_skill" / "outputs"
        without_dir = eval_dir / "without_skill" / "outputs"

        # Load eval_metadata.json if present (overrides evals.json assertions)
        meta_file = eval_dir / "eval_metadata.json"
        if meta_file.exists():
            eval_meta = json.loads(meta_file.read_text())
        else:
            eval_meta = {
                "eval_id": eval_id,
                "eval_name": eval_name,
                "prompt": ev["prompt"],
                "assertions": ev.get("assertions", []),
            }

        graded = grade_eval(eval_meta, with_dir, without_dir)

        with_timing = load_timing(eval_dir / "with_skill")
        without_timing = load_timing(eval_dir / "without_skill")

        with_rates = compute_pass_rate(graded["with_skill"])
        without_rates = compute_pass_rate(graded["without_skill"])

        # Accumulate overall
        overall_with["passed"] += with_rates["passed"]
        overall_with["total"] += with_rates["total"]
        overall_without["passed"] += without_rates["passed"]
        overall_without["total"] += without_rates["total"]

        delta_str = ""
        if with_rates["rate"] is not None and without_rates["rate"] is not None:
            delta = with_rates["rate"] - without_rates["rate"]
            sign = "+" if delta >= 0 else ""
            delta_str = f"{sign}{round(delta * 100, 1)}pp pass rate"

        all_results.append({
            "eval_id": eval_id,
            "eval_name": eval_name,
            "prompt_preview": ev["prompt"][:80] + ("..." if len(ev["prompt"]) > 80 else ""),
            "with_skill": {
                **with_rates,
                "duration_ms": with_timing.get("duration_ms"),
                "total_tokens": with_timing.get("total_tokens"),
                "assertions": graded["with_skill"],
            },
            "without_skill": {
                **without_rates,
                "duration_ms": without_timing.get("duration_ms"),
                "total_tokens": without_timing.get("total_tokens"),
                "assertions": graded["without_skill"],
            },
            "delta": delta_str,
        })

    overall_with_rate = round(overall_with["passed"] / overall_with["total"], 4) if overall_with["total"] > 0 else None
    overall_without_rate = round(overall_without["passed"] / overall_without["total"], 4) if overall_without["total"] > 0 else None

    summary = {
        "skill_name": skill_name,
        "iteration": iteration,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evals": all_results,
        "overall": {
            "with_skill_pass_rate": overall_with_rate,
            "without_skill_pass_rate": overall_without_rate,
            "improvement": (
                f"+{round((overall_with_rate - overall_without_rate) * 100, 1)}pp"
                if overall_with_rate is not None and overall_without_rate is not None
                else "N/A"
            ),
        },
    }

    out_file = iter_dir / "results_summary.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"✅ Results saved to: {out_file}")
    print(f"\n📊 Overall:")
    print(f"   With skill:    {(overall_with_rate or 0)*100:.1f}% pass rate")
    print(f"   Without skill: {(overall_without_rate or 0)*100:.1f}% pass rate")
    print(f"   Improvement:   {summary['overall']['improvement']}")
    return summary


# ─── Trigger mode ─────────────────────────────────────────────────────────────

def run_trigger_mode(args):
    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(f"ERROR: skill not found at: {skill_path}", file=sys.stderr)
        sys.exit(1)

    # Parse skill description from frontmatter
    content = skill_path.read_text()

    # Try multi-line block scalar (>- or | style)
    desc_match = re.search(
        r'^description:\s*[>|][^\n]*\n((?:[ \t]+[^\n]*\n?)+)',
        content, re.MULTILINE
    )
    # Try inline value
    inline_desc = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)

    if desc_match:
        raw = desc_match.group(1)
        # Strip leading indentation uniformly
        lines_d = [l.lstrip() for l in raw.splitlines()]
        description = " ".join(l for l in lines_d if l).strip()
    elif inline_desc:
        description = inline_desc.group(1).strip()
    else:
        description = "(could not parse description)"

    prompts_raw = args.prompts or ""
    prompts = [p.strip() for p in prompts_raw.split(",") if p.strip()]

    if not prompts:
        print("ERROR: --prompts is required in trigger mode", file=sys.stderr)
        sys.exit(1)

    print(f"\n🎯 Trigger Analysis for: {skill_path}")
    print(f"\n📋 Current description:\n{description}\n")
    print("=" * 60)

    results = []
    for i, prompt in enumerate(prompts, 1):
        # Heuristic: check if key terms from description appear in the prompt or vice versa
        desc_words = set(re.findall(r'\b\w{4,}\b', description.lower()))
        prompt_words = set(re.findall(r'\b\w{4,}\b', prompt.lower()))
        overlap = desc_words & prompt_words
        overlap_ratio = len(overlap) / max(len(prompt_words), 1)

        # Very rough heuristic trigger score
        if overlap_ratio >= 0.3:
            likely = "✅ Likely triggers"
            score = "HIGH"
        elif overlap_ratio >= 0.1:
            likely = "⚠️  May or may not trigger"
            score = "MEDIUM"
        else:
            likely = "❌ Unlikely to trigger"
            score = "LOW"

        print(f"\n[{i}] Prompt: \"{prompt}\"")
        print(f"    Trigger likelihood: {likely}")
        print(f"    Overlapping terms: {', '.join(sorted(overlap)) or 'none'}")
        results.append({"prompt": prompt, "score": score, "overlap": sorted(overlap)})

    # Suggestions
    print("\n" + "=" * 60)
    low_triggers = [r for r in results if r["score"] == "LOW"]
    medium_triggers = [r for r in results if r["score"] == "MEDIUM"]

    print("\n💡 Suggestions:")
    if low_triggers:
        missed_words = set()
        for r in low_triggers:
            for word in re.findall(r'\b\w{4,}\b', r["prompt"].lower()):
                if word not in re.findall(r'\b\w{4,}\b', description.lower()):
                    missed_words.add(word)
        print(f"  • {len(low_triggers)} prompt(s) unlikely to trigger the skill.")
        if missed_words:
            print(f"  • Consider adding these terms to the description: {', '.join(sorted(missed_words)[:10])}")
        print(f"  • Add a 'pushy' clause: \"Activate even when the user says [examples]...\"")
    elif medium_triggers:
        print(f"  • {len(medium_triggers)} prompt(s) have medium trigger likelihood.")
        print(f"  • Add more specific trigger examples to the description.")
    else:
        print("  • All test prompts appear likely to trigger the skill. ✓")
        print("  • Consider testing with more oblique/indirect phrasings.")

    # Save report
    report_path = skill_path.parent / "trigger_report.md"
    lines = [
        f"# Trigger Analysis Report\n",
        f"**Skill:** `{skill_path}`  ",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n",
        f"## Current Description\n\n```\n{description}\n```\n",
        f"## Results\n",
    ]
    for r in results:
        icon = {"HIGH": "✅", "MEDIUM": "⚠️", "LOW": "❌"}.get(r["score"], "?")
        lines.append(f"- {icon} **{r['score']}** — `{r['prompt']}`")
        if r["overlap"]:
            lines.append(f"  - Matching terms: {', '.join(r['overlap'])}")
    lines.append("\n## Suggestions\n")
    if low_triggers:
        lines.append(f"- Add indirect phrasing examples to description")
        lines.append(f"- Add 'pushy' activation clause")
    else:
        lines.append("- Description coverage looks good. Expand test set for confidence.")

    report_path.write_text("\n".join(lines))
    print(f"\n📄 Trigger report saved to: {report_path}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Antigravity skill-creator eval runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--mode", choices=["eval", "trigger"], default="eval",
                        help="Run mode: eval (grade test cases) or trigger (test description accuracy)")

    # eval mode args
    parser.add_argument("--evals", help="Path to evals.json file")
    parser.add_argument("--workspace", help="Workspace directory for results")
    parser.add_argument("--iteration", help="Iteration label (e.g. 'iteration-2')")

    # trigger mode args
    parser.add_argument("--skill-path", help="Path to the skill's SKILL.md file")
    parser.add_argument("--prompts", help="Comma-separated test prompts for trigger mode")

    args = parser.parse_args()

    if args.mode == "eval":
        if not args.evals or not args.workspace:
            parser.error("--evals and --workspace are required in eval mode")
        run_eval_mode(args)
    elif args.mode == "trigger":
        if not args.skill_path:
            parser.error("--skill-path is required in trigger mode")
        run_trigger_mode(args)


if __name__ == "__main__":
    main()
