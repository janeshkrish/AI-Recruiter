"""
AI Recruiter Brain — Synthetic Data Generator
===============================================

Generates ~100K realistic candidate profiles with all required fields:
career history, skills, certifications, education, behavioral signals,
platform metrics, and recruiter interaction data.

Usage:
    python -m recruiter_brain.data.generate_synthetic_data
"""

from __future__ import annotations

import json
import os
import random
import uuid
from pathlib import Path
from typing import Any

from loguru import logger
from tqdm import tqdm

from recruiter_brain.data.models import (
    BehavioralSignals,
    CandidateProfile,
    CareerEntry,
    Certification,
    Education,
    EmploymentType,
    JobDescription,
    Seniority,
)

# ---------------------------------------------------------------------------
# Taxonomy Data
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Dorothy", "Andrew",
    "Kimberly", "Paul", "Emily", "Joshua", "Donna", "Kenneth", "Michelle",
    "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Timothy",
    "Deborah", "Arun", "Priya", "Wei", "Mei", "Hiroshi", "Yuki", "Ahmed",
    "Fatima", "Carlos", "Maria", "Olga", "Dmitri", "Sanjay", "Deepa",
    "Raj", "Ananya", "Chen", "Li", "Takeshi", "Sakura", "Omar", "Layla",
    "Pedro", "Isabella", "Ivan", "Natasha", "Vikram", "Neha", "Jin", "Hana",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Patel", "Kumar", "Singh", "Sharma", "Gupta",
    "Chen", "Wang", "Zhang", "Liu", "Yang", "Kim", "Park", "Choi",
    "Tanaka", "Sato", "Suzuki", "Müller", "Schmidt", "Fischer", "Weber",
    "Ivanov", "Petrov", "Volkov", "Al-Hassan", "Mohammed", "Ali", "Silva",
    "Santos", "Oliveira", "Costa", "Fernandez", "Morales",
]

TECH_SKILLS = [
    # Programming Languages
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
    "Ruby", "Scala", "Kotlin", "Swift", "R", "Julia", "Perl", "PHP",
    "Elixir", "Haskell", "Clojure", "Lua",
    # ML/AI
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "Reinforcement Learning", "PyTorch", "TensorFlow", "scikit-learn",
    "Hugging Face Transformers", "LLM Engineering", "Prompt Engineering",
    "RAG Systems", "Fine-tuning", "RLHF", "MLOps", "Feature Engineering",
    "Model Optimization", "Neural Architecture Search", "GANs",
    "Diffusion Models", "LangChain", "LlamaIndex",
    # Data
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Apache Spark", "Apache Kafka", "Apache Airflow", "dbt",
    "Data Engineering", "Data Warehousing", "ETL Pipelines",
    "Data Modeling", "Snowflake", "BigQuery", "Redshift",
    "Apache Flink", "Delta Lake", "Data Governance",
    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform",
    "CI/CD", "Jenkins", "GitHub Actions", "ArgoCD", "Prometheus",
    "Grafana", "Linux", "Nginx", "Ansible", "Pulumi",
    "Serverless", "CloudFormation", "Helm",
    # Frontend
    "React", "Angular", "Vue.js", "Next.js", "Svelte", "HTML/CSS",
    "Tailwind CSS", "GraphQL", "REST APIs", "WebSockets",
    "React Native", "Flutter", "Figma",
    # Backend
    "Node.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "Express.js", "gRPC", "Microservices", "Event-Driven Architecture",
    "Domain-Driven Design", "CQRS",
    # Security
    "Cybersecurity", "OAuth", "JWT", "Encryption", "Penetration Testing",
    "SOC 2", "GDPR Compliance",
    # Other
    "Agile", "Scrum", "System Design", "Technical Writing",
    "API Design", "Performance Optimization", "Distributed Systems",
    "Blockchain", "IoT", "Edge Computing", "WebAssembly",
    "Vector Databases", "Qdrant", "Pinecone", "Weaviate",
]

INDUSTRIES = [
    "Technology", "Finance", "Healthcare", "E-commerce", "Education",
    "Media & Entertainment", "Cybersecurity", "Automotive", "Aerospace",
    "Telecommunications", "Energy", "Retail", "Gaming", "Social Media",
    "SaaS", "Consulting", "Insurance", "Real Estate", "Logistics",
    "Agriculture Tech", "Legal Tech", "HR Tech", "Climate Tech",
    "Biotech", "Robotics", "Defense",
]

COMPANIES_BY_TIER = {
    1: [  # Top-tier
        "Google", "Apple", "Microsoft", "Amazon", "Meta", "Netflix",
        "OpenAI", "DeepMind", "Anthropic", "Tesla", "NVIDIA", "Stripe",
        "Databricks", "Snowflake", "Palantir", "Coinbase", "Figma",
        "Vercel", "Notion", "Linear",
    ],
    2: [  # Well-known
        "Uber", "Lyft", "Airbnb", "Spotify", "Shopify", "Twilio",
        "Datadog", "MongoDB Inc", "Confluent", "HashiCorp", "Elastic",
        "Cloudflare", "DigitalOcean", "Atlassian", "HubSpot",
        "Square", "Robinhood", "Instacart", "DoorDash", "Snap",
        "Pinterest", "Reddit", "Zoom", "Slack", "Asana",
        "Canva", "GitLab", "Grafana Labs", "Supabase", "PlanetScale",
    ],
    3: [  # Other / Startups
        "DataPipe Inc", "CloudScale AI", "NeuralFlow", "QuantumLeap",
        "ByteForge", "CodeCraft", "InnoTech Solutions", "VectorAI",
        "StreamLine Data", "CoreLogic Tech", "BrightPath", "NexGen Labs",
        "Synaptic AI", "FusionWare", "AlphaMetrics", "DeepVerse",
        "CipherTech", "NovaStack", "Aether Systems", "PrimeLabs",
        "Zenith Software", "ArcLight", "TerraForm AI", "OmniCore",
        "PulsePoint", "EdgeWorks", "Stratify", "Luminos AI",
        "Meridian Tech", "ApexData", "CatalystML", "Helix Solutions",
        "BlueRidge Analytics", "IronClad Systems", "SwiftScale",
        "TitanOps", "OrionAI", "Phoenix Cloud", "Atlas Engineering",
        "Summit Digital", "Horizon Labs", "Vertex Solutions",
    ],
}

TITLES_BY_SENIORITY = {
    Seniority.INTERN: ["Software Engineering Intern", "Data Science Intern",
                       "ML Intern", "Research Intern"],
    Seniority.JUNIOR: ["Junior Software Engineer", "Junior Data Scientist",
                       "Associate Developer", "Software Engineer I",
                       "Junior ML Engineer"],
    Seniority.MID: ["Software Engineer", "Data Scientist", "ML Engineer",
                    "Backend Engineer", "Frontend Engineer",
                    "Full Stack Engineer", "Data Engineer",
                    "DevOps Engineer", "Platform Engineer",
                    "Software Engineer II"],
    Seniority.SENIOR: ["Senior Software Engineer", "Senior Data Scientist",
                       "Senior ML Engineer", "Senior Backend Engineer",
                       "Senior Platform Engineer", "Senior Data Engineer",
                       "Senior DevOps Engineer", "Tech Lead",
                       "Senior Full Stack Engineer"],
    Seniority.STAFF: ["Staff Engineer", "Staff ML Engineer",
                      "Staff Data Scientist", "Staff Platform Engineer"],
    Seniority.PRINCIPAL: ["Principal Engineer", "Principal Architect",
                          "Principal Data Scientist", "Distinguished Engineer"],
    Seniority.LEAD: ["Engineering Lead", "Team Lead", "Technical Lead",
                     "ML Team Lead", "Data Science Lead"],
    Seniority.MANAGER: ["Engineering Manager", "Data Science Manager",
                        "ML Engineering Manager", "Platform Manager"],
    Seniority.DIRECTOR: ["Director of Engineering", "Director of Data Science",
                         "Director of ML", "Director of Platform"],
    Seniority.VP: ["VP of Engineering", "VP of Data", "VP of AI/ML",
                   "VP of Technology", "CTO"],
}

SENIORITY_PROGRESSION = [
    Seniority.INTERN, Seniority.JUNIOR, Seniority.MID, Seniority.SENIOR,
    Seniority.STAFF, Seniority.LEAD, Seniority.MANAGER,
    Seniority.DIRECTOR, Seniority.VP,
]

UNIVERSITIES_BY_TIER = {
    1: ["MIT", "Stanford University", "Carnegie Mellon University",
        "UC Berkeley", "Caltech", "Harvard University", "Princeton University",
        "University of Cambridge", "University of Oxford", "ETH Zurich",
        "Georgia Tech", "University of Illinois", "IIT Bombay", "IIT Delhi",
        "Tsinghua University", "NUS Singapore"],
    2: ["University of Michigan", "University of Washington", "UCLA",
        "Columbia University", "Cornell University", "University of Texas",
        "Purdue University", "USC", "NYU", "University of Toronto",
        "University of Waterloo", "BITS Pilani", "IIT Madras",
        "Peking University", "NTU Singapore", "University of Edinburgh"],
    3: ["State University", "City College", "Regional Institute of Technology",
        "National University", "Technical University", "Polytechnic Institute",
        "Community College of Technology", "Metropolitan University",
        "Provincial University", "Federal University of Technology"],
}

DEGREES = ["BS", "MS", "PhD", "MBA", "BE", "BTech", "MTech", "MEng"]
FIELDS = [
    "Computer Science", "Software Engineering", "Data Science",
    "Electrical Engineering", "Mathematics", "Statistics",
    "Information Technology", "Artificial Intelligence",
    "Machine Learning", "Physics", "Operations Research",
    "Computational Linguistics", "Bioinformatics",
]

CERTIFICATIONS_LIST = [
    ("AWS Solutions Architect", "Amazon Web Services"),
    ("AWS Machine Learning Specialty", "Amazon Web Services"),
    ("Google Cloud Professional ML Engineer", "Google Cloud"),
    ("Google Cloud Professional Data Engineer", "Google Cloud"),
    ("Azure AI Engineer Associate", "Microsoft"),
    ("Azure Data Scientist Associate", "Microsoft"),
    ("Certified Kubernetes Administrator", "CNCF"),
    ("Terraform Associate", "HashiCorp"),
    ("TensorFlow Developer Certificate", "Google"),
    ("Deep Learning Specialization", "Coursera/DeepLearning.AI"),
    ("Professional Scrum Master", "Scrum.org"),
    ("PMP", "PMI"),
    ("Databricks Certified ML Professional", "Databricks"),
    ("Snowflake SnowPro Core", "Snowflake"),
    ("MongoDB Developer", "MongoDB"),
    ("Confluent Certified Developer", "Confluent"),
    ("CISSP", "ISC²"),
    ("CompTIA Security+", "CompTIA"),
]

PROJECT_TEMPLATES = [
    "Built {tech} pipeline processing {volume} events/day for {domain}",
    "Designed and deployed {tech} system achieving {metric} improvement",
    "Led migration from {old_tech} to {tech} serving {scale} users",
    "Developed {tech}-based recommendation engine for {domain} platform",
    "Implemented real-time {tech} analytics dashboard for {domain}",
    "Created {tech} microservices architecture handling {scale} RPS",
    "Built end-to-end {tech} ML pipeline with {metric} accuracy",
    "Architected {tech} data lake on {cloud} for {domain} analytics",
    "Developed {tech} API gateway with {metric} latency reduction",
    "Designed {tech} monitoring system tracking {scale} metrics",
]


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def _weighted_choice(options: list, weights: list[float]) -> Any:
    """Weighted random selection."""
    return random.choices(options, weights=weights, k=1)[0]


def _generate_career(
    experience_years: float, target_seniority_idx: int
) -> list[CareerEntry]:
    """Generate a realistic career progression."""
    entries: list[CareerEntry] = []
    remaining_months = int(experience_years * 12)
    current_year = 2024
    current_month = 6

    # Determine number of positions (2-6)
    num_positions = min(
        random.randint(2, 6),
        max(2, int(experience_years / 1.5)),
    )

    # Create seniority progression
    start_idx = max(0, target_seniority_idx - num_positions + 1)
    seniority_levels = []
    for i in range(num_positions):
        idx = min(start_idx + i, len(SENIORITY_PROGRESSION) - 1)
        seniority_levels.append(SENIORITY_PROGRESSION[idx])

    for i in range(num_positions):
        if remaining_months <= 0:
            break

        seniority = seniority_levels[i]

        # Duration: 12-48 months, last role gets remaining
        if i == num_positions - 1:
            duration = remaining_months
        else:
            duration = random.randint(12, min(48, remaining_months - 6))

        # Calculate start/end dates
        end_year = current_year
        end_month = current_month
        total_start_month = (end_year * 12 + end_month) - duration
        start_year = total_start_month // 12
        start_month = total_start_month % 12 or 12

        # Pick company tier (higher seniority → higher chance of good company)
        tier_weights = {
            Seniority.INTERN: [0.1, 0.3, 0.6],
            Seniority.JUNIOR: [0.15, 0.3, 0.55],
            Seniority.MID: [0.2, 0.35, 0.45],
            Seniority.SENIOR: [0.3, 0.35, 0.35],
            Seniority.STAFF: [0.4, 0.35, 0.25],
            Seniority.PRINCIPAL: [0.45, 0.35, 0.2],
            Seniority.LEAD: [0.3, 0.4, 0.3],
            Seniority.MANAGER: [0.35, 0.35, 0.3],
            Seniority.DIRECTOR: [0.4, 0.35, 0.25],
            Seniority.VP: [0.45, 0.35, 0.2],
        }
        tier = _weighted_choice([1, 2, 3], tier_weights.get(seniority, [0.2, 0.3, 0.5]))
        company = random.choice(COMPANIES_BY_TIER[tier])
        title = random.choice(TITLES_BY_SENIORITY.get(seniority, ["Engineer"]))
        industry = random.choice(INDUSTRIES)

        is_current = (i == num_positions - 1)

        entry = CareerEntry(
            company=company,
            title=title,
            seniority_level=seniority,
            start_date=f"{start_year}-{start_month:02d}",
            end_date=None if is_current else f"{end_year}-{end_month:02d}",
            duration_months=duration,
            industry=industry,
            description=f"{title} working on {random.choice(['backend', 'frontend', 'ML', 'data', 'platform', 'infrastructure'])} systems",
            is_leadership=seniority in (
                Seniority.LEAD, Seniority.MANAGER,
                Seniority.DIRECTOR, Seniority.VP,
            ),
            company_size=random.choice(["startup", "mid", "enterprise"]),
            company_tier=tier,
        )
        entries.append(entry)

        remaining_months -= duration
        current_year = start_year
        current_month = start_month

    entries.reverse()  # Chronological order (oldest first)
    return entries


def _generate_skills(seniority_idx: int) -> list[str]:
    """Generate a skill set sized by seniority."""
    base_count = random.randint(5, 10)
    bonus = min(seniority_idx * 2, 15)
    count = base_count + bonus
    return random.sample(TECH_SKILLS, min(count, len(TECH_SKILLS)))


def _generate_certifications() -> list[Certification]:
    """Generate 0-5 certifications."""
    count = _weighted_choice([0, 1, 2, 3, 4, 5], [0.25, 0.3, 0.2, 0.15, 0.07, 0.03])
    chosen = random.sample(
        CERTIFICATIONS_LIST, min(count, len(CERTIFICATIONS_LIST))
    )
    return [
        Certification(
            name=name,
            issuer=issuer,
            year=random.randint(2018, 2024),
            relevance_score=round(random.uniform(0.3, 1.0), 2),
        )
        for name, issuer in chosen
    ]


def _generate_education(seniority_idx: int) -> list[Education]:
    """Generate education entries."""
    entries = []
    # Undergraduate
    tier = _weighted_choice([1, 2, 3], [0.15, 0.35, 0.5])
    uni = random.choice(UNIVERSITIES_BY_TIER[tier])
    degree = random.choice(["BS", "BE", "BTech"])
    field = random.choice(FIELDS)
    grad_year = 2024 - int(random.uniform(2, 20))
    entries.append(Education(
        institution=uni,
        degree=degree,
        field=field,
        graduation_year=grad_year,
        gpa=round(random.uniform(2.8, 4.0), 2),
        tier=tier,
    ))

    # Graduate degree (higher chance for senior people)
    grad_prob = min(0.2 + seniority_idx * 0.08, 0.7)
    if random.random() < grad_prob:
        tier = _weighted_choice([1, 2, 3], [0.2, 0.4, 0.4])
        uni = random.choice(UNIVERSITIES_BY_TIER[tier])
        degree = random.choice(["MS", "MTech", "MEng", "PhD", "MBA"])
        entries.append(Education(
            institution=uni,
            degree=degree,
            field=random.choice(FIELDS),
            graduation_year=grad_year + random.randint(2, 4),
            gpa=round(random.uniform(3.2, 4.0), 2) if random.random() > 0.3 else None,
            tier=tier,
        ))

    return entries


def _generate_behavioral() -> BehavioralSignals:
    """Generate behavioral signals with realistic distributions."""
    # Profile completeness clusters around 0.6-0.9
    completeness = min(1.0, max(0.1, random.gauss(0.75, 0.15)))
    # Response rate correlates with engagement
    base_engagement = random.uniform(0.1, 0.95)
    response_rate = min(1.0, max(0.0, base_engagement + random.gauss(0, 0.1)))
    engagement = min(1.0, max(0.0, base_engagement + random.gauss(0, 0.15)))

    return BehavioralSignals(
        recruiter_response_rate=round(response_rate, 3),
        platform_engagement=round(engagement, 3),
        profile_completeness=round(completeness, 3),
        interview_completion_rate=round(
            min(1.0, max(0.0, random.gauss(0.7, 0.2))), 3
        ),
        offer_acceptance_rate=round(
            min(1.0, max(0.0, random.gauss(0.6, 0.25))), 3
        ),
        recruiter_saves=max(0, int(random.gauss(5, 8))),
        activity_score=round(min(1.0, max(0.0, random.gauss(0.5, 0.25))), 3),
        last_active_days_ago=max(0, int(random.expovariate(1 / 30))),
    )


def _generate_projects(skills: list[str]) -> list[str]:
    """Generate project descriptions based on skills."""
    count = random.randint(0, 4)
    projects = []
    techs = ["ML", "data pipeline", "microservice", "API", "dashboard",
             "recommendation", "search", "analytics", "monitoring", "platform"]
    clouds = ["AWS", "GCP", "Azure"]
    domains = ["fintech", "e-commerce", "healthcare", "social", "gaming",
               "enterprise", "IoT", "security"]
    volumes = ["1M", "10M", "100M", "1B"]
    metrics = ["40%", "60%", "3x", "10x", "99.9%"]
    scales = ["1M", "10M", "50M", "100K"]

    for _ in range(count):
        template = random.choice(PROJECT_TEMPLATES)
        project = template.format(
            tech=random.choice(skills[:5]) if skills else "Python",
            old_tech=random.choice(["monolith", "legacy system", "batch processing"]),
            domain=random.choice(domains),
            volume=random.choice(volumes),
            metric=random.choice(metrics),
            scale=random.choice(scales),
            cloud=random.choice(clouds),
        )
        projects.append(project)
    return projects


def _generate_headline(title: str, skills: list[str]) -> str:
    """Generate a LinkedIn-style headline."""
    templates = [
        f"{title} | {' · '.join(skills[:3])}",
        f"{title} passionate about {random.choice(skills[:5]) if skills else 'technology'}",
        f"Experienced {title} specializing in {' & '.join(skills[:2])}",
        f"{title} | Building the future with {random.choice(skills[:3]) if skills else 'code'}",
        f"{title} → {random.choice(['AI/ML', 'Data', 'Cloud', 'Full Stack', 'Platform'])} enthusiast",
    ]
    return random.choice(templates)


def _generate_summary(
    title: str, experience_years: float, skills: list[str], career: list[CareerEntry]
) -> str:
    """Generate a profile summary."""
    top_skills = ", ".join(skills[:5]) if skills else "software engineering"
    companies = [e.company for e in career[-3:]]
    company_text = ", ".join(companies) if companies else "various companies"

    templates = [
        (
            f"{title} with {experience_years:.0f}+ years of experience. "
            f"Skilled in {top_skills}. "
            f"Previously at {company_text}. "
            f"Passionate about building scalable systems and solving complex problems."
        ),
        (
            f"Results-driven {title} bringing {experience_years:.0f} years of expertise "
            f"in {top_skills}. "
            f"Track record of delivering high-impact projects at {company_text}."
        ),
        (
            f"Experienced {title} ({experience_years:.0f}+ yrs) with deep expertise in "
            f"{top_skills}. "
            f"Background includes roles at {company_text}. "
            f"Strong communicator and collaborative team player."
        ),
    ]
    return random.choice(templates)


def generate_candidate(idx: int) -> CandidateProfile:
    """Generate a single synthetic candidate profile."""
    # Seniority distribution (weighted toward mid-level)
    seniority_idx = _weighted_choice(
        list(range(len(SENIORITY_PROGRESSION))),
        [0.03, 0.10, 0.25, 0.25, 0.10, 0.08, 0.08, 0.06, 0.03, 0.02],
    )
    seniority = SENIORITY_PROGRESSION[seniority_idx]

    # Experience years correlates with seniority
    base_years = seniority_idx * 2 + random.uniform(-1, 2)
    experience_years = max(0.5, min(30, base_years))

    # Generate components
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
    skills = _generate_skills(seniority_idx)
    career = _generate_career(experience_years, seniority_idx)
    education = _generate_education(seniority_idx)
    certs = _generate_certifications()
    behavioral = _generate_behavioral()
    projects = _generate_projects(skills)

    current_entry = career[-1] if career else None
    current_title = current_entry.title if current_entry else "Software Engineer"
    current_company = current_entry.company if current_entry else "Unknown"

    headline = _generate_headline(current_title, skills)
    summary = _generate_summary(current_title, experience_years, skills, career)

    locations = [
        "San Francisco, CA", "New York, NY", "Seattle, WA", "Austin, TX",
        "Boston, MA", "Los Angeles, CA", "Chicago, IL", "Denver, CO",
        "Portland, OR", "Atlanta, GA", "Miami, FL", "London, UK",
        "Berlin, Germany", "Toronto, Canada", "Bangalore, India",
        "Singapore", "Tokyo, Japan", "Sydney, Australia", "Tel Aviv, Israel",
        "Amsterdam, Netherlands", "Remote",
    ]

    return CandidateProfile(
        candidate_id=f"cand_{idx:06d}",
        name=name,
        headline=headline,
        summary=summary,
        location=random.choice(locations),
        email=f"{name.lower().replace(' ', '.')}_{idx}@email.com",
        career_history=career,
        total_experience_years=round(experience_years, 1),
        current_title=current_title,
        current_company=current_company,
        skills=skills,
        certifications=certs,
        education=education,
        projects=projects,
        behavioral_signals=behavioral,
        tags=[seniority.value, random.choice(INDUSTRIES).lower()],
        source="synthetic",
    )


def generate_sample_job_descriptions() -> list[JobDescription]:
    """Generate sample job descriptions for testing."""
    return [
        JobDescription(
            job_id="jd_001",
            title="Senior AI/ML Engineer",
            company="TechCorp AI",
            industry="Technology",
            description="""
We are looking for a Senior AI/ML Engineer to join our Applied AI team.

Requirements:
- 5+ years of experience in machine learning and software engineering
- Strong proficiency in Python, PyTorch, and TensorFlow
- Experience building and deploying production ML systems
- Deep understanding of NLP, LLMs, and transformer architectures
- Experience with RAG systems, vector databases, and embedding models
- Familiarity with MLOps practices (CI/CD for ML, model monitoring)
- Strong system design skills for scalable ML infrastructure

Preferred:
- Experience with LLM fine-tuning and RLHF
- Knowledge of distributed training (DeepSpeed, FSDP)
- Experience with Kubernetes and cloud platforms (AWS/GCP)
- Published research or contributions to open-source ML projects
- Experience leading technical projects or mentoring engineers

About the role:
- Build next-generation AI features using large language models
- Design and implement scalable ML pipelines
- Collaborate with product and research teams
- Mentor junior engineers and contribute to technical strategy
- Work in a fast-paced startup environment

We value candidates who think like product owners, have a startup mindset,
and can drive technical decisions independently.
            """,
            location="San Francisco, CA",
            seniority="senior",
        ),
        JobDescription(
            job_id="jd_002",
            title="Staff Data Engineer",
            company="DataFlow Inc",
            industry="SaaS",
            description="""
Staff Data Engineer needed to architect our next-generation data platform.

Must-have:
- 8+ years in data engineering
- Expert in Apache Spark, Kafka, and Airflow
- Strong SQL and data modeling skills
- Experience with cloud data warehouses (Snowflake, BigQuery, or Redshift)
- Track record of building petabyte-scale data pipelines
- Python and Scala proficiency

Nice-to-have:
- Experience with real-time streaming architectures
- Knowledge of data governance and quality frameworks
- Familiarity with dbt and modern data stack
- Leadership experience managing data engineering teams
- Experience with Delta Lake or Apache Iceberg

You'll lead the design of our company-wide data infrastructure, mentor
a team of 5 engineers, and establish data engineering best practices.
            """,
            location="New York, NY",
            seniority="staff",
        ),
        JobDescription(
            job_id="jd_003",
            title="ML Platform Engineer",
            company="ScaleAI Labs",
            industry="Technology",
            description="""
ML Platform Engineer to build the infrastructure powering our AI products.

Requirements:
- 4+ years of experience in ML infrastructure or platform engineering
- Strong Python and Go programming skills
- Experience with Kubernetes, Docker, and container orchestration
- Familiarity with ML frameworks (PyTorch, TensorFlow)
- Experience building feature stores, model serving, or training platforms
- Knowledge of distributed systems and microservices

Preferred:
- Experience with Ray, Kubeflow, or MLflow
- Knowledge of GPU optimization and CUDA
- Experience with A/B testing frameworks
- Contributions to ML infrastructure open-source projects

Fast-paced startup, product-minded engineers preferred.
            """,
            location="Remote",
            seniority="mid",
        ),
        JobDescription(
            job_id="jd_004",
            title="Director of Machine Learning",
            company="Enterprise AI Corp",
            industry="Finance",
            description="""
Director of Machine Learning to lead our AI/ML organization.

Requirements:
- 12+ years in software engineering, 7+ in ML
- Proven track record leading ML teams of 15+ engineers
- Experience shipping ML products at scale in regulated industries
- Deep technical expertise in NLP, recommendation systems, or computer vision
- Strong product sense and business acumen
- PhD or MS in Computer Science, ML, or related field preferred

Must have:
- Executive communication skills
- Experience with ML strategy and roadmap planning
- Budget management experience
- Track record of recruiting and developing ML talent

You'll report to the CTO and own the entire ML strategy, team, and execution.
            """,
            location="New York, NY",
            seniority="director",
        ),
        JobDescription(
            job_id="jd_005",
            title="Full Stack Engineer (AI Products)",
            company="CreativeAI",
            industry="Media & Entertainment",
            description="""
Full Stack Engineer to build AI-powered creative tools.

Requirements:
- 3+ years of full stack development experience
- Strong React/Next.js and TypeScript skills
- Python backend experience (FastAPI or Django)
- Experience integrating AI/ML APIs into products
- Understanding of real-time systems and WebSockets
- Eye for design and UX

Preferred:
- Experience with generative AI products
- Knowledge of image/video processing
- Experience with Figma and design systems
- Startup experience and product ownership mindset
            """,
            location="Los Angeles, CA",
            seniority="mid",
        ),
    ]


def generate_dataset(
    num_candidates: int = 100_000,
    output_dir: str | Path | None = None,
    seed: int = 42,
) -> Path:
    """
    Generate the full synthetic dataset.

    Args:
        num_candidates: Number of candidate profiles to generate.
        output_dir: Directory to write output files.
        seed: Random seed for reproducibility.

    Returns:
        Path to the output directory.
    """
    random.seed(seed)

    if output_dir is None:
        output_dir = Path(__file__).resolve().parent.parent.parent / "data"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ---- Generate candidates ----
    candidates_file = output_dir / "candidates.jsonl"
    logger.info(f"Generating {num_candidates:,} candidate profiles → {candidates_file}")

    with open(candidates_file, "w", encoding="utf-8") as f:
        for i in tqdm(range(num_candidates), desc="Generating candidates"):
            candidate = generate_candidate(i)
            f.write(candidate.model_dump_json() + "\n")

    logger.info(f"✓ Wrote {num_candidates:,} candidates to {candidates_file}")

    # ---- Generate job descriptions ----
    jds = generate_sample_job_descriptions()
    jd_file = output_dir / "job_descriptions.json"
    with open(jd_file, "w", encoding="utf-8") as f:
        json.dump([jd.model_dump() for jd in jds], f, indent=2)

    logger.info(f"✓ Wrote {len(jds)} job descriptions to {jd_file}")

    # ---- Summary stats ----
    logger.info(f"Dataset generation complete. Output: {output_dir}")
    return output_dir


def load_candidates(
    path: str | Path | None = None, limit: int | None = None
) -> list[CandidateProfile]:
    """Load candidate profiles from JSONL file."""
    if path is None:
        path = Path(__file__).resolve().parent.parent.parent / "data" / "candidates.jsonl"
    path = Path(path)

    if not path.exists():
        logger.warning(f"Candidates file not found: {path}. Generating sample data...")
        generate_dataset(num_candidates=1000, output_dir=path.parent)

    candidates = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            candidates.append(CandidateProfile.model_validate_json(line.strip()))

    logger.info(f"Loaded {len(candidates):,} candidates from {path}")
    return candidates


def load_job_descriptions(path: str | Path | None = None) -> list[JobDescription]:
    """Load job descriptions from JSON file."""
    if path is None:
        path = Path(__file__).resolve().parent.parent.parent / "data" / "job_descriptions.json"
    path = Path(path)

    if not path.exists():
        logger.warning(f"JD file not found: {path}. Using built-in samples.")
        return generate_sample_job_descriptions()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [JobDescription.model_validate(jd) for jd in data]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic recruiter dataset")
    parser.add_argument(
        "-n", "--num-candidates", type=int, default=100_000,
        help="Number of candidates to generate (default: 100000)",
    )
    parser.add_argument(
        "-o", "--output-dir", type=str, default=None,
        help="Output directory (default: data/)",
    )
    parser.add_argument(
        "-s", "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    args = parser.parse_args()

    generate_dataset(
        num_candidates=args.num_candidates,
        output_dir=args.output_dir,
        seed=args.seed,
    )
