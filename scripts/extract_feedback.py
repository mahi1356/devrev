"""Extracts reviewer feedback from raw conversation logs into a single archive, then deletes the source logs.

Usage:
    python scripts/extract_feedback.py [--dry-run] [--keep-days N]

By default all logs/*.json files are processed. --keep-days N skips logs newer than N days
(so you can archive old runs while leaving recent ones available for debugging).
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
ARCHIVE_PATH = LOG_DIR / "feedback_history.jsonl"


def extract(log_path: Path) -> dict:
    data = json.loads(log_path.read_text())
    return {
        "source": log_path.name,
        "task": data.get("task"),
        "rounds": [
            {"round": r["round"], "reviewer_feedback": r["reviewer_feedback"]}
            for r in data.get("rounds", [])
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="show what would happen without writing or deleting")
    parser.add_argument("--keep-days", type=int, default=0, help="skip logs newer than N days")
    args = parser.parse_args()

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.keep_days)
    log_files = sorted(LOG_DIR.glob("*.json"))

    processed = 0
    with (open(ARCHIVE_PATH, "a") if not args.dry_run else open("/dev/null", "a")) as archive:
        for log_path in log_files:
            mtime = datetime.fromtimestamp(log_path.stat().st_mtime, tz=timezone.utc)
            if args.keep_days and mtime > cutoff:
                continue

            entry = extract(log_path)
            if args.dry_run:
                print(f"[dry-run] would extract and delete {log_path.name}")
            else:
                archive.write(json.dumps(entry) + "\n")
                log_path.unlink()
            processed += 1

    print(f"{'Would process' if args.dry_run else 'Processed'} {processed} log file(s).")
    if not args.dry_run and processed:
        print(f"Feedback archived to {ARCHIVE_PATH}")


if __name__ == "__main__":
    main()
