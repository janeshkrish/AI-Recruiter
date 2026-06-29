$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $repoRoot "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
  throw "Virtualenv Python not found at $python"
}

Set-Location $repoRoot
& $python -m uvicorn recruiter_brain.api.main:app --reload --host 127.0.0.1 --port 8000
