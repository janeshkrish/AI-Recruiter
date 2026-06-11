"""
Dataset Loader
===============

Loads the real challenge dataset from the JSONL file.
Uses chunked reading for memory efficiency or loads into pandas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Optional

from loguru import logger
from pydantic import ValidationError

from recruiter_brain.config import get_settings
from recruiter_brain.data.models import CandidateProfile


class DatasetLoader:
    """Loads candidates from the JSONL dataset file."""

    def __init__(self, dataset_path: Optional[str] = None):
        self.settings = get_settings()
        
        # Build path to candidates.jsonl
        base_path = Path(dataset_path or self.settings.dataset.path)
        self.file_path = base_path / self.settings.dataset.candidates_file
        
        if not self.file_path.exists():
            # Check if it's relative to project root
            project_root = Path(__file__).parent.parent.parent
            alt_path = project_root / self.settings.dataset.path / self.settings.dataset.candidates_file
            if alt_path.exists():
                self.file_path = alt_path
            else:
                logger.warning(f"Dataset not found at {self.file_path} or {alt_path}")

    def load_candidates_generator(self) -> Iterator[CandidateProfile]:
        """
        Yields CandidateProfile objects one by one to save memory.
        Handles dirty data by filling missing fields or casting types.
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.file_path}")

        logger.info(f"Streaming dataset from {self.file_path}...")
        
        valid_count = 0
        error_count = 0
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    data = json.loads(line)
                    
                    # 1. Ensure profile exists
                    if "profile" not in data or not isinstance(data["profile"], dict):
                        data["profile"] = {
                            "anonymized_name": f"Candidate_{data.get('candidate_id', 'Unknown')}"
                        }
                    else:
                        # Ensure string fallback for names
                        if not data["profile"].get("anonymized_name"):
                            data["profile"]["anonymized_name"] = "Unknown"

                    # 2. Fix dirty skills array
                    # Some candidates have strings instead of dicts: ["React", "Node"]
                    clean_skills = []
                    for s in data.get("skills", []):
                        if isinstance(s, str):
                            clean_skills.append({"name": s, "proficiency": "intermediate"})
                        elif isinstance(s, dict):
                            clean_skills.append(s)
                    data["skills"] = clean_skills
                    
                    # 3. Fix dirty education array
                    clean_edu = []
                    for e in data.get("education", []):
                        if isinstance(e, dict):
                            # Ensure tier is string
                            tier = e.get("tier", "unknown")
                            if isinstance(tier, int):
                                e["tier"] = f"tier_{tier}"
                            # Default year to 0 if missing
                            if "start_year" not in e: e["start_year"] = 0
                            if "end_year" not in e: e["end_year"] = 0
                            if "field_of_study" not in e: e["field_of_study"] = "Unknown"
                            clean_edu.append(e)
                    data["education"] = clean_edu

                    # Convert cleaned dict to Pydantic model
                    candidate = CandidateProfile(**data)
                    valid_count += 1
                    yield candidate
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error at line {line_idx+1}: {e}")
                    error_count += 1
                except ValidationError as e:
                    # Log first few validation errors to prevent terminal spam
                    if error_count < 5:
                        logger.error(f"Validation error for candidate at line {line_idx+1}: {e}")
                    error_count += 1
                except Exception as e:
                    if error_count < 5:
                        logger.error(f"Unexpected error at line {line_idx+1}: {e}")
                    error_count += 1
                    
        logger.info(f"Stream complete: {valid_count} valid, {error_count} errors.")

    def load_candidates_batch(self, limit: int = -1) -> list[CandidateProfile]:
        """
        Load a batch of candidates into memory.
        
        Args:
            limit: Maximum number to load. -1 means all.
        """
        candidates = []
        for i, candidate in enumerate(self.load_candidates_generator()):
            if limit > 0 and i >= limit:
                break
            candidates.append(candidate)
            
        logger.info(f"Loaded {len(candidates)} candidates into memory.")
        return candidates

    def get_candidate(self, candidate_id: str) -> Optional[CandidateProfile]:
        """
        Find a specific candidate by ID.
        """
        for candidate in self.load_candidates_generator():
            if candidate.candidate_id == candidate_id:
                return candidate
        return None
