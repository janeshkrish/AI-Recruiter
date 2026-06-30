from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.parser.candidate_profile_parser import canonical


DEFAULT_REDROB_JD = """
Senior AI Engineer, Founding Team at Redrob AI. Build and own candidate-role
matching, ranking, retrieval, and recommendation systems. Must have production
experience with embeddings, hybrid retrieval, vector databases, strong Python,
and evaluation frameworks for ranking systems such as NDCG, MRR, MAP, offline
benchmarks, online A/B tests, and feedback loops. Strong positives include LLM
fine-tuning, LoRA, QLoRA, PEFT, learning-to-rank, HR-tech, marketplace products,
distributed systems, inference optimization, open source, and GitHub activity.
Reject pure research without production deployment, LangChain-only or framework
demo profiles, consulting-only careers, title chasers, manager-only profiles,
CV/speech/robotics-only specialists without NLP or IR, and keyword stuffing.
Prefer product-minded startup builders in Pune, Noida, Hyderabad, Mumbai, Delhi
NCR, Gurgaon, or candidates willing to relocate. Good response rate, recent
activity, open-to-work, and shorter notice period are positive signals.
"""


@dataclass(frozen=True)
class JDRequirements:
    must_have: list[str] = field(default_factory=list)
    nice_to_have: list[str] = field(default_factory=list)
    explicit_reject: list[str] = field(default_factory=list)
    culture_fit: list[str] = field(default_factory=list)
    behavior_fit: list[str] = field(default_factory=list)
    hiring_intent: list[str] = field(default_factory=list)
    years_min: float = 5.0
    years_max: float = 9.0
    preferred_locations: list[str] = field(default_factory=list)
    raw_text: str = ""


class JDAnalyzer:
    """Deterministically extracts hiring intent from a JD without an LLM."""

    MUST_HAVE_BANK = (
        "production ml",
        "embeddings",
        "sentence transformers",
        "bge",
        "e5",
        "retrieval",
        "hybrid retrieval",
        "ranking",
        "recommendation systems",
        "search systems",
        "vector databases",
        "pinecone",
        "weaviate",
        "qdrant",
        "milvus",
        "faiss",
        "opensearch",
        "elasticsearch",
        "python",
        "evaluation",
        "ndcg",
        "mrr",
        "map",
        "a/b testing",
    )
    NICE_BANK = (
        "llm fine tuning",
        "fine tuning",
        "lora",
        "qlora",
        "peft",
        "learning to rank",
        "xgboost",
        "hr tech",
        "marketplace",
        "distributed systems",
        "inference optimization",
        "open source",
        "github",
    )
    REJECT_BANK = (
        "consulting only",
        "title chaser",
        "framework enthusiast",
        "langchain only",
        "pure research",
        "no production deployment",
        "manager only",
        "computer vision only",
        "speech only",
        "robotics only",
        "keyword stuffing",
    )
    CULTURE_BANK = (
        "startup fit",
        "product mindset",
        "ship fast",
        "async writing",
        "ambiguity",
        "hands on coding",
        "mentoring",
        "ownership",
    )
    BEHAVIOR_BANK = (
        "recent activity",
        "response rate",
        "open to work",
        "short notice",
        "relocation",
        "github activity",
    )
    LOCATION_BANK = ("pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "bengaluru", "bangalore")

    def analyze(self, jd_text: str | None) -> JDRequirements:
        raw = jd_text.strip() if jd_text and jd_text.strip() else DEFAULT_REDROB_JD
        text = canonical(raw)
        years_min, years_max = self._extract_years(text)

        return JDRequirements(
            must_have=self._extract_terms(text, self.MUST_HAVE_BANK, default=[
                "production ml",
                "embeddings",
                "retrieval",
                "ranking",
                "vector databases",
                "python",
                "evaluation",
            ]),
            nice_to_have=self._extract_terms(text, self.NICE_BANK, default=[
                "llm fine tuning",
                "learning to rank",
                "marketplace",
                "distributed systems",
                "open source",
            ]),
            explicit_reject=self._extract_terms(text, self.REJECT_BANK, default=list(self.REJECT_BANK)),
            culture_fit=self._extract_terms(text, self.CULTURE_BANK, default=[
                "startup fit",
                "product mindset",
                "ship fast",
                "ownership",
                "hands on coding",
            ]),
            behavior_fit=self._extract_terms(text, self.BEHAVIOR_BANK, default=[
                "recent activity",
                "response rate",
                "open to work",
                "short notice",
                "relocation",
            ]),
            hiring_intent=[
                "own production retrieval and ranking systems",
                "ship product improvements quickly",
                "design evaluation infrastructure",
                "mentor as a senior IC",
                "avoid keyword-only AI profiles",
            ],
            years_min=years_min,
            years_max=years_max,
            preferred_locations=[loc for loc in self.LOCATION_BANK if loc in text] or ["pune", "noida", "hyderabad", "mumbai", "delhi", "gurgaon"],
            raw_text=raw,
        )

    def _extract_terms(self, text: str, bank: tuple[str, ...], default: list[str]) -> list[str]:
        terms = [term for term in bank if canonical(term) in text]
        return terms or default

    def _extract_years(self, text: str) -> tuple[float, float]:
        match = re.search(r"(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)\s*years", text)
        if match:
            return float(match.group(1)), float(match.group(2))
        match = re.search(r"(\d+(?:\.\d+)?)\+?\s*years", text)
        if match:
            years = float(match.group(1))
            return years, max(9.0, years + 4.0)
        return 5.0, 9.0

    def to_dict(self, requirements: JDRequirements) -> dict[str, Any]:
        return {
            "must_have": requirements.must_have,
            "nice_to_have": requirements.nice_to_have,
            "explicit_reject": requirements.explicit_reject,
            "culture_fit": requirements.culture_fit,
            "behavior_fit": requirements.behavior_fit,
            "hiring_intent": requirements.hiring_intent,
            "years_min": requirements.years_min,
            "years_max": requirements.years_max,
            "preferred_locations": requirements.preferred_locations,
            "skills": requirements.must_have + requirements.nice_to_have,
            "years_experience": requirements.years_min,
            "location": "/".join(requirements.preferred_locations[:3]),
            "require_degree": False,
            "hidden_traits": requirements.culture_fit,
            "anti_patterns": requirements.explicit_reject,
        }
