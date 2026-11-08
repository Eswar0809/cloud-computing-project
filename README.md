# Cloud Command Parser: Knowledge Distillation and Deployment on a Local Cloud
**CS3081 Cloud Computing — Mini Project**

- **Student Name:** Chittoju Eswar Chandra vidya sagar
- **Roll Number:** 230101087
- **GitHub Repository:** [https://github.com/Eswar0809/cloud-computing-project](https://github.com/Eswar0809/cloud-computing-project)
- **Submission Tag:** `final`

---

## 1. Overview & Architecture

This repository contains the end-to-end implementation of sequence-level knowledge distillation (Kim & Rush, EMNLP 2016) compressing a 3-billion parameter teacher model into a 70-million parameter causal student model (`EleutherAI/pythia-70m`), containerized and orchestrated on a local Kubernetes cloud.

```
                    +-----------------------+
                    |   External Ingress    |
                    | (Traefik / Port 8000) |
                    +-----------+-----------+
                                |
             +------------------+------------------+
             |                                     |
   +---------v---------+                 +---------v---------+
   |   Pod Replica 1   |                 |   Pod Replica 2   |
   | (1 vCPU, 1 GiB)   |                 | (1 vCPU, 1 GiB)   |
   |    FastAPI :8000  |                 |    FastAPI :8000  |
   +---------+---------+                 +---------+---------+
             |                                     |
             +------------------+------------------+
                                | Startup Asset Download
                    +-----------v-----------+
                    |  SeaweedFS S3 Storage |
                    | (Bucket: s3://models) |
                    +-----------------------+
```

---

## 2. Directory Structure

```
├── .github/workflows/
│   └── ci.yml               # Complete GitHub Actions CI/CD pipeline
├── cluster/
│   └── k3d.yaml             # k3d 2-node cluster configuration
├── data/
│   ├── commands_pool.jsonl  # 3,000 raw SLURP voice assistant commands
│   ├── validation.jsonl     # 100 labeled validation commands
│   ├── schema.json          # 4-key JSON schema & 8 intent definitions
│   └── rate_card.json       # Hypothetical on-demand cloud pricing
├── datasets/v1/
│   ├── train.jsonl          # 1,556 cleaned training commands
│   └── train.sha256         # SHA-256 dataset checksum
├── k8s/
│   ├── app.yaml             # Deployment, Service, Ingress, HPA, Secrets
│   ├── pipeline.yaml        # Parallel worker Job manifest
│   └── seaweedfs.yaml       # SeaweedFS StatefulSet & Service manifests
├── models/
│   ├── v1/                  # Distilled student model v1 & model.sha256
│   └── v2/                  # Model v2 artifacts & model.sha256
├── network/
│   ├── nacl.json            # Stateless Network Access Control List rules
│   ├── subnets.md           # Subnetting hierarchy & stateless NACL proof
│   └── packets_sample.jsonl # 6 test packets for NACL verification
├── prompts/
│   └── teacher_prompt.txt   # Teacher generation prompt
├── results/
│   ├── cold_start.txt       # Cold-start benchmark across 3 independent runs
│   ├── loadtest_stats.csv   # Locust load test statistics
│   ├── loadtest_headers.json# Locust header telemetry (per-replica & per-version)
│   ├── memory_profile.txt   # 50-request memory profile under resource limits
│   ├── recovery_test.txt    # Rolling update & pod recovery log
│   ├── student_validation.json # Distilled student model evaluation report
│   └── teacher_validation.json # Teacher model evaluation report
├── service/
│   ├── app.py               # FastAPI inference service & schema validator
│   ├── Dockerfile           # Optimized CPU-only container image (<2 GB)
│   └── requirements.txt     # Pinned Python dependencies
├── tests/
│   └── test_service.py      # Unit test suite (5 comprehensive tests)
├── tools/
│   ├── generate_reflection_pdf.py # Generates 230101087.pdf (3-page reflection)
│   ├── generate_report_pdf.py     # Generates report/report.pdf (9-page report)
│   ├── locustfile.py        # Locust load test script
│   ├── nacl_sim.py          # Stateless NACL packet simulator
│   ├── profile_memory.py    # Memory and resource profiling tool
│   ├── run_cluster_benchmark.py # Cold start & cluster lifecycle benchmark
│   └── score.py             # Validation scoring tool
├── training/
│   ├── config.yaml          # Pinned training hyperparameters & library versions
│   ├── loss.csv             # Training loss progression (v1)
│   ├── loss_v2.csv          # Training loss progression (v2)
│   └── train.py             # Sequence-level knowledge distillation script
├── worker/
│   ├── clean.py             # Multi-stage cleaning & validation script
│   └── worker.py            # Parallel teacher labeling worker
├── 230101087.pdf            # 3-page scanned reflection deliverable
├── report/
│   └── report.pdf           # 9-page comprehensive engineering report
├── AI_USE.md                # AI transparency & human verification documentation
├── Makefile                 # Automation targets (up, down, train, test, lint)
└── README.md                # Project documentation
```

---

## 3. Quickstart & Deployment Instructions

### A. Prerequisites
- Python 3.11+
- SeaweedFS binary (`bin/weed.exe` or `weed`)
- Docker & kubectl / k3d (optional for containerized orchestration)

### B. One-Command Cluster Bootstrap
```bash
make up
```
This single command:
1. Launches SeaweedFS S3 server on port 8333.
2. Creates S3 buckets `datasets` and `models`.
3. Downloads release model assets from GitHub Releases.
4. Starts the dual-replica inference service with Ingress routing on port 8000.

### C. Teardown
```bash
make down
```
Tears down active deployments, stops storage servers, and cleans temporary mounts.

---

## 4. Testing, Profiling & Evaluation

### A. Run Unit Tests & Linting
```bash
# Execute unit test suite (5 passed)
make test

# Execute flake8 style linter (0 warnings / 0 errors)
make lint
```

### B. Score Distilled Student Model
```bash
python tools/score.py results/student_predictions.jsonl data/validation.jsonl --out results/student_validation.json --min-validity 95
```

### C. Execute Memory Profiling (50 Sequential Requests)
```bash
python tools/profile_memory.py
```
Outputs memory consumption evidence to `results/memory_profile.txt`.

### D. Run Locust Load Test Benchmark (2 Minutes)
```bash
locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m --host http://localhost:8000 --csv results/loadtest
```
Generates `results/loadtest_stats.csv` and `results/loadtest_headers.json`.

### E. Verify Stateless Network Access Control Rules
```bash
python tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check
```

### F. Compile PDF Deliverables
```bash
# Compile 3-page scanned reflection document
python tools/generate_reflection_pdf.py

# Compile comprehensive 9-page project report
python tools/generate_report_pdf.py
```

---

## 5. Measured Experimental Results

| Metric | Measured Value | Requirement / Grading Threshold | Compliance |
| :--- | :--- | :--- | :--- |
| **JSON Validity** | **97.0%** | &ge; 95.0% | **PASSED** |
| **Full-Frame Accuracy** | **59.0%** | &ge; 31.0% (50% of Teacher 62%) | **PASSED** |
| **Median Cold-Start Time** | **9.26 s** | Over 3 independent runs | **PASSED** |
| **Peak RSS Memory** | **554.00 MiB** | 1,024 MiB (45.9% Headroom) | **PASSED** |
| **p50 (Median) Latency** | **130 ms** | &le; 5,000 ms | **PASSED** |
| **p95 Latency** | **250 ms** | &le; 5,000 ms (20x faster) | **PASSED** |
| **Throughput** | **27.23 req/s** | Sustained over 2m under 4 users | **PASSED** |
| **Error Rate** | **0.0%** | &le; 1.0% (0 errors in 3,264 reqs) | **PASSED** |
| **Fault Injection** | **HTTP 500** | Body: `{"error": "invalid_model_output"}` | **PASSED** |
| **NACL Verification** | **6/6 (100.0%)** | 100% test packet match | **PASSED** |
| **Cost per 1,000 Reqs** | **₹0.0806 INR** | ₹7.90/hr cluster cost @ 27.23 req/s | **PASSED** |

---

## 6. GitHub Release Assets

In compliance with project specifications prohibiting large binary files in git history:
- Model weights (`model.safetensors`, 280 MB), tokenizer vocabulary files, and configuration manifests are published as assets under GitHub Release **`v1.0.0`**.
- Local checksum files:
  - `models/v1/model.sha256`: `95053ae63c454e1d5b57a8dc9cbdc5483304e61dea7b7ba10e4eee0e679e1452`
  - `models/v2/model.sha256`: `9d8678e277dad0b4c5630b326a6178e3ae9cb292ec216c8207f41d15f1e2c47a`
  - `datasets/v1/train.sha256`: `b6e8e5ddad44ee3e5c7bfa6b2fac230befc3b6c09ae80a29f4ce6597bea5aacf`

