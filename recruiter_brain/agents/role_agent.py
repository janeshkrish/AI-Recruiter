"""
Agent 1 — Role Understanding Agent
====================================

Extracts structured requirements from a raw job description using
LLM-based parsing (GPT-4.1 / DeepSeek) with regex-based fallback.

Output:
    RoleParsedOutput with must_have_skills, nice_to_have_skills,
    seniority, years_experience, leadership, startup_mindset,
    research_orientation, product_thinking.
"""

from __future__ import annotations

import json
import re
from typing import Optional

from loguru import logger

from recruiter_brain.config import get_settings
from recruiter_brain.data.models import RoleParsedOutput


# ---------------------------------------------------------------------------
# LLM Extraction Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert technical recruiter and job description analyst.
Given a job description, extract structured information about the role requirements.
Return ONLY valid JSON matching the specified schema. No additional text."""

EXTRACTION_PROMPT = """Analyze the following job description and extract:

1. must_have_skills: Required technical skills and tools (list of strings)
2. nice_to_have_skills: Preferred/optional skills (list of strings)
3. seniority: One of: intern, junior, mid, senior, staff, principal, lead, manager, director, vp
4. years_experience: Required years as a string like "5+" or "3-5"
5. leadership: Score 0.0-1.0 indicating leadership requirements (0=IC, 1=heavy leadership)
6. startup_mindset: Score 0.0-1.0 indicating startup culture fit importance
7. research_orientation: Score 0.0-1.0 indicating research/academic orientation
8. product_thinking: Score 0.0-1.0 indicating product ownership expectations
9. domain_expertise: List of domain areas (e.g., "fintech", "healthcare")
10. behavioral_expectations: List of soft skill / behavioral requirements
11. target_industry: Primary industry for the role

Return JSON only:
{{
    "must_have_skills": [],
    "nice_to_have_skills": [],
    "seniority": "",
    "years_experience": "",
    "leadership": 0.0,
    "startup_mindset": 0.0,
    "research_orientation": 0.0,
    "product_thinking": 0.0,
    "domain_expertise": [],
    "behavioral_expectations": [],
    "target_industry": ""
}}

Job Description:
{job_description}
"""


class RoleUnderstandingAgent:
    """
    Agent 1: Parses a job description into structured role requirements.

    Supports:
    - OpenAI GPT-4.1 (primary)
    - DeepSeek V3 (fallback)
    - Regex-based extraction (offline fallback)
    - Simulation mode (no API keys needed)
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, RoleParsedOutput] = {}
        logger.info("RoleUnderstandingAgent initialized")

    async def parse(self, job_description: str) -> RoleParsedOutput:
        """
        Parse a job description into structured requirements.

        Args:
            job_description: Raw job description text.

        Returns:
            RoleParsedOutput with extracted requirements.
        """
        # Check cache
        cache_key = hash(job_description)
        if cache_key in self._cache:
            logger.info("Returning cached JD parse result")
            return self._cache[cache_key]

        if self.settings.llm.simulation_mode:
            logger.info("Running in simulation mode — using regex extraction")
            result = self._regex_extract(job_description)
        else:
            try:
                result = await self._llm_extract(job_description)
            except Exception as e:
                logger.warning(f"LLM extraction failed: {e}. Falling back to regex.")
                result = self._regex_extract(job_description)

        self._cache[cache_key] = result
        logger.info(f"Parsed JD → {len(result.must_have_skills)} must-have, "
                     f"{len(result.nice_to_have_skills)} nice-to-have skills")
        return result

    async def _llm_extract(self, job_description: str) -> RoleParsedOutput:
        """Extract using LLM API call."""
        from openai import AsyncOpenAI

        cfg = self.settings.llm

        if cfg.provider == "deepseek":
            client = AsyncOpenAI(
                api_key=cfg.deepseek_api_key,
                base_url=cfg.deepseek_base_url,
            )
            model = cfg.deepseek_model
        else:
            client = AsyncOpenAI(api_key=cfg.openai_api_key)
            model = cfg.openai_model

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT.format(
                        job_description=job_description
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)
        return RoleParsedOutput.model_validate(data)

    def _regex_extract(self, job_description: str) -> RoleParsedOutput:
        """Fallback regex-based extraction for offline mode."""
        text = job_description.lower()

        # --- Skills extraction ---
        # Common tech skill patterns
        from recruiter_brain.data.generate_synthetic_data import TECH_SKILLS

        skill_set_lower = {s.lower(): s for s in TECH_SKILLS}
        found_skills = []
        for skill_lower, skill_original in skill_set_lower.items():
            if skill_lower in text:
                found_skills.append(skill_original)

        # Split into must-have vs nice-to-have based on section
        must_have = []
        nice_to_have = []

        # Find sections
        must_patterns = [
            r"(?:requirements?|must[- ]have|required|qualifications?)[\s:]*\n(.*?)(?=\n\s*(?:preferred|nice|about|$))",
        ]
        nice_patterns = [
            r"(?:preferred|nice[- ]to[- ]have|bonus|optional)[\s:]*\n(.*?)(?=\n\s*(?:about|$))",
        ]

        must_section = ""
        for pat in must_patterns:
            m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if m:
                must_section = m.group(1)
                break

        nice_section = ""
        for pat in nice_patterns:
            m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if m:
                nice_section = m.group(1)
                break

        for skill in found_skills:
            if skill.lower() in nice_section:
                nice_to_have.append(skill)
            else:
                must_have.append(skill)

        if not must_have and found_skills:
            # If no section parsing worked, split 70/30
            split = int(len(found_skills) * 0.7)
            must_have = found_skills[:split]
            nice_to_have = found_skills[split:]

        # --- Seniority ---
        seniority = "mid"
        seniority_map = {
            "intern": "intern", "junior": "junior", "entry": "junior",
            "mid": "mid", "senior": "senior", "staff": "staff",
            "principal": "principal", "lead": "lead",
            "manager": "manager", "director": "director",
            "vp": "vp", "vice president": "vp", "c-level": "c_level",
            "cto": "c_level", "head of": "director",
        }
        for keyword, level in seniority_map.items():
            if keyword in text:
                seniority = level
                break

        # --- Years experience ---
        years_exp = ""
        years_match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", text)
        if years_match:
            years_exp = f"{years_match.group(1)}+"

        # --- Scores ---
        leadership = 0.2
        if any(w in text for w in ["lead", "mentor", "manage", "team"]):
            leadership = 0.6
        if any(w in text for w in ["director", "vp", "head of", "leading"]):
            leadership = 0.9

        startup_mindset = 0.3
        if any(w in text for w in ["startup", "fast-paced", "scrappy", "agile"]):
            startup_mindset = 0.8

        research = 0.2
        if any(w in text for w in ["research", "publish", "paper", "phd", "novel"]):
            research = 0.7

        product = 0.3
        if any(w in text for w in ["product", "user", "customer", "feature", "ship"]):
            product = 0.7

        # --- Domain ---
        domains = []
        domain_keywords = {
            "fintech": ["fintech", "financial", "banking", "payment"],
            "healthcare": ["health", "medical", "clinical", "biotech"],
            "e-commerce": ["e-commerce", "ecommerce", "retail", "shopping"],
            "security": ["security", "cyber", "threat", "compliance"],
            "media": ["media", "entertainment", "content", "streaming"],
            "education": ["education", "learning", "edtech"],
        }
        for domain, keywords in domain_keywords.items():
            if any(k in text for k in keywords):
                domains.append(domain)

        # --- Behavioral ---
        behavioral = []
        if "communicat" in text:
            behavioral.append("strong communication")
        if "collaborat" in text:
            behavioral.append("collaborative")
        if "independent" in text or "autonomous" in text:
            behavioral.append("self-directed")
        if "mentor" in text:
            behavioral.append("mentorship")
        if "owner" in text or "ownership" in text:
            behavioral.append("ownership mindset")

        return RoleParsedOutput(
            must_have_skills=must_have,
            nice_to_have_skills=nice_to_have,
            seniority=seniority,
            years_experience=years_exp,
            leadership=round(leadership, 2),
            startup_mindset=round(startup_mindset, 2),
            research_orientation=round(research, 2),
            product_thinking=round(product, 2),
            domain_expertise=domains,
            behavioral_expectations=behavioral,
            target_industry=domains[0] if domains else "",
        )
