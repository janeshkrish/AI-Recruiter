# Sandbox Execution Strategy

This project has two sandbox profiles:

- Redrob ranking sandbox: no-network CPU-only batch execution.
- Application sandbox: resource-limited local API and UI containers for demos.

## Redrob Ranking Sandbox

Use the no-network compose recipe:

```bash
docker compose -f docker-compose.yml up --build ranker
```

Security properties:

- `network_mode: "none"` disables network access for ranking.
- The ranker uses only local files mounted into `/app`.
- No hosted LLM, hosted embedding, HTTP client, or external API is used by `rank.py`.
- Ranking writes only the output CSV path requested by the command.
- The default command validates CSV shape and repository compliance before exiting.

Recommended hardening for remote execution:

```yaml
services:
  ranker:
    network_mode: "none"
    read_only: true
    tmpfs:
      - /tmp:size=512m,noexec,nosuid,nodev
    mem_limit: 16g
    cpus: 8
    security_opt:
      - no-new-privileges:true
```

If the output CSV must be written, mount only a dedicated output directory as writable and keep the dataset mount read-only.

## Application Sandbox

Run the app with:

```bash
docker compose -f docker-compose.app.yml up --build
```

The app compose file applies CPU and memory limits:

- backend: 4 CPUs, 4 GB RAM
- frontend: 2 CPUs, 1 GB RAM

For public demos, place the backend behind a reverse proxy with request-size limits and TLS. Add authentication before exposing candidate data.

## Uploaded Resume Handling

The backend resume service follows these rules:

- never executes uploaded files
- accepts only known extensions: `.txt`, `.md`, `.csv`, `.pdf`, `.docx`
- enforces `AI_RECRUITER_MAX_UPLOAD_BYTES`
- copies each upload into a unique temporary directory
- extracts text using safe parsers or plain decoding
- deletes temporary files after parsing
- returns warnings instead of attempting risky behavior when extraction is limited

Recommended container hardening for uploads:

```yaml
services:
  backend:
    read_only: true
    tmpfs:
      - /tmp:size=256m,noexec,nosuid,nodev
    security_opt:
      - no-new-privileges:true
    mem_limit: 4g
    cpus: 4
```

## File Isolation

Use separate mounts for:

- dataset: read-only
- application code: read-only in production images
- upload temp storage: tmpfs
- output CSV: writable output-only directory

Do not mount the host home directory into the containers.

## Cleanup Process

Local cleanup:

```bash
docker compose -f docker-compose.yml down --remove-orphans
docker compose -f docker-compose.app.yml down --remove-orphans
```

Temporary upload directories are removed by the backend service at request completion. Docker `tmpfs` upload storage is also discarded when the backend container stops.

## Network Policy

Challenge ranking:

- network disabled
- no API keys
- no hosted inference
- no online vector database

Application mode:

- frontend talks to backend over local HTTP
- backend does not need outbound network for ranking
- outbound network can be blocked in production unless additional integrations are intentionally added

## Secrets Policy

The default project requires no secrets. Keep `.env` files local and never commit API keys. The Redrob ranking path ignores hosted-model credentials by design.
