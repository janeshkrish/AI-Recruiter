"""
Agent 6 — Recruiter Reasoning Agent
=====================================

LLM-based holistic candidate evaluation. Runs ONLY on the top candidates
after initial filtering stages. Uses GPT-4.1 or DeepSeek V3 to evaluate
candidates the way a senior recruiter would.

Evaluates:
1. Technical Fit
2. Career Trajectory
3. Learning Ability
4. Startup Fit
5. Hiring Probability
6. Leadership Potential

Returns: { "score": float, "reasoning": str }
"""

from __future__ import annotations

import json
import random
from typing import Optional

from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from recruiter_brain.config import get_settings
from recruiter_brain.data.models import (
    AgentScores,
    CandidateProfile,
    RoleParsedOutput,
)


RECRUITER_SYSTEM_PROMPT = """You are a senior technical recruiter with 15+ years of experience
at top-tier technology companies (Google, Meta, Stripe). You have an exceptional track record
of identifying top talent and predicting hiring success.

Evaluate candidates holistically, considering not just skill match but career trajectory,
growth potential, cultural fit, and hiring probability.

Return your evaluation as a JSON object ONLY. No additional text."""


EVALUATION_PROMPT = """Evaluate this candidate for the following role:

## JOB: {job_title}
{job_description}

## CANDIDATE: {candidate_name}
**Current Role:** {current_title} at {current_company}
**Experience:** {experience_years} years
**Headline:** {headline}

**Summary:** {summary}

**Skills:** {skills}

**Career History:**
{career_history}

**Education:**
{education}

**Certifications:** {certifications}

**Prior Agent Scores:**
- Technical Fit: {technical_score:.2f}/1.0
- Career Fit: {career_score:.2f}/1.0
- Behavioral Fit: {behavioral_score:.2f}/1.0
- Potential Score: {potential_score:.2f}/1.0

## YOUR EVALUATION

Evaluate on these dimensions (score each 0.0-1.0):
1. Technical Fit — Does the candidate have the right skills and depth?
2. Career Trajectory — Is the candidate on an upward path?
3. Learning Ability — Can they quickly acquire missing skills?
4. Startup Fit — Will they thrive in a fast-paced environment?
5. Hiring Probability — How likely are they to accept an offer?
6. Leadership Potential — Can they grow into leadership?

Return JSON:
{{
    "technical_fit": <0.0-1.0>,
    "career_trajectory": <0.0-1.0>,
    "learning_ability": <0.0-1.0>,
    "startup_fit": <0.0-1.0>,
    "hiring_probability": <0.0-1.0>,
    "leadership_potential": <0.0-1.0>,
    "overall_score": <0.0-1.0>,
    "reasoning": "<2-3 sentence explanation of your assessment>",
    "top_strengths": ["<strength1>", "<strength2>"],
    "key_risks": ["<risk1>", "<risk2>"],
    "recommendation": "<strong_hire | hire | maybe | pass>"
}}
"""


class RecruiterReasoningAgent:
    """
    Agent 6: LLM-based holistic candidate evaluation.

    Supports:
    - OpenAI GPT-4.1 (primary)
    - DeepSeek V3 (fallback)
    - Simulation mode (generates plausible scores without API calls)
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self._cache: dict[str, dict] = {}
        logger.info("RecruiterReasoningAgent initialized")

    async def evaluate(
        self,
        candidate: CandidateProfile,
        jd_title: str,
        jd_text: str,
        parsed_role: RoleParsedOutput,
        prior_scores: AgentScores,
    ) -> dict:
        """
        Evaluate a single candidate using LLM reasoning.

        Args:
            candidate: The candidate profile.
            jd_title: Job title.
            jd_text: Full job description text.
            parsed_role: Parsed role requirements.
            prior_scores: Scores from Agents 2-5.

        Returns:
            Dict with score, reasoning, and detailed evaluation.
        """
        cache_key = f"{candidate.candidate_id}_{hash(jd_text)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.settings.llm.simulation_mode:
            result = self._simulate_evaluation(candidate, prior_scores)
        else:
            result = await self._llm_evaluate(
                candidate, jd_title, jd_text, parsed_role, prior_scores
            )

        self._cache[cache_key] = result
        return result

    async def evaluate_batch(
        self,
        candidates: list[CandidateProfile],
        jd_title: str,
        jd_text: str,
        parsed_role: RoleParsedOutput,
        prior_scores_list: list[AgentScores],
    ) -> list[dict]:
        """
        Evaluate multiple candidates.

        Args:
            candidates: List of candidate profiles.
            jd_title: Job title.
            jd_text: Full job description text.
            parsed_role: Parsed role requirements.
            prior_scores_list: List of prior agent scores.

        Returns:
            List of evaluation dicts.
        """
        results = []
        for candidate, scores in zip(candidates, prior_scores_list):
            result = await self.evaluate(
                candidate, jd_title, jd_text, parsed_role, scores
            )
            results.append(result)
        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((Exception,)),
    )
    async def _llm_evaluate(
        self,
        candidate: CandidateProfile,
        jd_title: str,
        jd_text: str,
        parsed_role: RoleParsedOutput,
        prior_scores: AgentScores,
    ) -> dict:
        """Call LLM API for evaluation."""
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

        # Format career history
        career_text = "\n".join(
            f"  - {e.title} at {e.company} ({e.duration_months}mo, {e.industry})"
            for e in candidate.career_history[-5:]  # Last 5 roles
        )

        # Format education
        edu_text = ", ".join(
            f"{e.degree} {e.field} from {e.institution}"
            for e in candidate.education
        )

        # Format certifications
        cert_text = ", ".join(
            c.name for c in candidate.certifications
        ) or "None"

        prompt = EVALUATION_PROMPT.format(
            job_title=jd_title,
            job_description=jd_text[:2000],
            candidate_name=candidate.name,
            current_title=candidate.current_title,
            current_company=candidate.current_company,
            experience_years=candidate.total_experience_years,
            headline=candidate.headline,
            summary=candidate.summary[:500],
            skills=", ".join(candidate.skills[:20]),
            career_history=career_text,
            education=edu_text,
            certifications=cert_text,
            technical_score=prior_scores.technical_fit_score,
            career_score=prior_scores.career_fit_score,
            behavioral_score=prior_scores.behavioral_fit_score,
            potential_score=prior_scores.potential_score,
        )

        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": RECRUITER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content
        data = json.loads(raw)

        return {
            "score": float(data.get("overall_score", 0.5)),
            "reasoning": data.get("reasoning", ""),
            "technical_fit": float(data.get("technical_fit", 0.5)),
            "career_trajectory": float(data.get("career_trajectory", 0.5)),
            "learning_ability": float(data.get("learning_ability", 0.5)),
            "startup_fit": float(data.get("startup_fit", 0.5)),
            "hiring_probability": float(data.get("hiring_probability", 0.5)),
            "leadership_potential": float(data.get("leadership_potential", 0.5)),
            "top_strengths": data.get("top_strengths", []),
            "key_risks": data.get("key_risks", []),
            "recommendation": data.get("recommendation", "maybe"),
        }

    def _simulate_evaluation(
        self,
        candidate: CandidateProfile,
        prior_scores: AgentScores,
    ) -> dict:
        """
        Generate plausible evaluation without LLM API call.

        Uses prior agent scores plus heuristics to simulate recruiter reasoning.
        """
        # Base score from prior agents
        base = (
            prior_scores.technical_fit_score * 0.3
            + prior_scores.career_fit_score * 0.25
            + prior_scores.behavioral_fit_score * 0.2
            + prior_scores.potential_score * 0.25
        )

        # Add some variability
        noise = random.gauss(0, 0.05)
        overall = max(0.0, min(1.0, base + noise))

        # Heuristic sub-scores
        tech_fit = min(1.0, prior_scores.technical_fit_score + random.gauss(0, 0.05))
        career_traj = min(1.0, prior_scores.career_fit_score + random.gauss(0, 0.05))
        learning = min(1.0, prior_scores.potential_score * 0.8 + random.gauss(0.1, 0.05))
        startup = min(1.0, max(0.0, random.gauss(0.5, 0.15)))
        hiring_prob = min(1.0, prior_scores.behavioral_fit_score * 0.7 + random.gauss(0.2, 0.1))
        leadership = min(1.0, max(0.0, prior_scores.career_fit_score * 0.5 + random.gauss(0.2, 0.1)))

        # Generate reasoning
        strengths = []
        risks = []

        if prior_scores.technical_fit_score > 0.7:
            strengths.append("Strong technical skill alignment")
        if prior_scores.career_fit_score > 0.7:
            strengths.append("Excellent career progression")
        if prior_scores.potential_score > 0.7:
            strengths.append("High growth potential with transferable skills")
        if prior_scores.behavioral_fit_score > 0.7:
            strengths.append("Highly engaged and responsive candidate")
        if candidate.total_experience_years > 8:
            strengths.append("Deep industry experience")

        if prior_scores.technical_fit_score < 0.4:
            risks.append("Significant skill gaps in core requirements")
        if prior_scores.career_fit_score < 0.4:
            risks.append("Career trajectory concerns")
        if prior_scores.behavioral_fit_score < 0.3:
            risks.append("Low platform engagement may indicate passive interest")
        if candidate.total_experience_years < 2:
            risks.append("Limited professional experience")

        if not strengths:
            strengths = ["Adequate overall profile"]
        if not risks:
            risks = ["No major concerns identified"]

        # Recommendation
        if overall >= 0.75:
            recommendation = "strong_hire"
        elif overall >= 0.55:
            recommendation = "hire"
        elif overall >= 0.4:
            recommendation = "maybe"
        else:
            recommendation = "pass"

        reasoning = (
            f"Candidate shows {'strong' if overall > 0.65 else 'moderate' if overall > 0.4 else 'limited'} "
            f"alignment with the role. "
            f"{'Excellent' if tech_fit > 0.7 else 'Adequate' if tech_fit > 0.4 else 'Weak'} technical fit "
            f"with {'promising' if career_traj > 0.6 else 'average'} career trajectory. "
            f"{'High' if learning > 0.7 else 'Moderate'} learning potential."
        )

        return {
            "score": round(max(0.0, min(1.0, overall)), 4),
            "reasoning": reasoning,
            "technical_fit": round(max(0.0, min(1.0, tech_fit)), 4),
            "career_trajectory": round(max(0.0, min(1.0, career_traj)), 4),
            "learning_ability": round(max(0.0, min(1.0, learning)), 4),
            "startup_fit": round(max(0.0, min(1.0, startup)), 4),
            "hiring_probability": round(max(0.0, min(1.0, hiring_prob)), 4),
            "leadership_potential": round(max(0.0, min(1.0, leadership)), 4),
            "top_strengths": strengths[:3],
            "key_risks": risks[:3],
            "recommendation": recommendation,
        }
