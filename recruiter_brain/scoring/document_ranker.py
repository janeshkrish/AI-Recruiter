"""
Document-informed ranking for the Redrob Senior AI Engineer role.

This scorer is tuned from the attached JD, submission spec, and Redrob signals
reference. It avoids per-candidate LLM calls and only explains facts present in
the candidate profile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import math
import re
from typing import Any, Iterable


REFERENCE_DATE = date(2026, 6, 29)

PROFICIENCY_WEIGHT = {
    "expert": 1.0,
    "advanced": 0.86,
    "intermediate": 0.58,
    "beginner": 0.32,
}

CONSULTING_COMPANIES = {
    "tcs",
    "tata consultancy",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl",
    "tech mahindra",
    "mphasis",
    "mindtree",
    "l&t infotech",
    "lti",
    "ltimindtree",
    "hexaware",
    "persistent systems",
    "zensar",
    "birlasoft",
}

NON_TECH_TITLES = (
    "accountant",
    "business analyst",
    "content writer",
    "customer support",
    "graphic designer",
    "hr",
    "marketing",
    "operations manager",
    "project manager",
    "recruiter",
    "sales",
    "scrum master",
)

TECH_TITLES = (
    "ai engineer",
    "applied scientist",
    "backend engineer",
    "data engineer",
    "data scientist",
    "deep learning",
    "machine learning",
    "ml engineer",
    "nlp engineer",
    "platform engineer",
    "ranking",
    "recommendation",
    "search engineer",
    "software engineer",
)

REQUIRED_GROUPS = (
    {
        "label": "embeddings/retrieval",
        "weight": 0.30,
        "terms": (
            "embeddings",
            "sentence transformers",
            "semantic search",
            "information retrieval",
            "retrieval",
            "rag",
            "bm25",
            "search",
        ),
    },
    {
        "label": "vector or hybrid search",
        "weight": 0.24,
        "terms": (
            "vector database",
            "vector databases",
            "hybrid search",
            "pinecone",
            "weaviate",
            "qdrant",
            "milvus",
            "opensearch",
            "elasticsearch",
            "faiss",
            "chroma",
        ),
    },
    {
        "label": "ranking/evaluation",
        "weight": 0.28,
        "terms": (
            "ranking",
            "learning to rank",
            "learning-to-rank",
            "reranking",
            "re ranking",
            "recommendation systems",
            "recommendation",
            "recommender",
            "ndcg",
            "mrr",
            "map",
            "a b testing",
            "a/b testing",
            "ab testing",
            "evaluation",
            "relevance",
        ),
    },
    {
        "label": "Python",
        "weight": 0.18,
        "terms": ("python", "fastapi", "flask", "django", "pyspark"),
    },
)

NICE_TO_HAVE_GROUPS = (
    {
        "label": "LLM fine-tuning",
        "weight": 0.26,
        "terms": (
            "fine tuning",
            "fine-tuning",
            "lora",
            "qlora",
            "peft",
            "huggingface",
            "transformers",
            "llms",
            "llm",
        ),
    },
    {
        "label": "learning-to-rank",
        "weight": 0.22,
        "terms": ("learning to rank", "learning-to-rank", "xgboost", "lightgbm", "catboost"),
    },
    {
        "label": "HR-tech/marketplace",
        "weight": 0.18,
        "terms": ("hr tech", "hr-tech", "recruiting", "recruiter", "talent", "marketplace"),
    },
    {
        "label": "distributed/inference systems",
        "weight": 0.20,
        "terms": (
            "distributed systems",
            "large scale",
            "scale",
            "kubernetes",
            "docker",
            "mlops",
            "model deployment",
            "inference",
            "sagemaker",
            "mlflow",
        ),
    },
    {
        "label": "open-source/GitHub",
        "weight": 0.14,
        "terms": ("open source", "open-source", "github", "published", "talk"),
    },
)

PRODUCTION_TERMS = (
    "production",
    "deployed",
    "launched",
    "shipped",
    "built",
    "owned",
    "maintained",
    "real users",
    "user facing",
    "at scale",
    "on-call",
    "on call",
    "ab test",
    "a/b test",
    "metrics",
    "pipeline",
    "index",
    "ranker",
)

APPLIED_ML_TERMS = (
    "machine learning",
    "ml",
    "ai",
    "nlp",
    "llm",
    "retrieval",
    "ranking",
    "recommendation",
    "recommender",
    "search",
    "embeddings",
    "vector",
    "semantic",
    "rag",
)


@dataclass
class GroupEvidence:
    label: str
    score: float
    matched_skills: list[str] = field(default_factory=list)
    text_hits: list[str] = field(default_factory=list)


@dataclass
class CandidateScore:
    candidate_id: str
    raw_score: float
    reasoning: str
    candidate: dict[str, Any]


def _canonical(text: Any) -> str:
    value = "" if text is None else str(text).lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9+#./]+", " ", value)
    value = value.replace("-", " ")
    return re.sub(r"\s+", " ", value).strip()


def _contains(text: str, term: str) -> bool:
    needle = _canonical(term)
    if not needle:
        return False
    return needle in text


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        number = float(value)
        if math.isnan(number):
            return default
        return number
    except (TypeError, ValueError):
        return default


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _profile_completeness(value: Any) -> float:
    score = _as_float(value, 0.0)
    return _clamp(score / 100.0 if score > 1 else score)


def _skill_weight(skill: dict[str, Any]) -> float:
    return PROFICIENCY_WEIGHT.get(str(skill.get("proficiency", "")).lower(), 0.45)


class DocumentInformedRanker:
    """Ranks candidates for the attached Redrob Senior AI Engineer JD."""

    def rank(self, candidates: Iterable[dict[str, Any]], top_n: int = 100) -> list[dict[str, Any]]:
        scored: list[CandidateScore] = []

        for candidate in candidates:
            try:
                scored.append(self.score_candidate(candidate))
            except Exception:
                continue

        scored.sort(key=lambda row: (-row.raw_score, row.candidate_id))
        top = scored[: max(1, top_n)]
        if not top:
            return []

        rows: list[dict[str, Any]] = []
        for rank, row in enumerate(top, start=1):
            rows.append(
                {
                    "candidate_id": row.candidate_id,
                    "rank": rank,
                    "score": round(_clamp(row.raw_score), 3),
                    "reasoning": row.reasoning,
                    "candidate": row.candidate,
                }
            )
        return rows

    def score_candidate(self, data: dict[str, Any]) -> CandidateScore:
        candidate_id = str(data.get("candidate_id", ""))
        profile = data.get("profile", {}) or {}
        skills = data.get("skills", []) or []
        career = data.get("career_history", []) or []
        education = data.get("education", []) or []
        certifications = data.get("certifications", []) or []
        signals = data.get("redrob_signals", {}) or {}

        profile_text = _canonical(
            " ".join(
                [
                    profile.get("headline", ""),
                    profile.get("summary", ""),
                    profile.get("current_title", ""),
                    profile.get("current_industry", ""),
                ]
            )
        )
        career_text = _canonical(
            " ".join(
                [
                    " ".join(
                        [
                            str(job.get("title", "")),
                            str(job.get("company", "")),
                            str(job.get("industry", "")),
                            str(job.get("description", "")),
                        ]
                    )
                    for job in career
                    if isinstance(job, dict)
                ]
            )
        )
        all_text = _canonical(
            " ".join(
                [
                    profile_text,
                    career_text,
                    " ".join(str(s.get("name", "")) for s in skills if isinstance(s, dict)),
                    " ".join(str(c.get("name", "")) for c in certifications if isinstance(c, dict)),
                ]
            )
        )

        group_scores = [self._score_group(group, skills, all_text, career_text) for group in REQUIRED_GROUPS]
        core_score = sum(group.score * float(group_def["weight"]) for group, group_def in zip(group_scores, REQUIRED_GROUPS))
        core_hits = sum(1 for group in group_scores if group.score >= 0.56)

        nice_scores = [self._score_group(group, skills, all_text, career_text) for group in NICE_TO_HAVE_GROUPS]
        nice_score = sum(group.score * float(group_def["weight"]) for group, group_def in zip(nice_scores, NICE_TO_HAVE_GROUPS))

        experience_score = self._experience_score(profile)
        role_score = self._role_score(profile, career_text, core_score)
        applied_ml_score = self._applied_ml_score(career, career_text)
        career_score = (experience_score * 0.36) + (role_score * 0.34) + (applied_ml_score * 0.30)

        production_score = self._production_score(career_text, profile_text)
        product_company_score = self._product_company_score(profile, career)
        shipping_score = (production_score * 0.68) + (product_company_score * 0.32)

        behavior_score, behavior_facts = self._behavior_score(signals, profile)
        location_score = self._location_score(profile, signals)
        risk_multiplier, risk_flags = self._risk_multiplier(
            profile=profile,
            career=career,
            skills=skills,
            all_text=all_text,
            career_text=career_text,
            core_score=core_score,
        )

        raw_score = (
            (core_score * 0.38)
            + (career_score * 0.22)
            + (shipping_score * 0.14)
            + (behavior_score * 0.16)
            + (nice_score * 0.07)
            + (location_score * 0.03)
        )
        raw_score *= risk_multiplier

        candidate_summary = {
            "name": profile.get("anonymized_name", ""),
            "current_title": profile.get("current_title", ""),
            "years_of_experience": _as_float(profile.get("years_of_experience"), 0.0),
            "location": profile.get("location", ""),
            "current_company": profile.get("current_company", ""),
            "core_hits": core_hits,
        }

        reasoning = self._build_reasoning(
            profile=profile,
            group_scores=group_scores,
            nice_scores=nice_scores,
            core_hits=core_hits,
            applied_ml_score=applied_ml_score,
            production_score=production_score,
            behavior_facts=behavior_facts,
            risk_flags=risk_flags,
            raw_score=raw_score,
        )

        return CandidateScore(
            candidate_id=candidate_id,
            raw_score=_clamp(raw_score),
            reasoning=reasoning,
            candidate=candidate_summary,
        )

    def _score_group(
        self,
        group: dict[str, Any],
        skills: list[Any],
        all_text: str,
        career_text: str,
    ) -> GroupEvidence:
        best = 0.0
        matched_skills: list[str] = []
        text_hits: list[str] = []

        for term in group["terms"]:
            term_norm = _canonical(term)
            for skill in skills:
                if not isinstance(skill, dict):
                    continue
                name = str(skill.get("name", ""))
                skill_norm = _canonical(name)
                if not name or not skill_norm:
                    continue
                if term_norm == skill_norm or term_norm in skill_norm or skill_norm in term_norm:
                    best = max(best, _skill_weight(skill))
                    if name not in matched_skills:
                        matched_skills.append(name)

            if _contains(career_text, term):
                best = max(best, 0.78)
                if str(term) not in text_hits:
                    text_hits.append(str(term))
            elif _contains(all_text, term):
                best = max(best, 0.62)
                if str(term) not in text_hits:
                    text_hits.append(str(term))

        return GroupEvidence(
            label=str(group["label"]),
            score=_clamp(best),
            matched_skills=matched_skills[:4],
            text_hits=text_hits[:4],
        )

    def _experience_score(self, profile: dict[str, Any]) -> float:
        years = _as_float(profile.get("years_of_experience"), 0.0)
        if 5.0 <= years <= 9.0:
            return 1.0
        if 4.0 <= years < 5.0:
            return 0.84 + ((years - 4.0) * 0.16)
        if 9.0 < years <= 12.0:
            return 0.92 - ((years - 9.0) * 0.07)
        if 3.0 <= years < 4.0:
            return 0.62 + ((years - 3.0) * 0.18)
        if years > 12.0:
            return max(0.48, 0.72 - ((years - 12.0) * 0.035))
        return max(0.15, years / 5.0)

    def _role_score(self, profile: dict[str, Any], career_text: str, core_score: float) -> float:
        title = _canonical(profile.get("current_title", ""))
        if any(term in title for term in TECH_TITLES):
            return 1.0
        if any(term in title for term in NON_TECH_TITLES):
            return 0.25 + (core_score * 0.30)
        if any(term in career_text for term in ("engineer", "scientist", "developer", "architect")):
            return 0.74
        return 0.48

    def _applied_ml_score(self, career: list[Any], career_text: str) -> float:
        matched_months = 0
        total_months = 0
        for job in career:
            if not isinstance(job, dict):
                continue
            duration = int(_as_float(job.get("duration_months"), 0.0))
            total_months += duration
            job_text = _canonical(
                " ".join(
                    [
                        str(job.get("title", "")),
                        str(job.get("industry", "")),
                        str(job.get("description", "")),
                    ]
                )
            )
            if any(term in job_text for term in APPLIED_ML_TERMS):
                matched_months += duration

        inferred_years = matched_months / 12.0
        term_density = sum(1 for term in APPLIED_ML_TERMS if term in career_text)
        density_score = min(1.0, term_density / 8.0)
        years_score = min(1.0, inferred_years / 4.0)
        if total_months == 0:
            return density_score
        return max(density_score * 0.72, years_score)

    def _production_score(self, career_text: str, profile_text: str) -> float:
        hits = sum(1 for term in PRODUCTION_TERMS if term in career_text)
        profile_hits = sum(1 for term in PRODUCTION_TERMS if term in profile_text)
        return _clamp((hits / 7.0) + (profile_hits / 16.0))

    def _product_company_score(self, profile: dict[str, Any], career: list[Any]) -> float:
        industries = [_canonical(profile.get("current_industry", ""))]
        industries.extend(_canonical(job.get("industry", "")) for job in career if isinstance(job, dict))
        positive = (
            "software",
            "internet",
            "saas",
            "ecommerce",
            "e commerce",
            "fintech",
            "healthtech",
            "edtech",
            "marketplace",
            "ai",
            "technology",
            "product",
        )
        if any(any(term in industry for term in positive) for industry in industries):
            return 1.0
        if any("it services" in industry or "consulting" in industry for industry in industries):
            return 0.42
        return 0.68

    def _behavior_score(self, signals: dict[str, Any], profile: dict[str, Any]) -> tuple[float, dict[str, Any]]:
        response_rate = _clamp(_as_float(signals.get("recruiter_response_rate"), 0.0))
        open_to_work = 1.0 if signals.get("open_to_work_flag") else 0.42
        notice_days = int(_as_float(signals.get("notice_period_days"), 90.0))
        if notice_days <= 30:
            notice_score = 1.0
        elif notice_days <= 60:
            notice_score = 0.76
        elif notice_days <= 90:
            notice_score = 0.48
        else:
            notice_score = 0.22

        last_active = _parse_date(signals.get("last_active_date"))
        if last_active:
            days_since_active = max(0, (REFERENCE_DATE - last_active).days)
            if days_since_active <= 14:
                active_score = 1.0
            elif days_since_active <= 45:
                active_score = 0.88
            elif days_since_active <= 90:
                active_score = 0.68
            elif days_since_active <= 180:
                active_score = 0.42
            else:
                active_score = 0.18
        else:
            days_since_active = None
            active_score = 0.32

        completeness = _profile_completeness(signals.get("profile_completeness_score"))
        views_score = min(_as_float(signals.get("profile_views_received_30d"), 0.0) / 25.0, 1.0)
        saved_score = min(_as_float(signals.get("saved_by_recruiters_30d"), 0.0) / 8.0, 1.0)
        applications_score = min(_as_float(signals.get("applications_submitted_30d"), 0.0) / 8.0, 1.0)
        interview_score = _clamp(_as_float(signals.get("interview_completion_rate"), 0.0))
        github = _as_float(signals.get("github_activity_score"), -1.0)
        github_score = 0.55 if github < 0 else min(github / 100.0, 1.0)
        verified_score = (
            (0.34 if signals.get("verified_email") else 0.0)
            + (0.33 if signals.get("verified_phone") else 0.0)
            + (0.33 if signals.get("linkedin_connected") else 0.0)
        )

        engagement = (
            (completeness * 0.20)
            + (views_score * 0.14)
            + (saved_score * 0.18)
            + (applications_score * 0.10)
            + (interview_score * 0.18)
            + (github_score * 0.12)
            + (verified_score * 0.08)
        )

        location_score = self._location_score(profile, signals)
        behavior = (
            (response_rate * 0.28)
            + (active_score * 0.20)
            + (open_to_work * 0.14)
            + (notice_score * 0.15)
            + (engagement * 0.15)
            + (location_score * 0.08)
        )

        return _clamp(behavior), {
            "response_rate": response_rate,
            "notice_days": notice_days,
            "days_since_active": days_since_active,
            "open_to_work": bool(signals.get("open_to_work_flag")),
            "willing_to_relocate": bool(signals.get("willing_to_relocate")),
        }

    def _location_score(self, profile: dict[str, Any], signals: dict[str, Any]) -> float:
        location = _canonical(profile.get("location", ""))
        country = _canonical(profile.get("country", ""))
        preferred = ("pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "bengaluru", "bangalore")
        if any(city in location for city in preferred):
            return 1.0
        if signals.get("willing_to_relocate"):
            return 0.86
        if "india" in country:
            return 0.66
        return 0.26

    def _risk_multiplier(
        self,
        profile: dict[str, Any],
        career: list[Any],
        skills: list[Any],
        all_text: str,
        career_text: str,
        core_score: float,
    ) -> tuple[float, list[str]]:
        multiplier = 1.0
        flags: list[str] = []
        title = _canonical(profile.get("current_title", ""))

        if any(term in title for term in NON_TECH_TITLES):
            multiplier *= 0.58 if core_score >= 0.60 else 0.42
            flags.append(f"current role is {profile.get('current_title', 'non-technical')}")

        if career:
            companies = [_canonical(job.get("company", "")) for job in career if isinstance(job, dict)]
            industries = [_canonical(job.get("industry", "")) for job in career if isinstance(job, dict)]
            consulting_roles = 0
            for company, industry in zip(companies, industries):
                if any(c in company for c in CONSULTING_COMPANIES) or "it services" in industry or "consulting" in industry:
                    consulting_roles += 1
            if consulting_roles == len(career):
                multiplier *= 0.62
                flags.append("consulting-only career history")
            elif consulting_roles >= max(2, int(len(career) * 0.7)):
                multiplier *= 0.82
                flags.append("career is mostly services/consulting")

            if len(career) >= 3:
                durations = [int(_as_float(job.get("duration_months"), 24.0)) for job in career if isinstance(job, dict)]
                avg_tenure = sum(durations) / len(durations) if durations else 24.0
                if avg_tenure < 15:
                    multiplier *= 0.72
                    flags.append(f"short average tenure ({avg_tenure:.0f} months)")
                elif avg_tenure < 18:
                    multiplier *= 0.86
                    flags.append(f"below-ideal tenure ({avg_tenure:.0f} months)")

        research_heavy = any(term in all_text for term in ("research scientist", "academic", "lab", "publication", "paper"))
        production_light = not any(term in career_text for term in PRODUCTION_TERMS)
        if research_heavy and production_light:
            multiplier *= 0.66
            flags.append("research-heavy profile without clear production deployment")

        langchain_demo = any(term in all_text for term in ("langchain", "prompt engineering", "openai api"))
        retrieval_depth = any(term in all_text for term in ("retrieval", "ranking", "faiss", "vector", "search", "bm25", "recommendation"))
        if langchain_demo and not retrieval_depth:
            multiplier *= 0.64
            flags.append("LLM/framework exposure without deeper retrieval evidence")

        cv_speech = any(term in all_text for term in ("computer vision", "image classification", "object detection", "speech recognition", "robotics"))
        nlp_ir = any(term in all_text for term in ("nlp", "natural language", "retrieval", "search", "ranking", "rag", "llm"))
        if cv_speech and not nlp_ir:
            multiplier *= 0.70
            flags.append("CV/speech-heavy profile with limited NLP/IR evidence")

        zero_duration_expert = 0
        for skill in skills:
            if not isinstance(skill, dict):
                continue
            if str(skill.get("proficiency", "")).lower() == "expert" and int(_as_float(skill.get("duration_months"), 0.0)) == 0:
                zero_duration_expert += 1
        if zero_duration_expert >= 5:
            multiplier *= 0.18
            flags.append("honeypot-like expert skills with zero months used")
        elif zero_duration_expert >= 3:
            multiplier *= 0.55
            flags.append("suspicious zero-duration expert skills")

        return _clamp(multiplier, 0.08, 1.0), flags[:3]

    def _build_reasoning(
        self,
        profile: dict[str, Any],
        group_scores: list[GroupEvidence],
        nice_scores: list[GroupEvidence],
        core_hits: int,
        applied_ml_score: float,
        production_score: float,
        behavior_facts: dict[str, Any],
        risk_flags: list[str],
        raw_score: float,
    ) -> str:
        title = profile.get("current_title") or "Candidate"
        years = _as_float(profile.get("years_of_experience"), 0.0)
        company = profile.get("current_company") or "current company not listed"

        if raw_score >= 0.80:
            tier = "Excellent fit"
        elif raw_score >= 0.68:
            tier = "Strong fit"
        elif raw_score >= 0.54:
            tier = "Good fit"
        else:
            tier = "Qualified but lower-confidence fit"

        matched_groups = [g.label for g in group_scores if g.score >= 0.56]
        matched_skills: list[str] = []
        for group in group_scores + nice_scores:
            for skill in group.matched_skills:
                if skill not in matched_skills:
                    matched_skills.append(skill)
        skill_phrase = ", ".join(matched_skills[:5]) if matched_skills else ", ".join(matched_groups[:3])

        evidence_bits = []
        if skill_phrase:
            evidence_bits.append(f"{core_hits}/4 must-have groups evidenced via {skill_phrase}")
        else:
            evidence_bits.append(f"{core_hits}/4 must-have groups evidenced")

        if applied_ml_score >= 0.75:
            evidence_bits.append("career history shows applied ML/search relevance")
        elif applied_ml_score >= 0.45:
            evidence_bits.append("some applied ML/search adjacency")
        else:
            evidence_bits.append("limited explicit production retrieval/ranking history")

        if production_score >= 0.65:
            evidence_bits.append("production/shipping language is present")
        elif production_score < 0.30:
            evidence_bits.append("production deployment evidence is light")

        response = behavior_facts.get("response_rate", 0.0)
        notice = behavior_facts.get("notice_days", 90)
        active_days = behavior_facts.get("days_since_active")
        if active_days is None:
            behavior_text = f"response rate {response:.2f}; notice {notice}d"
        else:
            behavior_text = f"response rate {response:.2f}; active {active_days}d ago; notice {notice}d"
        evidence_bits.append(behavior_text)

        if risk_flags:
            evidence_bits.append("downweighted for " + "; ".join(risk_flags))

        reasoning = f"{tier}: {title} at {company} with {years:.1f} yrs; " + "; ".join(evidence_bits) + "."
        return re.sub(r"\s+", " ", reasoning).strip()
