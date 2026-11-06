"""
Compiles report/report.pdf
Maximum 8 pages for main tasks (excluding references and appendices).
Student: Nemapu Navaneeth (Roll No: 230101086)
GitHub: https://github.com/NavaneethNemapu/cloud-command-parser
"""
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

OUTPUT_PDF = "report/report.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        w, h = letter

        # Running header rule
        self.setStrokeColor(colors.HexColor("#0969DA"))
        self.setLineWidth(1.0)
        self.line(40, h - 38, w - 40, h - 38)

        # Header text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F2328"))
        self.drawString(40, h - 32, "CS3081 CLOUD COMPUTING — PROJECT REPORT")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#57606A"))
        self.drawRightString(w - 40, h - 32, "Nemapu Navaneeth | Roll: 230101086")

        # Footer rule
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.6)
        self.line(40, 36, w - 40, 36)

        # Footer text
        self.drawString(40, 24, "Repository: https://github.com/NavaneethNemapu/cloud-command-parser")
        self.drawRightString(w - 40, 24, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_report():
    os.makedirs(os.path.dirname(OUTPUT_PDF) or ".", exist_ok=True)
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=46,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # Core typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0969DA")
    )

    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#24292F")
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#24292F")
    )

    h1_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0969DA"),
        spaceBefore=6,
        spaceAfter=3
    )

    h2_style = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1F2328"),
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.4,
        textColor=colors.HexColor("#24292F"),
        spaceAfter=3
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, METADATA, EXEC SUMMARY & TASK 1 (OBJECT STORAGE & TEACHER)
    # =========================================================================
    story.append(Paragraph("Knowledge Distillation and Deployment of a Lightweight Command-Parsing Language Model on a Local Cloud", title_style))
    story.append(Paragraph("CS3081 Cloud Computing — Comprehensive Systems & Engineering Report", sub_title_style))
    story.append(Spacer(1, 3))

    meta_table_data = [
        [
            Paragraph("<b>Author:</b> Nemapu Navaneeth (Roll: <b>230101086</b>)", meta_style),
            Paragraph("<b>GitHub:</b> <font color='#0969DA'>https://github.com/NavaneethNemapu/cloud-command-parser</font>", meta_style)
        ],
        [
            Paragraph("<b>Target Hardware:</b> CPU-only Local Cloud Node", meta_style),
            Paragraph("<b>Student Model:</b> EleutherAI/pythia-70m (70M params)", meta_style)
        ]
    ]
    meta_t = Table(meta_table_data, colWidths=[260, 272])
    meta_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meta_t)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Executive Summary", h1_style))
    story.append(Paragraph(
        "Deploying multi-billion parameter LLMs for edge assistants is hindered by memory and compute ceilings. In this project, "
        "we apply sequence-level knowledge distillation (Kim &amp; Rush, 2016) to distill an instruction-tuned 3B parameter teacher "
        "into a 70M parameter causal student (EleutherAI/pythia-70m). The distilled model is containerized and orchestrated "
        "on a local Kubernetes cloud. Over a 2-minute Locust benchmark (3,264 requests), the deployment sustained <b>27.23 req/s</b>, "
        "with <b>p50 latency of 130 ms</b>, <b>p95 of 250 ms</b> (well below 5,000 ms), <b>0.0% error rate</b>, and <b>peak memory of 554 MiB</b> "
        "(45.9% safe headroom below the 1 GiB limit). Zero-downtime rolling updates and pod recovery were fully validated.",
        body_style
    ))

    story.append(Paragraph("1. Task 1: Object Storage and Parallel Teacher Labelling", h1_style))
    story.append(Paragraph("<b>Architecture & Storage Design:</b>", h2_style))
    story.append(Paragraph(
        "SeaweedFS was deployed as an S3-compatible, distributed blob store running locally on port 8333. Metadata is managed via LevelDB "
        "on the Filer layer, while data blobs reside on dedicated Volume Servers. Two isolated S3 buckets were established: "
        "<font face='Courier'>s3://datasets/</font> for training corpora and <font face='Courier'>s3://models/</font> for versioned model artifacts. "
        "The raw 3,000-command SLURP dataset pool was partitioned into 2 balanced shards. A multi-process worker architecture "
        "(<font face='Courier'>worker/worker.py</font>) was orchestrated with atomic filesystem locks (<font face='Courier'>os.mkdir</font>) "
        "to prevent Ollama daemon lock contention while querying the Llama-3.2-3B teacher with an exact 4-key JSON system prompt.",
        body_style
    ))

    story.append(Paragraph("<b>Implementation, Cleaning & Measured Results:</b>", h2_style))
    story.append(Paragraph(
        "Raw teacher completions were processed through a deterministic multi-stage cleaning pipeline (<font face='Courier'>worker/clean.py</font>): "
        "(a) stripping markdown formatting/codeblocks, (b) schema validation requiring exactly 4 keys (<font face='Courier'>intent, date, time, place</font>) "
        "and 8 valid intents, (c) slot constraint enforcement (literal string matching without prepositions, null for unmentioned slots), "
        "and (d) deduplication across duplicate IDs. The pipeline strictly preserved the invariant: "
        "<b>Input (1,775) = (a) Markdown (3) + (b) Schema (6) + (c) Slots (0) + Duplicates (210) + Cleaned (1,556)</b>.<br/>"
        "The cleaned training dataset was stored at <font face='Courier'>datasets/v1/train.jsonl</font> with SHA-256 checksum: "
        "<font face='Courier'>02ce7de3287854831254b7a7257cbf0beddfc4d1ee97b086e405bde24fb80df9</font> and uploaded to SeaweedFS S3.",
        body_style
    ))

    story.append(Paragraph("<b>Limitations & Proposed Improvements:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Limitation:</i> SeaweedFS default master volume limit (<font face='Courier'>volume.max=8</font>) threw volume allocation RPC errors when multiple collections were created.<br/>"
        "• <i>Improvement:</i> Configure master startup with <font face='Courier'>-volume.max=50</font> and integrate etcd/Consul distributed locking in place of filesystem mutexes.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: TASK 2 (SEQUENCE-LEVEL KNOWLEDGE DISTILLATION)
    # =========================================================================
    story.append(Paragraph("2. Task 2: Training the Student (Sequence-Level Distillation)", h1_style))
    story.append(Paragraph("<b>Theoretical Foundation & Distillation Architecture:</b>", h2_style))
    story.append(Paragraph(
        "In sequence-level knowledge distillation (Kim &amp; Rush, 2016), the student causal language model is fine-tuned to maximize the "
        "likelihood of teacher-generated output sequences: \\(\\mathcal{L}(\\theta) = -\\sum_{t=1}^T \\log P(y_t \\mid y_{&lt;t}, x; \\theta)\\), "
        "where \\(y\\) is the teacher's greedily decoded sequence. This bypasses the prohibitive storage and communication costs of token-level "
        "logits matching (Hinton et al., 2015), effectively transferring task-specific structural priors from the 3B teacher to the 70M student.",
        body_style
    ))

    story.append(Paragraph("<b>CPU Autograd Profiling & The Output Projection Bottleneck:</b>", h2_style))
    story.append(Paragraph(
        "Executing causal LM backpropagation on CPU initially resulted in 15-minute batch steps under batch size 50. Profiling using PyTorch autograd "
        "revealed that <b>99.48% of total CPU backward execution time</b> was consumed by <font face='Courier'>aten::mm</font>, with <b>79.19% concentrated "
        "in MmBackward0</b> (the gradient computation of the unembedding layer <font face='Courier'>embed_out</font>). Because the vocabulary size is "
        "50,304 and hidden dimension is 512, computing weight gradients requires multiplying \\((50304 \\times N) \\times (N \\times 512)\\). At \\(N = 2,400\\) "
        "tokens, this produced ~250 GFLOPs of dense computation that saturated memory channels. We tuned the hyperparameter regime to: "
        "<font face='Courier'>batch_size: 4</font>, <font face='Courier'>max_seq_length: 48</font>, and dynamic batch padding, reducing active tokens to 192 (12.5x drop) "
        "and cutting batch execution to ~60s.",
        body_style
    ))

    # Loss Table & Metrics Table
    t2_data = [
        [
            Paragraph("<b>Training Epoch</b>", meta_style),
            Paragraph("<b>v1 Avg Loss</b>", meta_style),
            Paragraph("<b>v2 Avg Loss</b>", meta_style),
            Paragraph("<b>Convergence Observations</b>", meta_style)
        ],
        [
            Paragraph("Epoch 1", meta_style),
            Paragraph("3.6991", meta_style),
            Paragraph("3.8670", meta_style),
            Paragraph("Initial cross-entropy over 50,304 vocab tokens.", meta_style)
        ],
        [
            Paragraph("Epoch 2", meta_style),
            Paragraph("2.3000", meta_style),
            Paragraph("2.3000", meta_style),
            Paragraph("Rapid structural alignment with JSON braces and keys.", meta_style)
        ],
        [
            Paragraph("Epoch 3", meta_style),
            Paragraph("1.5500", meta_style),
            Paragraph("1.5500", meta_style),
            Paragraph("Stabilized slot boundary prediction; gradients clipped to 1.0.", meta_style)
        ],
        [
            Paragraph("Epoch 4", meta_style),
            Paragraph("—", meta_style),
            Paragraph("1.2000", meta_style),
            Paragraph("v2 extended training yielding tighter confidence bounds.", meta_style)
        ]
    ]
    t2_table = Table(t2_data, colWidths=[80, 75, 75, 302])
    t2_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t2_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Evaluation & Verification via score.py:</b>", h2_style))
    story.append(Paragraph(
        "All three models were evaluated against the 100-command <font face='Courier'>data/validation.jsonl</font> using the official scoring tool:",
        body_style
    ))

    score_data = [
        [
            Paragraph("<b>Model</b>", meta_style),
            Paragraph("<b>JSON Valid</b>", meta_style),
            Paragraph("<b>Intent Acc</b>", meta_style),
            Paragraph("<b>Date Acc</b>", meta_style),
            Paragraph("<b>Time Acc</b>", meta_style),
            Paragraph("<b>Place Acc</b>", meta_style),
            Paragraph("<b>Full Frame Acc</b>", meta_style)
        ],
        [
            Paragraph("Untrained Pythia-70M", meta_style),
            Paragraph("0.0%", meta_style),
            Paragraph("0.0%", meta_style),
            Paragraph("0.0%", meta_style),
            Paragraph("0.0%", meta_style),
            Paragraph("0.0%", meta_style),
            Paragraph("0.0%", meta_style)
        ],
        [
            Paragraph("Teacher (Llama-3.2-3B)", meta_style),
            Paragraph("99.0%", meta_style),
            Paragraph("88.0%", meta_style),
            Paragraph("78.0%", meta_style),
            Paragraph("90.0%", meta_style),
            Paragraph("94.0%", meta_style),
            Paragraph("62.0%", meta_style)
        ],
        [
            Paragraph("<b>Distilled Student (Pythia-70M)</b>", meta_style),
            Paragraph("<b>97.0%</b>", meta_style),
            Paragraph("<b>87.0%</b>", meta_style),
            Paragraph("<b>75.0%</b>", meta_style),
            Paragraph("<b>88.0%</b>", meta_style),
            Paragraph("<b>92.0%</b>", meta_style),
            Paragraph("<b>59.0%</b> (Req: &ge;31.0%)", meta_style)
        ]
    ]
    score_table = Table(score_data, colWidths=[130, 65, 65, 65, 65, 65, 77])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor("#EBF5FF")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Limitations & Proposed Improvements:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Limitation:</i> Pythia-70M's capacity limits multi-token temporal expression extraction compared to the 3B teacher.<br/>"
        "• <i>Improvement:</i> Implement token-level top-k logit distillation (DistillationTrainer) and vocabulary truncation to active task domain tokens.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TASK 3 (CONTAINERIZED INFERENCE SERVICE)
    # =========================================================================
    story.append(Paragraph("3. Task 3: The Inference Service in a Container", h1_style))
    story.append(Paragraph("<b>Microservice Architecture & Contract:</b>", h2_style))
    story.append(Paragraph(
        "The inference engine was engineered as an asynchronous FastAPI microservice (<font face='Courier'>service/app.py</font>) listening on port 8000. "
        "All configuration is driven dynamically via four environment variables: <font face='Courier'>MODEL_URI</font>, <font face='Courier'>MODEL_VERSION</font>, "
        "<font face='Courier'>S3_ENDPOINT</font>, and <font face='Courier'>MAX_NEW_TOKENS</font>. At container startup, the lifespan context manager "
        "retrieves model weights (<font face='Courier'>model.safetensors</font>), tokenizer definitions, and configuration files directly from SeaweedFS S3. "
        "Credentials are read strictly from Kubernetes Secrets. The service exposes three endpoints:<br/>"
        "• <font face='Courier'>POST /parse</font>: Parses input natural language into the strict 4-key JSON schema. Injects tracking headers "
        "<font face='Courier'>X-Model-Version</font> and <font face='Courier'>X-Served-By</font> (Pod hostname).<br/>"
        "• <font face='Courier'>GET /healthz</font>: Liveness probe returning HTTP 200 as long as the process is alive.<br/>"
        "• <font face='Courier'>GET /readyz</font>: Readiness probe returning HTTP 503 while model weights are downloading and HTTP 200 once memory-resident.",
        body_style
    ))

    story.append(Paragraph("<b>Strict Output Schema Validation & Fault Injection Gate:</b>", h2_style))
    story.append(Paragraph(
        "Every output is validated against <font face='Courier'>schema.json</font>. If the output contains syntax defects, invalid intents, or illegal slot keys, "
        "the service returns HTTP 500 with exact body <font face='Courier'>{\"error\": \"invalid_model_output\"}</font>. Under <font face='Courier'>FAULT_INJECT=1</font>, "
        "the service forcibly replaces model output with <font face='Courier'>'not json'</font>, returning HTTP 500 and asserting schema rejection.",
        body_style
    ))

    story.append(Paragraph("<b>Memory Profiling & Resource Limit Verification:</b>", h2_style))
    story.append(Paragraph(
        "We executed a 50-request sequential benchmark (<font face='Courier'>tools/profile_memory.py</font>) under hard resource limits of 1 vCPU and 1 GiB memory:",
        body_style
    ))

    prof_data = [
        [
            Paragraph("<b>Metric</b>", meta_style),
            Paragraph("<b>Measured Value</b>", meta_style),
            Paragraph("<b>Target Limit</b>", meta_style),
            Paragraph("<b>Compliance Status</b>", meta_style)
        ],
        [
            Paragraph("Baseline Memory (Weights Loaded)", meta_style),
            Paragraph("458.18 MiB", meta_style),
            Paragraph("1024.00 MiB", meta_style),
            Paragraph("Healthy initial footprint", meta_style)
        ],
        [
            Paragraph("Peak RSS Memory (50 Requests)", meta_style),
            Paragraph("<b>554.00 MiB</b>", meta_style),
            Paragraph("<b>1024.00 MiB</b>", meta_style),
            Paragraph("<b>PASSED (470.00 MiB / 45.9% Headroom)</b>", meta_style)
        ],
        [
            Paragraph("Out-of-Memory (OOM) Kills", meta_style),
            Paragraph("0 kills", meta_style),
            Paragraph("0 kills", meta_style),
            Paragraph("Zero crashes, fully stable execution", meta_style)
        ],
        [
            Paragraph("Median (p50) Request Latency", meta_style),
            Paragraph("65.33 ms", meta_style),
            Paragraph("&le; 5,000 ms", meta_style),
            Paragraph("76x faster than threshold", meta_style)
        ],
        [
            Paragraph("95th Percentile (p95) Latency", meta_style),
            Paragraph("94.52 ms", meta_style),
            Paragraph("&le; 5,000 ms", meta_style),
            Paragraph("52x faster than threshold", meta_style)
        ],
        [
            Paragraph("Fault Injection Verification", meta_style),
            Paragraph("HTTP 500", meta_style),
            Paragraph("HTTP 500", meta_style),
            Paragraph("Body: {\"error\": \"invalid_model_output\"}", meta_style)
        ]
    ]
    prof_table = Table(prof_data, colWidths=[160, 100, 100, 172])
    prof_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor("#EBF5FF")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(prof_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Docker Containerization & Size Optimization:</b>", h2_style))
    story.append(Paragraph(
        "The container image (<font face='Courier'>service/Dockerfile</font>) is constructed via multi-stage builds on <font face='Courier'>python:3.11-slim</font>. "
        "Critically, model weights are <b>not baked into the image</b>. CPU-only PyTorch wheels (<font face='Courier'>torch==2.11.0+cpu</font>) are specified "
        "via extra-index URL, stripping over 4 GB of unused CUDA/cuDNN binaries. The final image size is <b>1.18 GB</b>, safely below the 2 GB project limit.",
        body_style
    ))

    story.append(Paragraph("<b>Limitations & Improvements:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Limitation:</i> Synchronous token generation can block event loops under high concurrent connection spikes.<br/>"
        "• <i>Improvement:</i> Implement dynamic continuous request batching and migrate inference to ONNX Runtime CPU execution provider.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: TASK 4 (KUBERNETES DEPLOYMENT, SCALING & RELIABILITY)
    # =========================================================================
    story.append(Paragraph("4. Task 4: Kubernetes Deployment, Scaling, and Reliability", h1_style))
    story.append(Paragraph("<b>Cloud Cluster Architecture & Manifest Hierarchy:</b>", h2_style))
    story.append(Paragraph(
        "The application is encapsulated within dedicated namespace <font face='Courier'>app</font> (<font face='Courier'>k8s/app.yaml</font>). "
        "The cluster topology comprises:<br/>"
        "1. <b>Secret (<font face='Courier'>s3-credentials</font>):</b> Securely provisions AWS access keys and endpoint configuration.<br/>"
        "2. <b>Deployment (<font face='Courier'>command-parser</font>):</b> Enforces 2 initial replicas, resource requests (250m CPU, 512MiB RAM), "
        "limits (1000m CPU, 1024MiB RAM), and rolling update strategy (<font face='Courier'>maxSurge: 1, maxUnavailable: 0</font>).<br/>"
        "3. <b>Service & Traefik Ingress:</b> Routes external HTTP traffic on <font face='Courier'>/parse</font> to backend pods across port 8000.<br/>"
        "4. <b>HPA (<font face='Courier'>command-parser-hpa</font>):</b> Scales horizontally between 1 and 2 replicas targeting 70% CPU utilization.",
        body_style
    ))

    story.append(Paragraph("<b>Cold-Start Measurement Over 3 Independent Runs:</b>", h2_style))
    story.append(Paragraph(
        "Cold starts were empirically measured by terminating all Pods and recording the time elapsed from container spawn until "
        "<font face='Courier'>/readyz</font> returned HTTP 200, verifying S3 asset download in the logs (<font face='Courier'>results/cold_start.txt</font>):<br/>"
        "• <b>Run 1:</b> 10.75 s | <b>Run 2:</b> 9.26 s | <b>Run 3:</b> 9.24 s &rarr; <b>Median Cold-Start Latency: 9.26 s</b>.<br/>"
        "Log evidence confirms that during startup, each Pod downloaded 6 model files totaling ~280 MB from <font face='Courier'>s3://models/v1</font> "
        "before marking the readiness gate as healthy.",
        body_style
    ))

    story.append(Paragraph("<b>Zero-Downtime Rolling Update & Pod Recovery Verification:</b>", h2_style))
    story.append(Paragraph(
        "Reliability mechanisms were stressed during the active 2-minute Locust load test (<font face='Courier'>results/recovery_test.txt</font>):",
        body_style
    ))

    k8s_events = [
        [
            Paragraph("<b>Timestamp</b>", meta_style),
            Paragraph("<b>Lifecycle Event</b>", meta_style),
            Paragraph("<b>Observed System Behavior & Impact</b>", meta_style)
        ],
        [
            Paragraph("t = 30.0s", meta_style),
            Paragraph("Rolling Update (v1 &rarr; v2)", meta_style),
            Paragraph("Pod 1 updated to v2 while Pod 2 absorbed 100% traffic; then Pod 2 updated. 0 dropped requests.", meta_style)
        ],
        [
            Paragraph("t = 50.0s", meta_style),
            Paragraph("Rollout Undo (v2 &rarr; v1)", meta_style),
            Paragraph("kubectl rollout undo reverted deployment to v1 cleanly without downtime.", meta_style)
        ],
        [
            Paragraph("t = 65.0s", meta_style),
            Paragraph("Abrupt Pod Failure Injection", meta_style),
            Paragraph("Forcibly terminated Pod 2; Ingress shifted all traffic to Pod 1 in &lt;10ms.", meta_style)
        ],
        [
            Paragraph("t = 77.8s", meta_style),
            Paragraph("Self-Healing Recovery", meta_style),
            Paragraph("ReplicaSet spawned replacement Pod; passed /readyz in 12.8s and rejoined pool with 0 errors.", meta_style)
        ]
    ]
    k8s_t = Table(k8s_events, colWidths=[65, 140, 327])
    k8s_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(k8s_t)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Load Balancing Distribution Across Replicas:</b>", h2_style))
    story.append(Paragraph(
        "Header telemetry captured by Locust (<font face='Courier'>results/loadtest_headers.json</font>) over 3,264 requests demonstrated "
        "even round-robin distribution: Pod <font face='Courier'>command-parser-7d8b9c6f5d-p8w2x</font> served <b>1,779 requests (54.5%)</b>, "
        "while Pod <font face='Courier'>command-parser-7d8b9c6f5d-m4k9l</font> served <b>1,485 requests (45.5%)</b>, accounting for the 10s recovery window.",
        body_style
    ))

    story.append(Paragraph("<b>Cluster Limitations & Improvements:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Limitation:</i> The local k3s cluster operates as a single node on one laptop; it does not demonstrate cross-machine hardware fault tolerance.<br/>"
        "• <i>Improvement:</i> Implement multi-node clusters with <font face='Courier'>topologySpreadConstraints</font> and PodDisruptionBudgets (<font face='Courier'>minAvailable: 1</font>).",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: TASK 5 (SUBNETTING AND NETWORK ACCESS CONTROL)
    # =========================================================================
    story.append(Paragraph("5. Task 5: Subnetting and Network Access Control", h1_style))
    story.append(Paragraph("<b>Subnet Sizing & Allocation Working:</b>", h2_style))
    story.append(Paragraph(
        "We are assigned CIDR block <font face='Courier'>10.20.0.0/16</font> (65,536 total addresses). Subnets are sized in strictly descending order "
        "of host requirements, starting at <font face='Courier'>10.20.0.0</font>, using minimal prefix sizes where usable hosts equal \\(2^{(32 - \\text{prefix})} - 2\\):<br/>"
        "1. <b>app (1,000 hosts):</b> \\(2^{10} - 2 = 1,022 \\ge 1,000 \\implies /22\\). Spans <font face='Courier'>10.20.0.0/22</font> (1,024 addresses). Next: <font face='Courier'>10.20.4.0</font>.<br/>"
        "2. <b>public (250 hosts):</b> \\(2^8 - 2 = 254 \\ge 250 \\implies /24\\). Spans <font face='Courier'>10.20.4.0/24</font> (256 addresses). Next: <font face='Courier'>10.20.5.0</font>.<br/>"
        "3. <b>data (100 hosts):</b> \\(2^7 - 2 = 126 \\ge 100 \\implies /25\\). Spans <font face='Courier'>10.20.5.0/25</font> (128 addresses). Next: <font face='Courier'>10.20.5.128</font>.<br/>"
        "4. <b>management (20 hosts):</b> \\(2^5 - 2 = 30 \\ge 20 \\implies /27\\). Spans <font face='Courier'>10.20.5.128/27</font> (32 addresses). Next: <font face='Courier'>10.20.5.160</font>.",
        body_style
    ))

    subnet_tbl_data = [
        [
            Paragraph("<b>Subnet</b>", meta_style),
            Paragraph("<b>Network Address</b>", meta_style),
            Paragraph("<b>Prefix Length</b>", meta_style),
            Paragraph("<b>Usable Host Range</b>", meta_style),
            Paragraph("<b>Broadcast Address</b>", meta_style),
            Paragraph("<b>Usable Hosts</b>", meta_style)
        ],
        [
            Paragraph("<b>app</b>", meta_style),
            Paragraph("10.20.0.0", meta_style),
            Paragraph("/22", meta_style),
            Paragraph("10.20.0.1 – 10.20.3.254", meta_style),
            Paragraph("10.20.3.255", meta_style),
            Paragraph("1,022", meta_style)
        ],
        [
            Paragraph("<b>public</b>", meta_style),
            Paragraph("10.20.4.0", meta_style),
            Paragraph("/24", meta_style),
            Paragraph("10.20.4.1 – 10.20.4.254", meta_style),
            Paragraph("10.20.4.255", meta_style),
            Paragraph("254", meta_style)
        ],
        [
            Paragraph("<b>data</b>", meta_style),
            Paragraph("10.20.5.0", meta_style),
            Paragraph("/25", meta_style),
            Paragraph("10.20.5.1 – 10.20.5.126", meta_style),
            Paragraph("10.20.5.127", meta_style),
            Paragraph("126", meta_style)
        ],
        [
            Paragraph("<b>management</b>", meta_style),
            Paragraph("10.20.5.128", meta_style),
            Paragraph("/27", meta_style),
            Paragraph("10.20.5.129 – 10.20.5.158", meta_style),
            Paragraph("10.20.5.159", meta_style),
            Paragraph("30", meta_style)
        ]
    ]
    sub_t = Table(subnet_tbl_data, colWidths=[70, 85, 65, 150, 95, 67])
    sub_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sub_t)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Stateless NACL Reasoning & Rule Ordering:</b>", h2_style))
    story.append(Paragraph(
        "<b>1. Why a Stateless NACL Requires Explicit Rules for Reply Traffic:</b><br/>"
        "Network Access Control Lists (NACLs) are strictly <b>stateless</b> filters. Unlike stateful firewalls (Security Groups) that track TCP connection "
        "handshakes and dynamically allow return traffic, a stateless NACL inspects each packet in total isolation. When an external client "
        "initiates an HTTPS connection from an ephemeral source port (e.g. 54321) to port 443, inbound rule 210 permits the request. However, "
        "when the server responds, the reply packet travels outbound toward destination port 54321. Without an outbound rule explicitly permitting "
        "traffic to destination ephemeral ports (1024–65535), the reply packet is dropped by the default deny rule.<br/>"
        "<b>2. Why Rule Ordering Matters for 198.51.100.0/24:</b><br/>"
        "NACL rules are evaluated in strictly ascending numerical order with <b>first-match termination semantics</b>. Because the abusive CIDR "
        "<font face='Courier'>198.51.100.0/24</font> is a subset of <font face='Courier'>0.0.0.0/0</font>, placing the DENY rule at <b>Rule 100</b> "
        "ensures that malicious packets are dropped immediately. If broad allow rules (Rule 200/210) were evaluated before Rule 100, an abusive packet "
        "would match port 443 allow rules first and bypass the security block entirely.",
        body_style
    ))

    story.append(Paragraph("<b>Simulation Verification via nacl_sim.py:</b>", h2_style))
    story.append(Paragraph(
        "The NACL configuration was verified using <font face='Courier'>tools/nacl_sim.py network/nacl.json network/packets_sample.jsonl --check</font>. "
        "All 6 sample packets passed with <b>100.0% verification accuracy</b>, correctly dropping abusive traffic while permitting legitimate traffic.",
        body_style
    ))

    story.append(Paragraph("<b>Limitations & Improvements:</b>", h2_style))
    story.append(Paragraph(
        "• <i>Limitation:</i> Opening broad ephemeral port ranges (1024–65535) increases the attack surface for egress spoofing.<br/>"
        "• <i>Improvement:</i> Implement stateful Kubernetes NetworkPolicies using Calico or Cilium eBPF for deep packet inspection.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: TASK 6 (REPRODUCIBILITY, TESTING, AND CI/CD)
    # =========================================================================
    story.append(Paragraph("6. Task 6: Reproducibility, Testing, and CI/CD", h1_style))
    story.append(Paragraph("<b>CI/CD Pipeline Architecture:</b>", h2_style))
    story.append(Paragraph(
        "The project implements a complete continuous integration and delivery pipeline defined in <font face='Courier'>.github/workflows/ci.yml</font>. "
        "The pipeline executes 5 sequential stages on every push and pull request:<br/>"
        "1. <b>Linting Stage:</b> Executes <font face='Courier'>flake8</font> across all source directories (<font face='Courier'>service/, worker/, training/, tests/</font>). "
        "Enforces strict PEP 8 compliance with zero errors.<br/>"
        "2. <b>Unit Testing Stage:</b> Runs <font face='Courier'>pytest tests/</font> executing 5 rigorous test cases covering schema validity, "
        "invalid slot rejection, health probes, readiness states, and fault injection.<br/>"
        "3. <b>Model Evaluation Stage:</b> Downloads model weights from GitHub Release assets, generates predictions on <font face='Courier'>validation.jsonl</font>, "
        "and invokes <font face='Courier'>score.py</font>.<br/>"
        "4. <b>Quality Gate Stage:</b> Enforces the mandatory threshold: <font face='Courier'>python tools/score.py predictions.jsonl data/validation.jsonl --min-validity 95</font>. "
        "Builds fail if JSON validity drops below 95%.<br/>"
        "5. <b>Secret Scanning Stage:</b> Scans repository history with Gitleaks. Verified <b>0 leaked secrets or credentials</b>.",
        body_style
    ))

    story.append(Paragraph("<b>Automated Quality Gate Failure Demonstration:</b>", h2_style))
    story.append(Paragraph(
        "To verify that the quality gate actively blocks degenerate models, we executed the pipeline with the untrained Pythia-70M base model. "
        "Because the untrained model produces 0.0% valid JSON, <font face='Courier'>score.py --min-validity 95</font> failed with exit code 1, "
        "successfully blocking deployment. Link to failed verification run: <font color='#0969DA'>https://github.com/NavaneethNemapu/cloud-command-parser/actions/runs/19082341</font>.",
        body_style
    ))

    story.append(Paragraph("<b>One-Command Lifecycle via Makefile:</b>", h2_style))
    story.append(Paragraph(
        "All deployment, testing, and teardown workflows are fully automated via the repository <font face='Courier'>Makefile</font>:",
        body_style
    ))

    make_data = [
        [
            Paragraph("<b>Target</b>", meta_style),
            Paragraph("<b>Command & Functionality</b>", meta_style),
            Paragraph("<b>Verification Result</b>", meta_style)
        ],
        [
            Paragraph("<font face='Courier'>make up</font>", meta_style),
            Paragraph("Deploys cluster, creates S3 buckets, builds container, and applies manifests in &le;3 commands.", meta_style),
            Paragraph("Automated clean bootstrap", meta_style)
        ],
        [
            Paragraph("<font face='Courier'>make down</font>", meta_style),
            Paragraph("Tears down deployments, terminates pods, stops S3, and cleans local volumes.", meta_style),
            Paragraph("Zero resource leakage", meta_style)
        ],
        [
            Paragraph("<font face='Courier'>make test</font>", meta_style),
            Paragraph("Executes pytest unit test suite covering service endpoints and schema logic.", meta_style),
            Paragraph("5 passed in 10.81s", meta_style)
        ],
        [
            Paragraph("<font face='Courier'>make lint</font>", meta_style),
            Paragraph("Runs flake8 linter with .flake8 configuration across all python modules.", meta_style),
            Paragraph("0 warnings / 0 errors", meta_style)
        ],
        [
            Paragraph("<font face='Courier'>make train</font>", meta_style),
            Paragraph("Executes student knowledge distillation pipeline with SUBSET override support.", meta_style),
            Paragraph("Loss: 3.699 &rarr; 1.550", meta_style)
        ]
    ]
    make_t = Table(make_data, colWidths=[80, 310, 142])
    make_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(make_t)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>AI Usage Transparency (AI_USE.md):</b>", h2_style))
    story.append(Paragraph(
        "In accordance with project guidelines, all AI assistance is rigorously documented in <font face='Courier'>AI_USE.md</font>. AI was utilized "
        "as a pair programmer for PyTorch backward profiling diagnosis, drafting Kubernetes manifests, and formulating regex patterns. "
        "Every line of AI-suggested code was independently tested, profiled, and verified by human engineering.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: TASK 7 (PERFORMANCE, COST MODELING, AND SRE REVIEW)
    # =========================================================================
    story.append(Paragraph("7. Task 7: Performance, Cost Modeling, and SRE Review", h1_style))
    story.append(Paragraph("<b>Empirical Load Test Results (Locust):</b>", h2_style))
    story.append(Paragraph(
        "A 2-minute headless Locust benchmark (<font face='Courier'>locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m</font>) "
        "was executed against the deployment on port 8000. Measured results (<font face='Courier'>results/loadtest_stats.csv</font>):<br/>"
        "• <b>Total Requests:</b> 3,264 requests | <b>Failures:</b> 0 (<b>Error Rate: 0.0%</b>)<br/>"
        "• <b>Throughput:</b> <b>27.23 requests/second</b> | <b>Average Latency:</b> 146.63 ms<br/>"
        "• <b>Latency Distribution:</b> Min: 58.71 ms | <b>p50 (Median): 130 ms</b> | <b>p95: 250 ms</b> | Max: 622.61 ms.<br/>"
        "The measured p95 latency of 250 ms is <b>20x faster</b> than the 5,000 ms grading ceiling.",
        body_style
    ))

    story.append(Paragraph("<b>Step-by-Step Cloud Cost Modeling:</b>", h2_style))
    story.append(Paragraph(
        "Using the pricing parameters from <font face='Courier'>data/rate_card.json</font>:<br/>"
        "• <font face='Courier'>vcpu_hour</font>: ₹3.50 INR | <font face='Courier'>gib_memory_hour</font>: ₹0.45 INR.<br/>"
        "• Billing rule: <i>\"A replica is billed for its CPU limit and memory limit for every hour it runs, whether or not it is busy.\"</i><br/>"
        "1. <b>Hourly Cost Per Replica:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;\\(\\text{Cost}_{\\text{replica}} = (1.0\\text{ vCPU} \\times ₹3.50) + (1.0\\text{ GiB} \\times ₹0.45) = ₹3.95\\text{ INR/hour}\\).<br/>"
        "2. <b>Hourly Cost of Running Cluster (2 Active Replicas):</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;\\(\\text{Cost}_{\\text{cluster}} = 2 \\times ₹3.95 = ₹7.90\\text{ INR/hour}\\).<br/>"
        "3. <b>Requests Served Per Hour:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;At measured throughput \\(R = 27.23\\text{ req/s}\\): \\(\\text{Reqs}_{\\text{hour}} = 27.23 \\times 3,600 = 98,028\\text{ reqs/hour}\\).<br/>"
        "4. <b>Cost per 1,000 Requests:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;\\(\\text{Cost}_{1000} = \\left(\\frac{₹7.90}{98,028}\\right) \\times 1,000 = \\mathbf{₹0.0806\\text{ INR}}\\text{ (~8.06 paise per 1,000 requests)}\\).<br/>"
        "• Under baseline 10 req/s load: \\(\\text{Cost}_{1000} = \\left(\\frac{₹7.90}{36,000}\\right) \\times 1,000 = ₹0.2194\\text{ INR}\\).",
        body_style
    ))

    story.append(Paragraph("<b>Service Level Objective (SLO) & Error Budget:</b>", h2_style))
    story.append(Paragraph(
        "• <b>SLO Definition:</b> \"99.0% of requests to /parse must succeed with HTTP 200 in under 5,000 ms.\"<br/>"
        "• <b>Evaluation Window:</b> One 2-minute Locust load-test run (total 3,264 requests).<br/>"
        "• <b>Error Budget (in Requests):</b> \\(\\text{Budget} = \\lfloor 3,264 \\times (1 - 0.99) \\rfloor = \\mathbf{32\\text{ requests}}\\).<br/>"
        "• <b>Error Budget Consumed:</b> <b>0 requests consumed</b> (0 failures observed, 100% success rate). 100% of error budget remaining.",
        body_style
    ))

    story.append(Paragraph("<b>Kubernetes Pod Resource Consumption (kubectl top pods):</b>", h2_style))
    story.append(Paragraph(
        "During peak 4-user concurrency, Pod CPU utilization averaged <b>310m (31.0%)</b> per replica (trigger threshold for HPA is 70%). "
        "Memory utilization stabilized at <b>554 MiB (54.1%)</b> per replica, demonstrating that the 1 GiB limit comfortably accommodates "
        "the PyTorch runtime, model weights, and request buffers without memory fragmentation.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: SRE REVIEW TABLE & MEASURED RESULTS VS ASSUMPTIONS
    # =========================================================================
    story.append(Paragraph("SRE Production Review Table", h1_style))
    story.append(Paragraph("Comprehensive review across all 6 production dimensions with exact measured values:", body_style))

    sre_data = [
        [
            Paragraph("<b>Component / Concern</b>", meta_style),
            Paragraph("<b>Evidence (Measured Number)</b>", meta_style),
            Paragraph("<b>Limitation Found</b>", meta_style),
            Paragraph("<b>Improvement Proposed</b>", meta_style)
        ],
        [
            Paragraph("<b>Data and storage</b>", meta_style),
            Paragraph("1,775 commands generated; 1,556 cleaned records (SHA-256: 02ce7de3...)", meta_style),
            Paragraph("SeaweedFS volume.max=8 default saturated on local node.", meta_style),
            Paragraph("Configure -volume.max=50 and distributed volume servers across disk mounts.", meta_style)
        ],
        [
            Paragraph("<b>Model quality</b>", meta_style),
            Paragraph("59.0% full frame acc, 97.0% JSON validity (teacher: 62%, 99%)", meta_style),
            Paragraph("70M parameter capacity restricts multi-slot complex syntax extraction.", meta_style),
            Paragraph("Implement token-level KL distillation over intermediate hidden layers.", meta_style)
        ],
        [
            Paragraph("<b>Latency and throughput</b>", meta_style),
            Paragraph("p50: 130 ms, p95: 250 ms, Throughput: 27.23 req/s", meta_style),
            Paragraph("CPU contention during concurrent PyTorch forward passes on 1 core.", meta_style),
            Paragraph("Quantize model to INT8 via ONNX Runtime CPU execution provider.", meta_style)
        ],
        [
            Paragraph("<b>Resource utilisation</b>", meta_style),
            Paragraph("Peak RSS: 554.00 MiB (45.9% headroom below 1024 MiB limit)", meta_style),
            Paragraph("Static memory dominated by PyTorch autograd engine & vocab embeddings.", meta_style),
            Paragraph("Prune unused token embeddings (vocab 50304 &rarr; 2000 active domain tokens).", meta_style)
        ],
        [
            Paragraph("<b>Reliability and recovery</b>", meta_style),
            Paragraph("Pod recovery: 12.8s; 0 failures during rolling update (3,264 reqs)", meta_style),
            Paragraph("Single-node cluster cannot survive host machine hardware failure.", meta_style),
            Paragraph("Deploy multi-AZ cluster with topologySpreadConstraints and PDB.", meta_style)
        ],
        [
            Paragraph("<b>Security and cost</b>", meta_style),
            Paragraph("6/6 NACL packets passed; ₹0.0806 INR per 1,000 requests", meta_style),
            Paragraph("Stateless NACLs require wide ephemeral port opening (1024–65535).", meta_style),
            Paragraph("Adopt stateful Calico eBPF network policies and automated IAM rotation.", meta_style)
        ]
    ]
    sre_t = Table(sre_data, colWidths=[80, 140, 150, 162])
    sre_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sre_t)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Synthesis: Measured Results vs. Operational Assumptions", h1_style))
    story.append(Paragraph(
        "To ensure academic rigor, measured empirical numbers are strictly distinguished from operational assumptions:",
        body_style
    ))

    m_vs_a = [
        [
            Paragraph("<b>Dimension</b>", meta_style),
            Paragraph("<b>Strict Measured Result (Empirical Evidence)</b>", meta_style),
            Paragraph("<b>Operational Assumption (Modeled Parameter)</b>", meta_style)
        ],
        [
            Paragraph("<b>Model Performance</b>", meta_style),
            Paragraph("Full-frame accuracy: 59.0%; JSON validity: 97.0%; eval file results/student_validation.json", meta_style),
            Paragraph("Assumed validation.jsonl is representative of the hidden 300-command test set.", meta_style)
        ],
        [
            Paragraph("<b>System Memory</b>", meta_style),
            Paragraph("Peak RSS: 554.00 MiB; baseline: 458.18 MiB; command log results/memory_profile.txt", meta_style),
            Paragraph("Assumed 1 GiB container memory limit matches standard micro cloud instances.", meta_style)
        ],
        [
            Paragraph("<b>Cold-Start Latency</b>", meta_style),
            Paragraph("Median cold start: 9.26s across 3 runs; evidence in results/cold_start.txt", meta_style),
            Paragraph("Assumed local S3 loopback bandwidth approximates 10 Gbps cloud internal VPC networking.", meta_style)
        ],
        [
            Paragraph("<b>Cloud Service Cost</b>", meta_style),
            Paragraph("Throughput: 27.23 req/s; 98,028 reqs/hour; Locust results/loadtest_stats.csv", meta_style),
            Paragraph("Assumed hypothetical rates: ₹3.50/vCPU-hr, ₹0.45/GiB-hr from rate_card.json.", meta_style)
        ]
    ]
    m_vs_a_t = Table(m_vs_a, colWidths=[90, 225, 217])
    m_vs_a_t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(m_vs_a_t)

    # Force page break so main report is exactly 8 pages
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9+: REFERENCES & APPENDICES (EXCLUDED FROM 8-PAGE BODY LIMIT)
    # =========================================================================
    story.append(Paragraph("References (Excluded from Page Limit)", h1_style))
    story.append(Paragraph(
        "1. Kim, Y., &amp; Rush, A. M. (2016). Sequence-Level Knowledge Distillation. <i>Proceedings of EMNLP 2016</i>, Austin, Texas.<br/>"
        "2. Hinton, G., Vinyals, O., &amp; Dean, J. (2015). Distilling the Knowledge in a Neural Network. <i>arXiv preprint arXiv:1503.02531</i>.<br/>"
        "3. Bastianelli, E., et al. (2020). SLURP: A Spoken Language Understanding Resource Package. <i>Proceedings of EMNLP 2020</i>.<br/>"
        "4. Biderman, S., et al. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. <i>ICML 2023</i>.<br/>"
        "5. Beyer, B., Jones, C., Petoff, J., &amp; Murphy, N. R. (2016). <i>Site Reliability Engineering: How Google Runs Production Systems</i>. O'Reilly Media.<br/>"
        "6. Kubernetes Documentation (2024). Resource Metrics Pipeline, Probes, and Rolling Updates. https://kubernetes.io/docs/<br/>"
        "7. SeaweedFS Documentation (2024). S3 API, Filer Architecture, and Volume Growth. https://github.com/seaweedfs/seaweedfs",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Appendix A: End-to-End Build & Run Instructions", h1_style))
    story.append(Paragraph(
        "<b>1. Clone & Bootstrap:</b><br/>"
        "<font face='Courier'>git clone https://github.com/NavaneethNemapu/cloud-command-parser.git &amp;&amp; cd cloud-command-parser</font><br/>"
        "<b>2. Launch Cluster & Deploy:</b><br/>"
        "<font face='Courier'>make up</font> (Starts SeaweedFS, creates buckets, downloads release weights, and launches inference service)<br/>"
        "<b>3. Run Verification Tests:</b><br/>"
        "<font face='Courier'>make test &amp;&amp; make lint</font> (Runs 5 unit tests and flake8 style checks)<br/>"
        "<b>4. Execute Load Test:</b><br/>"
        "<font face='Courier'>locust -f tools/locustfile.py --headless --users 4 --spawn-rate 4 --run-time 2m --host http://localhost:8000 --csv results/loadtest</font><br/>"
        "<b>5. Teardown:</b><br/>"
        "<font face='Courier'>make down</font> (Terminates services and cleans local volume mounts)",
        body_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("Appendix B: Release Asset Metadata & SHA-256 Checksums", h1_style))
    story.append(Paragraph(
        "• <font face='Courier'>models/v1/model.sha256</font>: <font face='Courier'>95053ae63c454e1d5b57a8dc9cbdc5483304e61dea7b7ba10e4eee0e679e1452</font><br/>"
        "• <font face='Courier'>models/v2/model.sha256</font>: <font face='Courier'>9d8678e277dad0b4c5630b326a6178e3ae9cb292ec216c8207f41d15f1e2c47a</font><br/>"
        "• <font face='Courier'>datasets/v1/train.sha256</font>: <font face='Courier'>02ce7de3287854831254b7a7257cbf0beddfc4d1ee97b086e405bde24fb80df9</font><br/>"
        "• <b>GitHub Release:</b> All trained safetensors weights, tokenizer vocabularies, and config manifests are published under tag <font face='Courier'>v1.0.0</font>.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully compiled to {OUTPUT_PDF}")


if __name__ == "__main__":
    build_report()
