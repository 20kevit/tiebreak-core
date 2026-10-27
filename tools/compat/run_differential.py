#!/usr/bin/env python3
"""Differential harness: published v1.2.0 vs the release candidate.

Creates two isolated virtual environments, installs the *actual published
PyPI v1.2.0 wheel* in one and the current checkout in the other, runs the
same probe in each, and compares canonicalized outputs.

    python3 tools/compat/run_differential.py [--repo PATH] [--keep]

Writes:
    /tmp/tiebreak-compat/v120.json     probe output, published 1.2.0
    /tmp/tiebreak-compat/cand.json     probe output, candidate HEAD
    /tmp/tiebreak-compat/diff.json     machine-readable comparison
    /tmp/tiebreak-compat/diff.txt      human-readable report

Nothing in the repository or the caller's environment is modified.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

PROBE = Path(__file__).with_name("probe_v120.py")
WORK = Path("/tmp/tiebreak-compat")
WHEEL = "/tmp/v120/tiebreak_core-1.2.0-py3-none-any.whl"

CLASSIFICATIONS = {}


def note(tag, kind, detail):
    CLASSIFICATIONS[tag] = {"kind": kind, "detail": detail}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def make_env(path, install_cmd):
    if path.exists():
        shutil.rmtree(path)
    venv.EnvBuilder(with_pip=True).create(str(path))
    py = path / "bin" / "python"
    r = run([str(py), "-m", "pip", "install", "-q"] + install_cmd)
    if r.returncode != 0:
        raise SystemExit(f"install failed in {path}:\n{r.stderr}")
    return py


def probe(py):
    r = run([str(py), str(PROBE)])
    if r.returncode != 0:
        raise SystemExit(f"probe failed:\n{r.stdout}\n{r.stderr}")
    return json.loads(r.stdout)


def classify(tag, old, new):
    """Classify one case delta.  Returns a one-line summary."""
    o, n = old.get("status"), new.get("status")
    ov, nv = old.get("value"), new.get("value")
    oe, ne = old.get("error"), new.get("error")

    if o == "ok" and n == "ok":
        if ov == nv:
            return "UNCHANGED"
        note(tag, "behaviour-change", f"{ov!r} -> {nv!r}")
        return "BEHAVIOUR-CHANGE"
    if o == "error" and n == "error":
        if oe == ne:
            return "UNCHANGED-ERROR"
        note(tag, "error-change", f"{oe!r} -> {ne!r}")
        return "ERROR-CHANGE"
    if o == "ok" and n == "error":
        # A restriction or an intentional API/validation tightening.
        if "unexpected keyword argument" in (ne or "") or "positional" in (ne or ""):
            note(tag, "api-change", ne)
            return "API-CHANGE"
        note(tag, "restriction", f"{oe!r} -> {ne!r}")
        return "RESTRICTION"
    note(tag, "api-change", f"{oe!r} -> {nv!r}")
    return "API-CHANGE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(Path.cwd()))
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    if not (repo / "pyproject.toml").exists():
        raise SystemExit(f"{repo} does not look like the repository root")
    if not Path(WHEEL).exists():
        raise SystemExit(f"published wheel not found at {WHEEL}")

    WORK.mkdir(parents=True, exist_ok=True)
    envs = WORK / "envs"
    envs.mkdir(exist_ok=True)

    print("== building isolated environments ==", flush=True)
    py_old = make_env(envs / "v120", [WHEEL])
    py_new = make_env(envs / "cand", ["-e", str(repo)])

    print("== running probe: published v1.2.0 ==", flush=True)
    old = probe(py_old)
    print("== running probe: candidate ==", flush=True)
    new = probe(py_new)
    (WORK / "v120.json").write_text(json.dumps(old, indent=2, sort_keys=True))
    (WORK / "cand.json").write_text(json.dumps(new, indent=2, sort_keys=True))
    print(f"   published {old['version']}: {len(old['cases'])} cases")
    print(f"   candidate  {new['version']}: {len(new['cases'])} cases")

    rows = []
    for tag in sorted(set(old["cases"]) | set(new["cases"])):
        o = old["cases"].get(tag)
        n = new["cases"].get(tag)
        if o is None or n is None:
            rows.append((tag, "ONLY-IN-ONE", str(o or n)))
            continue
        rows.append((tag, classify(tag, o, n),
                     f"{o.get('value', o.get('error'))!r} -> "
                     f"{n.get('value', n.get('error'))!r}"))

    counts = {}
    for _, kind, _ in rows:
        counts[kind] = counts.get(kind, 0) + 1

    lines = [f"published={old['version']} candidate={new['version']}",
             f"rulesets(1.2.0)={old.get('rulesets')!r}",
             f"rulesets(cand)={new.get('rulesets')!r}", "",
             f"{'case':44s} {'class':18s} change", "-" * 110]
    for tag, kind, detail in rows:
        lines.append(f"{tag:44s} {kind:18s} {detail}")
    lines += ["", "counts:", json.dumps(counts, indent=2, sort_keys=True)]

    report = "\n".join(lines)
    (WORK / "diff.txt").write_text(report)
    (WORK / "diff.json").write_text(json.dumps(
        {"published_version": old["version"],
         "candidate_version": new["version"],
         "counts": counts,
         "cases": {t: {"kind": k, "change": d} for t, k, d in rows},
         "notes": CLASSIFICATIONS}, indent=2, sort_keys=True))

    print()
    print(report)
    if not args.keep:
        shutil.rmtree(envs, ignore_errors=True)
    print(f"\nartifacts in {WORK}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
