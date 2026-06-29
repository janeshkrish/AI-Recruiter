from __future__ import annotations

import csv
import re
from pathlib import Path


REQUIRED_HEADER = ["candidate_id", "rank", "score", "reasoning"]
EXPECTED_ROWS = 100
CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")


class SubmissionValidator:
    """Validates Redrob submission CSV compliance."""

    def validate_csv(self, path: str | Path) -> list[str]:
        csv_path = Path(path)
        errors: list[str] = []
        if csv_path.suffix.lower() != ".csv":
            errors.append("Filename must use .csv extension.")
            return errors

        try:
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                try:
                    header = next(reader)
                except StopIteration:
                    return ["CSV is empty."]
                if header != REQUIRED_HEADER:
                    errors.append(f"Header must be exactly {','.join(REQUIRED_HEADER)}.")
                rows = [row for row in reader if any(cell.strip() for cell in row)]
        except UnicodeDecodeError:
            return ["CSV must be UTF-8 encoded."]

        errors.extend(self.validate_rows(rows))
        return errors

    def validate_rows(self, rows: list[list[str]]) -> list[str]:
        errors: list[str] = []
        if len(rows) != EXPECTED_ROWS:
            errors.append(f"Expected exactly {EXPECTED_ROWS} data rows; found {len(rows)}.")

        seen_ids: set[str] = set()
        seen_ranks: set[int] = set()
        by_rank: list[tuple[int, float, str]] = []

        for index, row in enumerate(rows, start=2):
            if len(row) != 4:
                errors.append(f"Row {index}: expected 4 columns, got {len(row)}.")
                continue
            candidate_id, rank_text, score_text, reasoning = [cell.strip() for cell in row]
            if not CANDIDATE_ID_PATTERN.match(candidate_id):
                errors.append(f"Row {index}: invalid candidate_id.")
            if candidate_id in seen_ids:
                errors.append(f"Row {index}: duplicate candidate_id {candidate_id}.")
            seen_ids.add(candidate_id)
            if not reasoning:
                errors.append(f"Row {index}: reasoning is required.")

            try:
                rank = int(rank_text)
                if rank < 1 or rank > 100:
                    errors.append(f"Row {index}: rank must be 1-100.")
                if rank in seen_ranks:
                    errors.append(f"Row {index}: duplicate rank {rank}.")
                seen_ranks.add(rank)
            except ValueError:
                errors.append(f"Row {index}: rank must be an integer.")
                continue

            try:
                score = float(score_text)
            except ValueError:
                errors.append(f"Row {index}: score must be a float.")
                continue

            by_rank.append((rank, score, candidate_id))

        missing = sorted(set(range(1, 101)) - seen_ranks)
        if missing:
            errors.append(f"Missing ranks: {missing}")

        by_rank.sort(key=lambda item: item[0])
        for (rank_a, score_a, candidate_a), (rank_b, score_b, candidate_b) in zip(by_rank, by_rank[1:]):
            if score_a < score_b:
                errors.append(f"Scores must be non-increasing: rank {rank_a} < rank {rank_b}.")
            if score_a == score_b and candidate_a > candidate_b:
                errors.append(f"Tie at ranks {rank_a}/{rank_b} must sort candidate_id ascending.")

        return errors
