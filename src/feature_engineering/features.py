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

        values["ai_months"] = self._months_for_terms(candidate, AI_TERMS)
        values["production_ai_months"] = self._months_for_terms(candidate, AI_TERMS + PRODUCTION_TERMS, require_any=AI_TERMS)
        values["retrieval_months"] = self._months_for_terms(candidate, RETRIEVAL_TERMS)
        values["ranking_months"] = self._months_for_terms(candidate, RANKING_TERMS)
        values["recommendation_months"] = self._months_for_terms(candidate, RECOMMENDATION_TERMS)
        values["search_months"] = self._months_for_terms(candidate, SEARCH_TERMS)
        values["embeddings_months"] = self._months_for_terms(candidate, EMBEDDING_TERMS)
        values["vector_db_months"] = self._months_for_terms(candidate, VECTOR_DB_TERMS)
        values["hybrid_search_months"] = self._months_for_terms(candidate, HYBRID_SEARCH_TERMS)
        values["evaluation_months"] = self._months_for_terms(candidate, EVALUATION_TERMS)
        values["research_months"] = self._months_for_terms(candidate, RESEARCH_TERMS)
        values["product_months"] = self._months_for_terms(candidate, PRODUCT_TERMS)
        values["startup_months"] = self._months_for_terms(candidate, STARTUP_TERMS)
        values["service_months"] = self._service_months(candidate)
        values["product_company_months"] = self._product_company_months(candidate)
        values["years_in_ai"] = values["ai_months"] / 12.0
        values["years_in_product_companies"] = values["product_company_months"] / 12.0
        values["years_in_service_companies"] = values["service_months"] / 12.0

        category_terms = {
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
        for name, terms in category_terms.items():
            values[f"{name}_profile_term_count"] = float(self._count_terms(profile_text, terms))
            values[f"{name}_career_term_count"] = float(self._count_terms(career_text, terms))
            values[f"{name}_skill_term_count"] = float(self._count_terms(skill_text, terms))
            values[f"{name}_all_term_count"] = float(self._count_terms(all_text, terms))
            values[f"has_{name}"] = 1.0 if values[f"{name}_all_term_count"] > 0 else 0.0
            evidence[name] = self._matched_terms(all_text, terms)[:8]

        for term in TERM_FLAG_BANK:
            key = canonical(term).replace(" ", "_").replace("/", "_").replace("-", "_").replace("+", "plus").replace(".", "")
            values[f"term_flag_{key}"] = 1.0 if canonical(term) in all_text else 0.0

        skill_metrics = self._skill_metrics(candidate)
        values.update(skill_metrics)

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
        return sum(1 for term in terms if canonical(term) in text)

    def _matched_terms(self, text: str, terms: tuple[str, ...]) -> list[str]:
        return [term for term in terms if canonical(term) in text]

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
        positive = ("software", "internet", "saas", "ecommerce", "e commerce", "fintech", "healthtech", "edtech", "marketplace", "ai", "technology", "product")
        months = 0.0
        for job in candidate.career_history:
            industry = canonical(job.get("industry"))
            if any(term in industry for term in positive):
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
            for category, terms in (
                ("skill_python", PYTHON_TERMS),
                ("skill_retrieval", RETRIEVAL_TERMS),
                ("skill_ranking", RANKING_TERMS),
                ("skill_recommendation", RECOMMENDATION_TERMS),
                ("skill_search", SEARCH_TERMS),
                ("skill_embeddings", EMBEDDING_TERMS),
                ("skill_vector_db", VECTOR_DB_TERMS),
                ("skill_evaluation", EVALUATION_TERMS),
                ("skill_llm_finetuning", ("fine tuning", "fine-tuning", "lora", "qlora", "peft", "transformers")),
            ):
                if any(canonical(term) in name for term in terms):
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
