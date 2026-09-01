# Product Change Impact Assessment & Decision Readiness

## Demo Command Reference v0.1

**Purpose:** Cross-platform operator commands for the existing five-minute deterministic demo.  
**Narrative authority:** none — this is an operator aid only.  
**Supported presentation paths:** Bash-compatible shell and Windows PowerShell.

---

# 1. Rule

Use the command set that matches the presentation host. Do not change scenario inputs, expected oracles, committed evidence or frozen architecture files to make a live demonstration work.

The static evidence extracts remain the explanatory views. The commands only prove execution through the real application services.

---

# 2. Bash / Linux / macOS-style shell

## Prepare disposable paths

```bash
export PLM_REF_DATABASE_PATH=/tmp/plm-ref-demo.db
rm -f /tmp/plm-ref-demo.db /tmp/plm-ref-verify.db
rm -rf /tmp/plm-ref-demo-evidence
```

## Scenario A live execution

```bash
plm-ref db reset
plm-ref scenario run A
```

Expected terse output:

```text
database reset
CHG-A01
```

## Independent verification into disposable evidence

```bash
export PLM_REF_DATABASE_PATH=/tmp/plm-ref-verify.db
export PLM_REF_EVIDENCE_PATH=/tmp/plm-ref-demo-evidence
python -c 'import os; from plm_ref.application.scenario_runner import verify_all; raise SystemExit(0 if verify_all(os.environ["PLM_REF_DATABASE_PATH"], os.environ["PLM_REF_EVIDENCE_PATH"]) else 1)'
```

---

# 3. Windows PowerShell

## Prepare disposable paths

```powershell
$env:PLM_REF_DATABASE_PATH = Join-Path $env:TEMP "plm-ref-demo.db"
$demoDb = $env:PLM_REF_DATABASE_PATH
$verifyDb = Join-Path $env:TEMP "plm-ref-verify.db"
$verifyEvidence = Join-Path $env:TEMP "plm-ref-demo-evidence"

Remove-Item $demoDb -Force -ErrorAction SilentlyContinue
Remove-Item $verifyDb -Force -ErrorAction SilentlyContinue
Remove-Item $verifyEvidence -Recurse -Force -ErrorAction SilentlyContinue
```

## Scenario A live execution

```powershell
plm-ref db reset
plm-ref scenario run A
```

Expected terse output:

```text
database reset
CHG-A01
```

## Independent verification into disposable evidence

```powershell
$env:PLM_REF_DATABASE_PATH = $verifyDb
$env:PLM_REF_EVIDENCE_PATH = $verifyEvidence
python -c "import os; from plm_ref.application.scenario_runner import verify_all; raise SystemExit(0 if verify_all(os.environ['PLM_REF_DATABASE_PATH'], os.environ['PLM_REF_EVIDENCE_PATH']) else 1)"
```

---

# 4. Pre-session installation

Use the repository's locked release environment. For the verified release path, use Python 3.12.

```text
python -m pip install --require-hashes -r requirements.lock
python -m pip install --no-deps --no-build-isolation -e .
```

The project metadata permits Python 3.12+, but the release lock and CI verification are specifically established on Python 3.12.

---

# 5. Failure handling

If the command fails because of host setup:

1. stop the live command path;
2. use the committed Session 6 static evidence extracts;
3. state that the recorded verified executable baseline is `7a5733fc7042e33a790db12278f8776d047eb4b6`;
4. do not edit fixtures, expected oracles or committed evidence during a presentation.

A host-environment failure is not evidence that the frozen architecture changed. Conversely, do not claim success unless either the live command succeeds or the committed verification evidence is being shown explicitly.
