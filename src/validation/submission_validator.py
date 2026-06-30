from __future__ import annotations

import csv
import re
from pathlib import Path


REQUIRED_HEADER = ["candidate_id", "rank", "score", "reasoning"]
EXPECTED_ROWS = 100
CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")
ALLOWED_REQUIREMENTS = {"numpy", "pandas", "rapidfuzz", "scikit-learn", "sentence-transformers"}
PROHIBITED_CODE_PATTERNS = (
    re.compile(r"^\s*(?:from|import)\s+openai\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+anthropic\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+cohere\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+groq\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+together\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+google\.generativeai\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+requests\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+httpx\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^\s*(?:from|import)\s+aiohttp\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"urllib\.request", re.IGNORECASE),
)


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

    def validate_repository(self, root: str | Path) -> list[str]:
        repo = Path(root)
        errors: list[str] = []

        if (repo / ".env").exists():
            errors.append(".env exists in the workspace; remove local API keys/secrets before submission.")
        if (repo / "recruiter_brain").exists():
            errors.append("Legacy recruiter_brain package exists; submission architecture must use src/.")

        requirements = repo / "requirements.txt"
        if requirements.exists():
            for line_number, line in enumerate(requirements.read_text(encoding="utf-8").splitlines(), start=1):
                dependency = line.strip()
                if not dependency or dependency.startswith("#"):
                    continue
                package = re.split(r"[<>=!~\[]", dependency, maxsplit=1)[0].strip().lower()
                if package not in ALLOWED_REQUIREMENTS:
                    errors.append(f"requirements.txt:{line_number}: dependency '{package}' is outside the allowed offline set.")

        for path in self._iter_executable_files(repo):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in PROHIBITED_CODE_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{path.relative_to(repo)} contains prohibited hosted-API/network code pattern: {pattern.pattern}")
                    break

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

    def _iter_executable_files(self, repo: Path):
        ignored_parts = {
            ".git",
            "venv",
            ".venv",
            "__pycache__",
            ".cache",
            "[PUB] India_runs_data_and_ai_challenge",
            "backend",
            "frontend",
        }
        for pattern in ("*.py", "Dockerfile", "docker-compose.yml", "pyproject.toml"):
            for path in repo.rglob(pattern):
                if any(part in ignored_parts for part in path.parts):
                    continue
                yield path
