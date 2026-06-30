#!/usr/bin/env python3
"""Offline Redrob submission generator.

No network calls, hosted LLM APIs, or runtime embedding inference are used.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.parser.jd_analyzer import DEFAULT_REDROB_JD
from src.ranking.ranker import OfflineRanker
from src.validation.submission_validator import SubmissionValidator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Redrob top-100 candidate ranking CSV offline.")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--jd", default=None, help="Optional path to a plain-text job description")
    parser.add_argument("--out", default="submission.csv", help="Output CSV path")
    args = parser.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8") if args.jd else DEFAULT_REDROB_JD
    ranker = OfflineRanker(jd_text=jd_text)
    rows = ranker.rank_jsonl(args.candidates, top_n=100)
    ranker.write_submission_csv(rows, args.out)

    validator = SubmissionValidator()
    errors = validator.validate_csv(args.out)
    errors.extend(validator.validate_repository(Path(__file__).resolve().parent))
    if errors:
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Submission is valid: {Path(args.out).resolve()}")


if __name__ == "__main__":
    main()
