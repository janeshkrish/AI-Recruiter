# API Documentation

Base URL for local development:

```text
http://127.0.0.1:8000
```

Most application endpoints are prefixed with `/api`. The root `/` route is a friendly backend landing response.

Authentication: none for the local hackathon application. Add authentication at the API gateway or middleware layer before exposing this service publicly.

## Error Format

All handled errors return:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

Common status codes:

| Status | Meaning |
| --- | --- |
| 400 | Invalid request, unsupported file type, malformed upload |
| 404 | Candidate not found |
| 413 | Uploaded file exceeds configured limit |
| 422 | Request validation failed |
| 500 | Unexpected server error |

## GET /

Backend landing response. Use this when opening `http://127.0.0.1:8000` directly in a browser.

Response:

```json
{
  "name": "AI Recruiter Platform",
  "version": "4.0.0",
  "status": "running",
  "frontend": "http://127.0.0.1:5173",
  "docs": "http://127.0.0.1:8000/docs",
  "health": "http://127.0.0.1:8000/api/health",
  "message": "This is the backend API. Open the frontend URL for the app UI."
}
```

## GET /api/health

Health check.

Response:

```json
{
  "status": "healthy",
  "app": "AI Recruiter Platform",
  "version": "4.0.0",
  "ranking_mode": "offline_deterministic",
  "network_required_for_ranking": false
}
```

## GET /api/status

Alias for `/api/health`.

## GET /api/stats

Dataset statistics for the frontend dashboard.

Response:

```json
{
  "total_applicants": 100000,
  "avg_experience": 7.2,
  "total_companies": 63,
  "top_skills": [
    { "name": "Python", "count": 10000 }
  ],
  "locations": {
    "Bengaluru": 12000
  }
}
```

Exact skill and location values depend on the dataset.

## GET /api/candidates

Paginated candidate search.

Query parameters:

| Name | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| page | integer | no | `>= 1`, default `1` | Page number |
| limit | integer | no | `1..500`, default `25` | Page size |
| search | string | no | any | Free-text match across ID, name, role, company, location, and skills |
| skills | string | no | comma-separated | Required skill filters |
| min_experience | number | no | `>= 0`, default `0` | Minimum years of experience |
| current_role | string | no | any | Current title substring filter |

Response:

```json
{
  "candidates": [
    {
      "id": "CAND_0000001",
      "profile": {},
      "skills": [],
      "career_history": []
    }
  ],
  "total": 100000,
  "page": 1,
  "limit": 25,
  "total_pages": 4000
}
```

## GET /api/candidates/{candidate_id}

Returns a single candidate record.

Path parameters:

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| candidate_id | string | yes | Candidate ID, for example `CAND_0000001` |

Response:

```json
{
  "id": "CAND_0000001",
  "profile": {},
  "career_history": [],
  "skills": [],
  "education": [],
  "certifications": [],
  "projects": [],
  "languages": [],
  "redrob_signals": {}
}
```

Errors:

| Status | Code | Cause |
| --- | --- | --- |
| 404 | `CANDIDATE_NOT_FOUND` | Unknown candidate ID |

## GET /api/candidates/role-ranking

Returns the default Senior AI Engineer ranking used by the restored UI.

Query parameters:

| Name | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| limit | integer | no | `1..500`, default `100` | Number of ranked rows |

Response:

```json
{
  "role": "Senior AI Engineer",
  "source_documents": ["jd.txt", "candidates.jsonl"],
  "total": 100,
  "rows": [
    {
      "candidate_id": "CAND_0046064",
      "rank": 1,
      "score": 92.3456,
      "reasoning": "Evidence-based deterministic explanation.",
      "overall_score": 92.3456,
      "hiring_recommendation": "Strong match",
      "top_matching_evidence": [],
      "missing_requirements": [],
      "risk_factors": [],
      "production_evidence": [],
      "behavioral_evidence": [],
      "jd_alignment_score": 0.91,
      "score_breakdown": {},
      "scoring_weights": {}
    }
  ]
}
```

## GET /api/candidates/role-ranking.csv

Downloads the default ranking CSV.

Query parameters:

| Name | Type | Required | Validation | Description |
| --- | --- | --- | --- | --- |
| limit | integer | no | `1..500`, default `100` | Number of rows |

Response content type:

```text
text/csv; charset=utf-8
```

CSV columns:

```csv
candidate_id,rank,score,reasoning
```

## POST /api/rank

Ranks candidates for a supplied job description.

Request body:

```json
{
  "job_description": "Senior AI Engineer with production retrieval and ranking experience...",
  "custom_weights": {
    "production_ml_experience": 0.25,
    "retrieval_ranking_experience": 0.2
  }
}
```

Validation:

| Field | Required | Rule |
| --- | --- | --- |
| job_description | yes | non-empty string |
| custom_weights | no | object of weight names to numeric values |

Response:

```json
{
  "ranked_candidates": [
    {
      "candidate_id": "CAND_0046064",
      "rank": 1,
      "score": 92.3456,
      "skill_match": 0.88,
      "experience_match": 0.93,
      "semantic_similarity": 0.84,
      "location_match": 1.0,
      "potential_score": 0.72,
      "behavioral_score": 0.66,
      "transferable_matches": 4,
      "reasoning": "Evidence-based deterministic explanation.",
      "behavioral_insights": [],
      "anti_pattern_flags": [],
      "anti_pattern_penalty": 1.0,
      "candidate_details": {},
      "overall_score": 92.3456,
      "hiring_recommendation": "Strong match",
      "top_matching_evidence": [],
      "missing_requirements": [],
      "risk_factors": [],
      "production_evidence": [],
      "behavioral_evidence": [],
      "jd_alignment_score": 0.91,
      "score_breakdown": {},
      "scoring_weights": {}
    }
  ],
  "parsed_jd": {
    "must_have": [],
    "nice_to_have": [],
    "explicit_reject": [],
    "culture_fit": [],
    "behavior_fit": [],
    "hiring_intent": []
  },
  "pipeline_stats": {
    "total_candidates_scanned": 100000,
    "ranking_mode": "offline_deterministic"
  }
}
```

## POST /api/rank/role

Alias for `/api/rank`. The restored frontend calls this route from the JD analysis workflow.

## GET /api/pipeline/analytics

Returns aggregate analytics for the pipeline page.

Response:

```json
{
  "funnel": [],
  "quality_signals": {},
  "skill_distribution": [],
  "location_distribution": [],
  "experience_distribution": []
}
```

The exact keys are generated from the loaded dataset and are intended for frontend visualization.

## POST /api/copilot

Returns a deterministic non-LLM answer for recruiter questions.

Request body:

```json
{
  "question": "Who are the strongest retrieval candidates?",
  "candidates": [
    {
      "candidate_id": "CAND_0046064",
      "score": 92.34,
      "reasoning": "..."
    }
  ],
  "totalCandidates": 100
}
```

Validation:

| Field | Required | Rule |
| --- | --- | --- |
| question | yes | 1 to 1000 characters |
| candidates | no | list of candidate-like objects |
| totalCandidates | no | integer |

Response:

```json
{
  "answer": "Deterministic answer based on supplied candidates and computed evidence."
}
```

## POST /api/resumes/upload

Safely parses an uploaded resume into text preview and basic skills.

Form data:

| Name | Type | Required | Validation |
| --- | --- | --- | --- |
| file | file | yes | `.txt`, `.md`, `.csv`, `.pdf`, `.docx`; max size from `AI_RECRUITER_MAX_UPLOAD_BYTES` |

Response:

```json
{
  "filename": "resume.txt",
  "content_type": "text/plain",
  "size_bytes": 1024,
  "text_preview": "Candidate resume preview...",
  "extracted_skills": ["python", "machine learning"],
  "warnings": []
}
```

Security behavior:

- uploaded files are not executed
- files are copied into a temporary directory
- temporary files are deleted after parsing
- unsupported file types are rejected
- PDFs are accepted with a warning if text extraction is unavailable
