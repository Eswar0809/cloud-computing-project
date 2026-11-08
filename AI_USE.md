# AI Assistance Disclosure (AI_USE.md)

**Student Name:** Chittoju Eswar Chandra vidya sagar  
**Roll Number:** 230101087  
**Course:** CS3081 - Cloud Computing  
**Project:** Knowledge Distillation and Deployment of a Lightweight Command-Parsing Language Model on a Local Cloud  
**GitHub Repository:** https://github.com/Eswar0809/cloud-computing-project  

---

## 1. AI Tools Utilized

In accordance with the assignment guidelines, modern AI assistance was leveraged strategically throughout the implementation of this project:

1. **Google DeepMind Antigravity / Gemini 2.5 Pro:**
   - **Usage Purpose:** Architecture design, automation script synthesis, Kubernetes manifest validation, CIDR subnetting arithmetic verification, and report drafting.
   - **Context:** Used as an intelligent pair-programmer to design reproducible distillation pipelines, container configurations, and CI/CD workflows.

2. **Ollama with Phi-3.5-mini-instruct (3.8B Parameters):**
   - **Usage Purpose:** Sequence-level knowledge distillation teacher model.
   - **Configuration:** Temperature `0`, Seed `42`, JSON mode formatting. Served locally on port 11434 to label natural language voice commands from `commands_pool.jsonl`.

---

## 2. Specific Tasks and Workflows

| Project Component | AI Tool Used | AI Contribution | Human Oversight & Verification Method |
| :--- | :--- | :--- | :--- |
| **Task 1: Teacher Sharding & Pipeline** | Antigravity | Synthesized sharded worker script (`worker/worker.py`) with S3 integration and directory locking. | Tested atomic lock under race conditions, verified zero overlaps across `shard-0.jsonl` and `shard-1.jsonl`, confirmed `commands_pool` IDs cover all 3,000 commands. |
| **Task 1: Data Cleaning Filter** | Antigravity | Formulated `worker/clean.py` implementing strict filter criteria (a)–(e) and checksum verification. | Manually checked JSON schema conformity, validated slot boundary checking against command substrings, and ensured arithmetic balance `input = (a)+(b)+(c)+(d)+duplicates+kept`. |
| **Task 2: Student Distillation** | Antigravity | Drafted PyTorch causal LM training loop with fixed seeds and CPU thread optimization. | Identified hybrid Intel CPU (P/E core) thread contention bottleneck, added `torch.set_num_threads(2)`, and confirmed loss convergence in `training/loss.csv`. |
| **Task 3: Inference Container** | Antigravity | Formulated FastAPI application with `/healthz`, `/readyz`, `/parse`, and fault injection. | Verified `FAULT_INJECT=1` returns HTTP 500 `{"error": "invalid_model_output"}`, verified response headers (`X-Model-Version`, `X-Served-By`), and tested memory usage. |
| **Task 4: Kubernetes Deployment** | Antigravity | Authored Kubernetes manifests (`k8s/app.yaml`) including Deployment, Service, Ingress, and HPA. | Tested YAML syntax with `kubectl --dry-run=client`, verified probe timings, rolling update zero-downtime strategy, and replica recovery logic. |
| **Task 5: Subnetting & NACL** | Antigravity | Calculated binary CIDR boundaries for 10.20.0.0/16 and initial NACL rule sequencing. | Executed `tools/nacl_sim.py` with `--check` against test packets (100% pass rate), verified ephemeral port replies, and ensured deny rules precede allow rules. |
| **Task 6: CI/CD Pipeline** | Antigravity | Created GitHub Actions workflow YAML (`.github/workflows/ci.yml`) and `Makefile`. | Ran `flake8` lint checks locally (0 warnings), verified `pytest tests/` (5 unit tests passed), and configured Gitleaks secret scanning. |
| **Task 7: Performance & SRE** | Antigravity | Drafted cost formulas and SRE review structure based on `data/rate_card.json`. | Checked every mathematical calculation step for cost per 1,000 requests, error budget formulas, and linked evidence to measured numbers. |

---

## 3. Verification and Validation Procedures

All code, manifests, and mathematical proofs generated with AI assistance were strictly verified using deterministic validation techniques:

1. **Automated Testing & Linting:**
   - Ran `flake8 service/ worker/ training/ tests/` ensuring 100% compliance with PEP8 standards.
   - Ran `pytest tests/test_service.py` verifying schema validation, health probes, and fault injection behavior.
2. **Ground Truth Validation Scripts:**
   - Evaluated teacher and student models using the official `tools/score.py` against `data/validation.jsonl`.
   - Verified network access rules using the official `tools/nacl_sim.py` simulator.
3. **Execution Profiling:**
   - Benchmarked inference latency, throughput, and memory consumption directly on host hardware using `psutil` and Locust.
4. **Security & Credential Auditing:**
   - Conducted repository scans using Gitleaks to guarantee that zero API keys, secrets, or passwords are committed to source control.

