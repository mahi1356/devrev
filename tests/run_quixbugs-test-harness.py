"""Feed QuixBugs buggy programs through the developer/reviewer loop and check
the fix against QuixBugs' own tests.

Usage:
    python tests/run_quixbugs.py bitcount
    python tests/run_quixbugs.py  # runs every program in python_programs/
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

# Step 1: locate the QuixBugs dataset and make src/ importable for the agents.
QUIXBUGS_DIR = Path(__file__).parent / "quixbugs"
PROGRAMS_DIR = QUIXBUGS_DIR / "python_programs"
TESTCASES_DIR = QUIXBUGS_DIR / "python_testcases"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from main_orthestrator import run  # noqa: E402


def extract_code(agent_output: str) -> str | None:
    """Step 2 helper: agents wrap code in ```python fences plus prose - pull
    just the code back out so it's a valid standalone module. Returns None
    if the agent's final reply had no code fence at all (e.g. it just
    confirmed the previous fix was fine in prose) - writing raw prose into
    a .py file would corrupt it rather than testing anything meaningful."""
    match = re.search(r"```(?:python)?\n(.*?)```", agent_output, re.DOTALL)
    return match.group(1) if match else None


def fix_one(name: str) -> bool:
    program_path = PROGRAMS_DIR / f"{name}.py"
    test_path = TESTCASES_DIR / f"test_{name}.py"
    if not program_path.exists() or not test_path.exists():
        print(f"[{name}] skipped: no program or test file found")
        return False

    buggy_source = program_path.read_text()

    # Step 3: run the buggy program through the developer/reviewer loop,
    # asking the agents to fix it rather than write it from scratch.
    task = f"This function has a bug. Fix it and return the corrected function only."
    agent_output = run(task, code=buggy_source)
    fixed_source = extract_code(agent_output)
    if fixed_source is None:
        print(f"[{name}] FAIL (agent's final reply had no code block)")
        return False

    # Step 4: QuixBugs' tests import `python_programs.<name>` directly, so the
    # simplest way to test the agent's fix is to swap it into that file,
    # run the test, then restore the original buggy file no matter what.
    backup = program_path.read_text()
    try:
        program_path.write_text(fixed_source)
        try:
            # Step 4b: an unfixed (or wrongly "fixed") program can infinite-loop
            # - QuixBugs' own bugs are often hangs, not just wrong answers - so
            # this must not run without a timeout.
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_path), "-q"],
                cwd=QUIXBUGS_DIR,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            print(f"[{name}] FAIL (timed out - fix likely still hangs)")
            return False
        passed = result.returncode == 0
        print(f"[{name}] {'PASS' if passed else 'FAIL'}")
        if not passed:
            print(result.stdout[-1000:])
        return passed
    finally:
        program_path.write_text(backup)


def main():
    # Step 5: run one named program, or every program in the dataset, and
    # report an aggregate pass rate.
    names = sys.argv[1:]
    if not names:
        names = sorted(p.stem for p in PROGRAMS_DIR.glob("*.py"))

    results = {name: fix_one(name) for name in names}
    passed = sum(results.values())
    print(f"\n{passed}/{len(results)} passed")


if __name__ == "__main__":
    main()
