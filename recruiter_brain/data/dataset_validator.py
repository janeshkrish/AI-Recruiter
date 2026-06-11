"""
Dataset Validator
==================

Validates the loaded dataset for data quality issues.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from recruiter_brain.data.models import CandidateProfile


class DatasetValidator:
    """Validates data quality of the candidate records."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_candidate(self, candidate: CandidateProfile) -> bool:
        """
        Validate a single candidate record.
        Returns True if perfectly valid, False if it has critical errors.
        """
        is_valid = True
        cid = candidate.candidate_id

        # 1. Check ID format
        if not cid.startswith("CAND_") or len(cid) != 12:
            self.errors.append(f"[{cid}] Invalid ID format")
            is_valid = False

        # 2. Check profile basics
        if not candidate.profile.anonymized_name:
            self.errors.append(f"[{cid}] Missing name")
            is_valid = False
            
        if candidate.profile.years_of_experience < 0 or candidate.profile.years_of_experience > 60:
            self.warnings.append(f"[{cid}] Unrealistic years of experience: {candidate.profile.years_of_experience}")

        # 3. Check behavioral signals
        bs = candidate.redrob_signals
        if bs.recruiter_response_rate < 0 or bs.recruiter_response_rate > 1:
            self.errors.append(f"[{cid}] Invalid response rate: {bs.recruiter_response_rate}")
            is_valid = False

        if bs.interview_completion_rate < 0 or bs.interview_completion_rate > 1:
            self.errors.append(f"[{cid}] Invalid interview completion rate: {bs.interview_completion_rate}")
            is_valid = False

        # 4. Check skills
        if not candidate.skills:
            self.warnings.append(f"[{cid}] No skills listed")
            
        # 5. Check career history
        if not candidate.career_history:
            self.warnings.append(f"[{cid}] No career history listed")

        return is_valid

    def validate_batch(self, candidates: list[CandidateProfile]) -> dict[str, Any]:
        """Validate a batch of candidates and return a summary report."""
        logger.info(f"Validating {len(candidates)} candidates...")
        
        valid_count = 0
        self.errors = []
        self.warnings = []
        
        seen_ids = set()

        for c in candidates:
            if c.candidate_id in seen_ids:
                self.errors.append(f"[{c.candidate_id}] Duplicate ID")
                continue
            seen_ids.add(c.candidate_id)
            
            if self.validate_candidate(c):
                valid_count += 1

        report = {
            "total_checked": len(candidates),
            "valid_count": valid_count,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "sample_errors": self.errors[:10],
            "sample_warnings": self.warnings[:10]
        }
        
        logger.info(f"Validation complete: {valid_count}/{len(candidates)} fully valid.")
        return report
