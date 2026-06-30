from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from src.parser.candidate_profile_parser import ParsedCandidate, canonical
from src.parser.jd_analyzer import JDRequirements
from src.validation.honeypot_detector import HoneypotDetector, as_float, as_int, parse_date


REFERENCE_DATE = date(2026, 6, 29)

PROFICIENCY_WEIGHT = {
    "expert": 1.0,
    "advanced": 0.82,
    "intermediate": 0.56,
    "beginner": 0.28,
}

SERVICE_COMPANIES = (
    "tcs",
    "tata consultancy",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl",
    "tech mahindra",
    "mindtree",
    "ltimindtree",
    "lti",
    "mphasis",
    "hexaware",
    "persistent systems",
    "zensar",
    "birlasoft",
)

NON_TECH_TITLES = (
    "accountant",
    "customer support",
    "content writer",
    "graphic designer",
    "hr",
    "marketing",
    "operations manager",
    "recruiter",
    "sales",
    "scrum master",
)

SENIOR_TERMS = ("senior", "lead", "staff", "principal", "architect", "manager")
AI_TERMS = ("ai", "ml", "machine learning", "deep learning", "nlp", "llm", "retrieval", "ranking", "recommendation", "search", "embeddings", "vector", "semantic", "rag")
PRODUCTION_TERMS = ("production", "deployed", "launched", "shipped", "built", "owned", "maintained", "real users", "user facing", "at scale", "on call", "on-call", "pipeline", "index", "ranker", "monitoring")
RETRIEVAL_TERMS = ("retrieval", "information retrieval", "semantic search", "dense retrieval", "hybrid retrieval", "rag", "bm25", "search")
RANKING_TERMS = ("ranking", "ranker", "learning to rank", "learning-to-rank", "reranking", "re ranking", "relevance", "candidate matching")
RECOMMENDATION_TERMS = ("recommendation", "recommender", "personalization", "marketplace ranking", "feed ranking")
SEARCH_TERMS = ("search", "elasticsearch", "opensearch", "bm25", "query", "document retrieval")
EMBEDDING_TERMS = ("embedding", "embeddings", "sentence transformer", "sentence transformers", "bge", "e5", "dense vector")
VECTOR_DB_TERMS = ("vector database", "vector databases", "pinecone", "weaviate", "qdrant", "milvus", "faiss", "chroma", "ann index")
HYBRID_SEARCH_TERMS = ("hybrid search", "hybrid retrieval", "bm25", "dense retrieval", "sparse retrieval")
PYTHON_TERMS = ("python", "fastapi", "flask", "django", "pyspark", "pandas", "numpy")
EVALUATION_TERMS = ("ndcg", "mrr", "map", "precision", "recall", "offline evaluation", "online evaluation", "a/b", "ab testing", "a b testing", "benchmark", "metrics", "relevance evaluation")
OPEN_SOURCE_TERMS = ("open source", "open-source", "github", "published", "talk", "conference", "blog", "paper", "maintainer")
STARTUP_TERMS = ("startup", "series a", "founding", "early stage", "mvp", "scrappy")
PRODUCT_TERMS = ("product", "pm", "customer", "user", "recruiter workflow", "marketplace", "saas", "engagement")
RESEARCH_TERMS = ("research", "academic", "lab", "publication", "paper", "scientist")
FRAMEWORK_TERMS = ("langchain", "llamaindex", "haystack", "prompt engineering", "chatgpt", "demo", "tutorial")
CV_TERMS = ("computer vision", "image classification", "object detection", "segmentation", "opencv")
SPEECH_TERMS = ("speech", "speech recognition", "tts", "asr", "voice", "audio")
ROBOTICS_TERMS = ("robotics", "robot", "slam", "ros", "autonomous")
LOCATION_TERMS = ("pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "bengaluru", "bangalore")
CS_EDUCATION_TERMS = ("computer science", "data science", "machine learning", "artificial intelligence", "information technology", "statistics", "mathematics")
ADVANCED_DEGREE_TERMS = ("m.tech", "mtech", "m.s.", "ms", "master", "phd", "ph.d", "doctorate")
ML_CERT_TERMS = ("machine learning", "deep learning", "tensorflow", "pytorch", "aws machine learning", "azure ai", "google cloud ml", "data science")
CLOUD_MLOPS_TERMS = ("aws", "gcp", "azure", "kubernetes", "docker", "mlops", "mlflow", "kubeflow", "sagemaker", "vertex ai")
ENGLISH_PROFICIENCIES = {"native": 1.0, "professional": 0.85, "conversational": 0.55, "basic": 0.25}
COMPANY_SIZE_SCORE = {
    "1-10": 0.75,
    "11-50": 0.85,
    "51-200": 0.95,
    "201-500": 1.0,
    "501-1000": 0.92,
    "1001-5000": 0.84,
    "5001-10000": 0.76,
    "10001+": 0.68,
}

TERM_FLAG_BANK = sorted(
    set(
        AI_TERMS
        + PRODUCTION_TERMS
        + RETRIEVAL_TERMS
        + RANKING_TERMS
        + RECOMMENDATION_TERMS
        + SEARCH_TERMS
        + EMBEDDING_TERMS
        + VECTOR_DB_TERMS
        + HYBRID_SEARCH_TERMS
        + PYTHON_TERMS
        + EVALUATION_TERMS
        + OPEN_SOURCE_TERMS
        + STARTUP_TERMS
        + PRODUCT_TERMS
        + RESEARCH_TERMS
        + FRAMEWORK_TERMS
        + CV_TERMS
        + SPEECH_TERMS
        + ROBOTICS_TERMS
    )
)
TERM_FLAGS = tuple(
    (
        canonical(term).replace(" ", "_").replace("/", "_").replace("-", "_").replace("+", "plus").replace(".", ""),
        canonical(term),
    )
    for term in TERM_FLAG_BANK
)
CATEGORY_TERMS = {
    "production_ai": AI_TERMS + PRODUCTION_TERMS,
    "retrieval": RETRIEVAL_TERMS,
    "ranking": RANKING_TERMS,
    "recommendation_systems": RECOMMENDATION_TERMS,
    "search_systems": SEARCH_TERMS,
    "embeddings": EMBEDDING_TERMS,
    "vector_db": VECTOR_DB_TERMS,
    "hybrid_search": HYBRID_SEARCH_TERMS,
    "python": PYTHON_TERMS,
    "evaluation_metrics": EVALUATION_TERMS,
    "ab_testing": ("a/b", "ab testing", "a b testing", "experiment"),
    "open_source": OPEN_SOURCE_TERMS,
    "startup": STARTUP_TERMS,
    "product": PRODUCT_TERMS,
    "research": RESEARCH_TERMS,
    "framework": FRAMEWORK_TERMS,
    "computer_vision": CV_TERMS,
    "speech": SPEECH_TERMS,
    "robotics": ROBOTICS_TERMS,
}
CATEGORY_TERMS_CANONICAL = {
    name: tuple(canonical(term) for term in terms)
    for name, terms in CATEGORY_TERMS.items()
}
SKILL_CATEGORY_TERMS = (
    ("skill_python", PYTHON_TERMS),
    ("skill_retrieval", RETRIEVAL_TERMS),
    ("skill_ranking", RANKING_TERMS),
    ("skill_recommendation", RECOMMENDATION_TERMS),
    ("skill_search", SEARCH_TERMS),
    ("skill_embeddings", EMBEDDING_TERMS),
    ("skill_vector_db", VECTOR_DB_TERMS),
    ("skill_evaluation", EVALUATION_TERMS),
    ("skill_llm_finetuning", ("fine tuning", "fine-tuning", "lora", "qlora", "peft", "transformers")),
)
SKILL_CATEGORY_TERMS_CANONICAL = tuple(
    (category, tuple(canonical(term) for term in terms))
    for category, terms in SKILL_CATEGORY_TERMS
)
RELEVANT_ASSESSMENT_TERMS = tuple(canonical(term) for term in AI_TERMS + RETRIEVAL_TERMS + RANKING_TERMS + PYTHON_TERMS + EVALUATION_TERMS)


@dataclass
class FeatureSet:
    candidate_id: str
    values: dict[str, float]
    evidence: dict[str, list[str]] = field(default_factory=dict)
    risks: list[str] = field(default_factory=list)


class FeatureEngineer:
    """Creates 100+ deterministic features from the complete candidate profile."""

    def __init__(self) -> None:
        self.honeypot_detector = HoneypotDetector()

    def transform(self, candidate: ParsedCandidate, jd: JDRequirements) -> FeatureSet:
        profile = candidate.profile
        signals = candidate.redrob_signals
        title = canonical(profile.get("current_title"))
        location = canonical(profile.get("location"))
        country = canonical(profile.get("country"))
        all_text = candidate.all_text
        career_text = candidate.career_text
        skill_text = candidate.skill_text
        profile_text = candidate.profile_text
        certification_text = candidate.certification_text
        project_text = candidate.project_text

        values: dict[str, float] = {}
        evidence: dict[str, list[str]] = {}

        values["total_years_experience"] = as_float(profile.get("years_of_experience"), 0.0)
        values["experience_in_target_band"] = 1.0 if jd.years_min <= values["total_years_experience"] <= jd.years_max else 0.0
        values["experience_under_min"] = 1.0 if values["total_years_experience"] < jd.years_min else 0.0
        values["experience_over_max"] = 1.0 if values["total_years_experience"] > jd.years_max else 0.0
        values["career_role_count"] = float(len(candidate.career_history))
        values["education_count"] = float(len(candidate.education))
        values["certification_count"] = float(len(candidate.certifications))
        values["project_count"] = float(len(candidate.projects))
        values["language_count"] = float(len(candidate.languages))
        values["skill_count"] = float(len(candidate.skills))
        values["current_company_size_score"] = COMPANY_SIZE_SCORE.get(str(profile.get("current_company_size", "")), 0.5)
        values["current_company_product_industry_flag"] = 1.0 if self._is_product_industry(profile.get("current_industry")) else 0.0
        values["current_company_service_industry_flag"] = 1.0 if "service" in canonical(profile.get("current_industry")) or "consulting" in canonical(profile.get("current_industry")) else 0.0

        job_texts = [canonical(" ".join(str(job.get(key, "")) for key in job)) for job in candidate.career_history]
        durations = [max(0, as_int(job.get("duration_months"), 0)) for job in candidate.career_history]
        total_months = sum(durations)
        values["career_total_months"] = float(total_months)
        values["avg_tenure_months"] = float(sum(durations) / len(durations)) if durations else 0.0
        values["min_tenure_months"] = float(min(durations)) if durations else 0.0
        values["max_tenure_months"] = float(max(durations)) if durations else 0.0
        values["short_tenure_role_count"] = float(sum(1 for d in durations if 0 < d < 15))
        values["long_tenure_role_count"] = float(sum(1 for d in durations if d >= 30))
        values["current_role_months"] = float(max([as_int(job.get("duration_months"), 0) for job in candidate.career_history if job.get("is_current")] or [0]))
        values["senior_title_flag"] = self._flag_any(title, SENIOR_TERMS)
        values["non_technical_title_flag"] = self._flag_any(title, NON_TECH_TITLES)
        values.update(self._career_date_metrics(candidate))

        values["ai_months"] = self._months_for_terms_from_jobs(job_texts, durations, AI_TERMS)
        values["production_delivery_months"] = self._months_for_terms_from_jobs(job_texts, durations, PRODUCTION_TERMS)
        values["production_ai_months"] = self._months_for_term_groups_from_jobs(job_texts, durations, (AI_TERMS, PRODUCTION_TERMS))
        values["retrieval_months"] = self._months_for_terms_from_jobs(job_texts, durations, RETRIEVAL_TERMS)
        values["ranking_months"] = self._months_for_terms_from_jobs(job_texts, durations, RANKING_TERMS)
        values["recommendation_months"] = self._months_for_terms_from_jobs(job_texts, durations, RECOMMENDATION_TERMS)
        values["search_months"] = self._months_for_terms_from_jobs(job_texts, durations, SEARCH_TERMS)
        values["embeddings_months"] = self._months_for_terms_from_jobs(job_texts, durations, EMBEDDING_TERMS)
        values["vector_db_months"] = self._months_for_terms_from_jobs(job_texts, durations, VECTOR_DB_TERMS)
        values["hybrid_search_months"] = self._months_for_terms_from_jobs(job_texts, durations, HYBRID_SEARCH_TERMS)
        values["evaluation_months"] = self._months_for_terms_from_jobs(job_texts, durations, EVALUATION_TERMS)
        values["research_months"] = self._months_for_terms_from_jobs(job_texts, durations, RESEARCH_TERMS)
        values["product_months"] = self._months_for_terms_from_jobs(job_texts, durations, PRODUCT_TERMS)
        values["startup_months"] = self._months_for_terms_from_jobs(job_texts, durations, STARTUP_TERMS)
        values["service_months"] = self._service_months(candidate)
        values["product_company_months"] = self._product_company_months(candidate)
        values["years_in_ai"] = values["ai_months"] / 12.0
        values["years_in_product_companies"] = values["product_company_months"] / 12.0
        values["years_in_service_companies"] = values["service_months"] / 12.0

        term_presence = {term: term in all_text for _, term in TERM_FLAGS}
        for key, term in TERM_FLAGS:
            values[f"term_flag_{key}"] = 1.0 if term_presence[term] else 0.0

        for name, terms in CATEGORY_TERMS_CANONICAL.items():
            values[f"{name}_profile_term_count"] = float(self._count_terms(profile_text, terms))
            values[f"{name}_career_term_count"] = float(self._count_terms(career_text, terms))
            values[f"{name}_skill_term_count"] = float(self._count_terms(skill_text, terms))
            values[f"{name}_certification_term_count"] = float(self._count_terms(certification_text, terms)) if certification_text else 0.0
            values[f"{name}_project_term_count"] = float(self._count_terms(project_text, terms)) if project_text else 0.0
            values[f"{name}_all_term_count"] = float(sum(1 for term in terms if term_presence.get(term, False)))
            values[f"has_{name}"] = 1.0 if values[f"{name}_all_term_count"] > 0 else 0.0
            evidence[name] = [term for term in terms if term_presence.get(term, False)][:8]

        skill_metrics = self._skill_metrics(candidate)
        values.update(skill_metrics)
        values.update(self._education_metrics(candidate))
        values.update(self._certification_metrics(candidate))
        values.update(self._project_metrics(candidate))
        values.update(self._language_metrics(candidate))

        values["profile_completeness"] = self._fraction(signals.get("profile_completeness_score"), percent_scale=True)
        values["recruiter_response_rate"] = self._fraction(signals.get("recruiter_response_rate"))
        values["interview_completion_rate"] = self._fraction(signals.get("interview_completion_rate"))
        values["offer_acceptance_rate"] = max(0.0, self._fraction(signals.get("offer_acceptance_rate")))
        values["open_to_work_flag"] = 1.0 if signals.get("open_to_work_flag") else 0.0
        values["willing_to_relocate"] = 1.0 if signals.get("willing_to_relocate") else 0.0
        values["notice_period_days"] = as_float(signals.get("notice_period_days"), 90.0)
        values["short_notice_flag"] = 1.0 if values["notice_period_days"] <= 30 else 0.0
        values["reasonable_notice_flag"] = 1.0 if values["notice_period_days"] <= 60 else 0.0
        values["github_activity_score"] = max(0.0, as_float(signals.get("github_activity_score"), 0.0))
        values["github_linked_flag"] = 1.0 if as_float(signals.get("github_activity_score"), -1.0) >= 0 else 0.0
        values["profile_views_30d"] = as_float(signals.get("profile_views_received_30d"), 0.0)
        values["applications_30d"] = as_float(signals.get("applications_submitted_30d"), 0.0)
        values["search_appearance_30d"] = as_float(signals.get("search_appearance_30d"), 0.0)
        values["saved_by_recruiters_30d"] = as_float(signals.get("saved_by_recruiters_30d"), 0.0)
        values["connection_count"] = as_float(signals.get("connection_count"), 0.0)
        values["endorsements_received"] = as_float(signals.get("endorsements_received"), 0.0)
        values["verified_email"] = 1.0 if signals.get("verified_email") else 0.0
        values["verified_phone"] = 1.0 if signals.get("verified_phone") else 0.0
        values["linkedin_connected"] = 1.0 if signals.get("linkedin_connected") else 0.0
        values["avg_response_time_hours"] = as_float(signals.get("avg_response_time_hours"), 168.0)
        values["fast_response_flag"] = 1.0 if values["avg_response_time_hours"] <= 24 else 0.0
        values["recent_activity_days"] = self._days_since(signals.get("last_active_date"))
        values["recent_activity_flag"] = 1.0 if values["recent_activity_days"] <= 45 else 0.0
        values["active_14d_flag"] = 1.0 if values["recent_activity_days"] <= 14 else 0.0
        values.update(self._structured_signal_metrics(signals))

        values["preferred_location_flag"] = 1.0 if any(loc in location for loc in jd.preferred_locations) else 0.0
        values["india_flag"] = 1.0 if "india" in country else 0.0
        values["location_or_relocation_fit"] = max(values["preferred_location_flag"], values["willing_to_relocate"] * 0.86, values["india_flag"] * 0.65)

        service_roles = self._service_role_count(candidate)
        values["service_role_count"] = float(service_roles)
        values["consulting_only_flag"] = 1.0 if candidate.career_history and service_roles == len(candidate.career_history) else 0.0
        values["mostly_service_flag"] = 1.0 if candidate.career_history and service_roles >= max(2, int(len(candidate.career_history) * 0.7)) else 0.0
        values["framework_enthusiast_flag"] = 1.0 if values["has_framework"] and not (values["has_retrieval"] or values["has_ranking"] or values["has_vector_db"]) else 0.0
        values["langchain_only_flag"] = 1.0 if "langchain" in all_text and not (values["has_retrieval"] or values["has_ranking"] or values["has_vector_db"]) else 0.0
        values["computer_vision_only_flag"] = 1.0 if values["has_computer_vision"] and not (values["has_retrieval"] or values["has_ranking"] or "nlp" in all_text or "llm" in all_text) else 0.0
        values["speech_only_flag"] = 1.0 if values["has_speech"] and not (values["has_retrieval"] or values["has_ranking"] or "nlp" in all_text or "llm" in all_text) else 0.0
        values["robotics_only_flag"] = 1.0 if values["has_robotics"] and not (values["has_retrieval"] or values["has_ranking"] or "nlp" in all_text or "llm" in all_text) else 0.0
        values["research_only_flag"] = 1.0 if values["has_research"] and values["has_production_ai"] == 0.0 else 0.0
        values["title_chaser_flag"] = 1.0 if len(candidate.career_history) >= 3 and values["avg_tenure_months"] < 18 and values["senior_title_flag"] else 0.0
        values["manager_only_flag"] = 1.0 if "manager" in title and not any(term in all_text for term in ("python", "built", "deployed", "production code", "hands on")) else 0.0
        values["keyword_stuffer_flag"] = 1.0 if values["skill_count"] >= 40 and values["production_ai_months"] < 18 else 0.0
        values["no_recent_code_flag"] = 1.0 if values["manager_only_flag"] or ("architect" in title and "production code" not in all_text and "python" not in all_text) else 0.0

        honeypot = self.honeypot_detector.evaluate(candidate)
        values["honeypot_penalty"] = honeypot.penalty
        values["honeypot_flag_count"] = float(len(honeypot.flags))

        risks = list(honeypot.flags)
        for feature, label in (
            ("consulting_only_flag", "consulting-only career"),
            ("framework_enthusiast_flag", "framework/demo-heavy profile"),
            ("langchain_only_flag", "LangChain-only AI evidence"),
            ("computer_vision_only_flag", "computer-vision-only profile"),
            ("speech_only_flag", "speech-only profile"),
            ("robotics_only_flag", "robotics-only profile"),
            ("research_only_flag", "research without production deployment"),
            ("title_chaser_flag", "short-tenure title progression"),
            ("manager_only_flag", "manager/architecture without recent coding evidence"),
            ("keyword_stuffer_flag", "broad keyword-stuffed skill list"),
        ):
            if values.get(feature, 0.0) > 0:
                risks.append(label)

        return FeatureSet(candidate_id=candidate.candidate_id, values=values, evidence=evidence, risks=risks[:8])

    def _flag_any(self, text: str, terms: tuple[str, ...]) -> float:
        return 1.0 if any(canonical(term) in text for term in terms) else 0.0

    def _count_terms(self, text: str, terms: tuple[str, ...]) -> int:
        return sum(1 for term in terms if term in text)

    def _matched_terms(self, text: str, terms: tuple[str, ...]) -> list[str]:
        return [term for term in terms if canonical(term) in text]

    def _career_date_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values: dict[str, float] = {
            "career_start_year": 0.0,
            "career_end_year_latest": 0.0,
            "current_role_count": 0.0,
            "career_gap_months_estimate": 0.0,
            "career_overlap_months_estimate": 0.0,
            "career_duration_date_mismatch_count": 0.0,
        }
        intervals: list[tuple[datetime, datetime]] = []
        for job in candidate.career_history:
            start = parse_date(job.get("start_date"))
            end = parse_date(job.get("end_date")) or datetime.combine(REFERENCE_DATE, datetime.min.time())
            if job.get("is_current"):
                values["current_role_count"] += 1.0
            if start:
                values["career_start_year"] = min(values["career_start_year"] or float(start.year), float(start.year))
                values["career_end_year_latest"] = max(values["career_end_year_latest"], float(end.year))
                intervals.append((start, end))
                expected = self._months_between(start, end)
                actual = as_int(job.get("duration_months"), 0)
                if actual and abs(actual - expected) > 6:
                    values["career_duration_date_mismatch_count"] += 1.0

        intervals.sort(key=lambda item: item[0])
        for previous, current in zip(intervals, intervals[1:]):
            previous_end = previous[1]
            current_start = current[0]
            if current_start > previous_end:
                values["career_gap_months_estimate"] += float(self._months_between(previous_end, current_start))
            elif current_start < previous_end:
                values["career_overlap_months_estimate"] += float(self._months_between(current_start, previous_end))
        return values

    def _months_for_terms(
        self,
        candidate: ParsedCandidate,
        terms: tuple[str, ...],
        require_any: tuple[str, ...] | None = None,
    ) -> float:
        months = 0.0
        required = require_any or terms
        for job in candidate.career_history:
            job_text = canonical(" ".join(str(job.get(key, "")) for key in job))
            if any(canonical(term) in job_text for term in terms) and any(canonical(term) in job_text for term in required):
                months += max(0, as_int(job.get("duration_months"), 0))
        return months

    def _months_for_terms_from_jobs(self, job_texts: list[str], durations: list[int], terms: tuple[str, ...]) -> float:
        canonical_terms = tuple(canonical(term) for term in terms)
        return float(
            sum(
                duration
                for job_text, duration in zip(job_texts, durations)
                if any(term in job_text for term in canonical_terms)
            )
        )

    def _months_for_term_groups(self, candidate: ParsedCandidate, groups: tuple[tuple[str, ...], ...]) -> float:
        months = 0.0
        canonical_groups = tuple(tuple(canonical(term) for term in group) for group in groups)
        for job in candidate.career_history:
            job_text = canonical(" ".join(str(job.get(key, "")) for key in job))
            if all(any(term in job_text for term in group) for group in canonical_groups):
                months += max(0, as_int(job.get("duration_months"), 0))
        return months

    def _months_for_term_groups_from_jobs(self, job_texts: list[str], durations: list[int], groups: tuple[tuple[str, ...], ...]) -> float:
        canonical_groups = tuple(tuple(canonical(term) for term in group) for group in groups)
        return float(
            sum(
                duration
                for job_text, duration in zip(job_texts, durations)
                if all(any(term in job_text for term in group) for group in canonical_groups)
            )
        )

    def _education_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values: dict[str, float] = {
            "cs_or_quant_education_flag": 0.0,
            "advanced_degree_flag": 0.0,
            "tier_1_education_flag": 0.0,
            "tier_2_plus_education_flag": 0.0,
            "education_tier_score": 0.0,
            "latest_education_end_year": 0.0,
        }
        tier_score = {"tier_1": 1.0, "tier_2": 0.75, "tier_3": 0.45, "tier_4": 0.25, "unknown": 0.35}
        for item in candidate.education:
            text = canonical(" ".join(str(item.get(key, "")) for key in item))
            tier = canonical(item.get("tier"))
            values["cs_or_quant_education_flag"] = max(values["cs_or_quant_education_flag"], self._flag_any(text, CS_EDUCATION_TERMS))
            values["advanced_degree_flag"] = max(values["advanced_degree_flag"], self._flag_any(text, ADVANCED_DEGREE_TERMS))
            values["tier_1_education_flag"] = max(values["tier_1_education_flag"], 1.0 if tier == "tier_1" else 0.0)
            values["tier_2_plus_education_flag"] = max(values["tier_2_plus_education_flag"], 1.0 if tier in {"tier_1", "tier_2"} else 0.0)
            values["education_tier_score"] = max(values["education_tier_score"], tier_score.get(tier, 0.35))
            values["latest_education_end_year"] = max(values["latest_education_end_year"], as_float(item.get("end_year"), 0.0))
        return values

    def _certification_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values = {
            "ml_certification_count": 0.0,
            "cloud_mlops_certification_count": 0.0,
            "recent_certification_count": 0.0,
            "certification_recency_score": 0.0,
        }
        for item in candidate.certifications:
            text = canonical(" ".join(str(item.get(key, "")) for key in item))
            year = as_int(item.get("year"), 0)
            if self._flag_any(text, ML_CERT_TERMS):
                values["ml_certification_count"] += 1.0
            if self._flag_any(text, CLOUD_MLOPS_TERMS):
                values["cloud_mlops_certification_count"] += 1.0
            if year >= REFERENCE_DATE.year - 3:
                values["recent_certification_count"] += 1.0
                values["certification_recency_score"] = max(values["certification_recency_score"], 1.0 - max(0, REFERENCE_DATE.year - year) / 4.0)
        return values

    def _project_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values = {
            "production_project_count": 0.0,
            "retrieval_project_count": 0.0,
            "ranking_project_count": 0.0,
            "vector_project_count": 0.0,
            "evaluation_project_count": 0.0,
            "open_source_project_count": 0.0,
        }
        for item in candidate.projects:
            text = canonical(" ".join(str(item.get(key, "")) for key in item))
            values["production_project_count"] += self._flag_any(text, PRODUCTION_TERMS)
            values["retrieval_project_count"] += self._flag_any(text, RETRIEVAL_TERMS)
            values["ranking_project_count"] += self._flag_any(text, RANKING_TERMS)
            values["vector_project_count"] += self._flag_any(text, VECTOR_DB_TERMS)
            values["evaluation_project_count"] += self._flag_any(text, EVALUATION_TERMS)
            values["open_source_project_count"] += self._flag_any(text, OPEN_SOURCE_TERMS)
        return values

    def _language_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values = {
            "english_proficiency_score": 0.0,
            "professional_language_count": 0.0,
            "native_language_count": 0.0,
        }
        for item in candidate.languages:
            language = canonical(item.get("language"))
            proficiency = canonical(item.get("proficiency"))
            score = ENGLISH_PROFICIENCIES.get(proficiency, 0.0)
            if language == "english":
                values["english_proficiency_score"] = max(values["english_proficiency_score"], score)
            if proficiency in {"professional", "native"}:
                values["professional_language_count"] += 1.0
            if proficiency == "native":
                values["native_language_count"] += 1.0
        return values

    def _structured_signal_metrics(self, signals: dict[str, Any]) -> dict[str, float]:
        salary = signals.get("expected_salary_range_inr_lpa") if isinstance(signals.get("expected_salary_range_inr_lpa"), dict) else {}
        assessments = signals.get("skill_assessment_scores") if isinstance(signals.get("skill_assessment_scores"), dict) else {}
        assessment_values = [as_float(score, 0.0) for score in assessments.values()]
        relevant_assessments = [
            as_float(score, 0.0)
            for name, score in assessments.items()
            if any(term in canonical(name) for term in RELEVANT_ASSESSMENT_TERMS)
        ]
        work_mode = canonical(signals.get("preferred_work_mode"))
        return {
            "signup_age_days": self._days_since(signals.get("signup_date")),
            "expected_salary_min_lpa": as_float(salary.get("min"), 0.0),
            "expected_salary_max_lpa": as_float(salary.get("max"), 0.0),
            "expected_salary_mid_lpa": (as_float(salary.get("min"), 0.0) + as_float(salary.get("max"), 0.0)) / 2.0,
            "remote_work_preference_flag": 1.0 if work_mode == "remote" else 0.0,
            "hybrid_work_preference_flag": 1.0 if work_mode == "hybrid" else 0.0,
            "onsite_work_preference_flag": 1.0 if work_mode == "onsite" else 0.0,
            "flexible_work_preference_flag": 1.0 if work_mode == "flexible" else 0.0,
            "skill_assessment_count": float(len(assessment_values)),
            "avg_skill_assessment_score": (sum(assessment_values) / len(assessment_values) / 100.0) if assessment_values else 0.0,
            "max_skill_assessment_score": (max(assessment_values) / 100.0) if assessment_values else 0.0,
            "avg_relevant_skill_assessment_score": (sum(relevant_assessments) / len(relevant_assessments) / 100.0) if relevant_assessments else 0.0,
            "high_relevant_assessment_count": float(sum(1 for score in relevant_assessments if score >= 75.0)),
        }

    def _is_product_industry(self, value: Any) -> bool:
        industry = canonical(value)
        return any(term in industry for term in ("software", "internet", "saas", "ecommerce", "e commerce", "fintech", "healthtech", "edtech", "marketplace", "ai", "technology", "product"))

    def _months_between(self, start: datetime, end: datetime) -> int:
        if end < start:
            return 0
        return max(0, (end.year - start.year) * 12 + end.month - start.month)

    def _service_role_count(self, candidate: ParsedCandidate) -> int:
        count = 0
        for job in candidate.career_history:
            company = canonical(job.get("company"))
            industry = canonical(job.get("industry"))
            if any(service in company for service in SERVICE_COMPANIES) or "it services" in industry or "consulting" in industry:
                count += 1
        return count

    def _service_months(self, candidate: ParsedCandidate) -> float:
        months = 0.0
        for job in candidate.career_history:
            company = canonical(job.get("company"))
            industry = canonical(job.get("industry"))
            if any(service in company for service in SERVICE_COMPANIES) or "it services" in industry or "consulting" in industry:
                months += max(0, as_int(job.get("duration_months"), 0))
        return months

    def _product_company_months(self, candidate: ParsedCandidate) -> float:
        months = 0.0
        for job in candidate.career_history:
            if self._is_product_industry(job.get("industry")):
                months += max(0, as_int(job.get("duration_months"), 0))
        return months

    def _skill_metrics(self, candidate: ParsedCandidate) -> dict[str, float]:
        values: dict[str, float] = {}
        total_weight = 0.0
        total_endorsements = 0.0
        total_months = 0.0
        expert_count = 0
        advanced_count = 0
        zero_duration_expert_count = 0
        for skill in candidate.skills:
            name = canonical(skill.get("name"))
            proficiency = canonical(skill.get("proficiency"))
            weight = PROFICIENCY_WEIGHT.get(proficiency, 0.45)
            months = max(0, as_int(skill.get("duration_months"), 0))
            total_weight += weight
            total_months += months
            total_endorsements += max(0, as_float(skill.get("endorsements"), 0.0))
            if proficiency == "expert":
                expert_count += 1
                if months == 0:
                    zero_duration_expert_count += 1
            if proficiency == "advanced":
                advanced_count += 1
            for category, terms in SKILL_CATEGORY_TERMS_CANONICAL:
                if any(term in name for term in terms):
                    values[f"{category}_present"] = 1.0
                    values[f"{category}_weighted_proficiency"] = max(values.get(f"{category}_weighted_proficiency", 0.0), weight)
                    values[f"{category}_months"] = max(values.get(f"{category}_months", 0.0), float(months))
        values["avg_skill_proficiency_weight"] = total_weight / len(candidate.skills) if candidate.skills else 0.0
        values["total_skill_endorsements"] = total_endorsements
        values["avg_skill_duration_months"] = total_months / len(candidate.skills) if candidate.skills else 0.0
        values["expert_skill_count"] = float(expert_count)
        values["advanced_skill_count"] = float(advanced_count)
        values["zero_duration_expert_skill_count"] = float(zero_duration_expert_count)
        for category in ("skill_python", "skill_retrieval", "skill_ranking", "skill_recommendation", "skill_search", "skill_embeddings", "skill_vector_db", "skill_evaluation", "skill_llm_finetuning"):
            values.setdefault(f"{category}_present", 0.0)
            values.setdefault(f"{category}_weighted_proficiency", 0.0)
            values.setdefault(f"{category}_months", 0.0)
        return values

    def _fraction(self, value: Any, percent_scale: bool = False) -> float:
        number = as_float(value, 0.0)
        if percent_scale or number > 1.0:
            number /= 100.0
        return max(0.0, min(1.0, number))

    def _days_since(self, value: Any) -> float:
        parsed = parse_date(value)
        if not parsed:
            return 999.0
        return float(max(0, (REFERENCE_DATE - parsed.date()).days))
