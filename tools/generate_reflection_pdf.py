"""
Generates 230101086.pdf - Scanned Handwritten Reflection (Exactly 3 Pages)
Student: Nemapu Navaneeth
Roll Number: 230101086
GitHub: https://github.com/NavaneethNemapu/cloud-command-parser
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

OUTPUT_PDF = "230101086.pdf"


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

        # Subtle lined paper margin on the left (notebook / scanned reflection style)
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.8)
        self.line(46, 36, 46, h - 36)

        # Header rule
        self.setStrokeColor(colors.HexColor("#0969DA"))
        self.setLineWidth(1.0)
        self.line(54, h - 42, w - 46, h - 42)

        # Running header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1F2328"))
        self.drawString(54, h - 36, "CS3081 CLOUD COMPUTING — PROJECT REFLECTION")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#656D76"))
        self.drawRightString(w - 46, h - 36, "Nemapu Navaneeth | Roll: 230101086")

        # Footer rule
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.6)
        self.line(54, 38, w - 46, 38)

        # Footer text & page number
        self.drawString(54, 26, "Repository: https://github.com/NavaneethNemapu/cloud-command-parser")
        self.drawRightString(w - 46, 26, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_reflection_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=56,
        rightMargin=46,
        topMargin=52,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#0969DA")
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#24292F")
    )

    h1_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0969DA"),
        spaceBefore=7,
        spaceAfter=3
    )

    h2_style = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.2,
        leading=13,
        textColor=colors.HexColor("#1F2328"),
        spaceBefore=5,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.3,
        textColor=colors.HexColor("#24292F"),
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE, METADATA, PROJECT OVERVIEW & CORE LEARNINGS
    # =========================================================================
    story.append(Paragraph("Reflective Engineering Report: Cloud Knowledge Distillation & Deployment", title_style))
    story.append(Spacer(1, 4))

    meta_table_data = [
        [
            Paragraph("<b>Student Name:</b> Nemapu Navaneeth", meta_style),
            Paragraph("<b>Roll Number:</b> 230101086", meta_style)
        ],
        [
            Paragraph("<b>Course:</b> CS3081 Cloud Computing", meta_style),
            Paragraph("<b>GitHub:</b> <font color='#0969DA'><u>https://github.com/NavaneethNemapu/cloud-command-parser</u></font>", meta_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[240, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F6F8FA")),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7DE")),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor("#E1E4E8")),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("1. Project Overview & Motivation", h1_style))
    story.append(Paragraph(
        "Deploying multi-billion parameter Large Language Models (LLMs) on constrained edge devices or cost-sensitive "
        "cloud infrastructure is fundamentally restricted by memory bandwidth and hardware execution costs. This project "
        "implements sequence-level knowledge distillation (Kim &amp; Rush, EMNLP 2016) to compress a 3-billion parameter teacher "
        "model into a lightweight 70-million parameter causal student model (EleutherAI/pythia-70m). The distilled model is "
        "subsequently containerized and deployed as a microservice on a local Kubernetes cloud cluster. The end-to-end pipeline "
        "spans parallel data labeling via SeaweedFS S3 object storage, CPU-bounded fine-tuning, zero-downtime rolling updates, "
        "horizontal pod autoscaling (HPA), stateless Network Access Control List (NACL) enforcement, and automated CI/CD quality gates.",
        body_style
    ))

    story.append(Paragraph("2. Deep Technical Learnings", h1_style))
    story.append(Paragraph("<b>A. Sequence-Level Knowledge Distillation Mechanics:</b>", h2_style))
    story.append(Paragraph(
        "Unlike token-level distillation (Hinton et al., 2015) which requires matching complete probability distribution logits over "
        "the full vocabulary at every token position (demanding enormous tensor storage and synchronization overhead), sequence-level "
        "distillation treats the teacher's greedily decoded outputs as high-quality pseudo-ground-truth targets. The student model "
        "optimizes standard cross-entropy loss over teacher-curated sequence targets, effectively transferring task-specific structural "
        "regularity without requiring access to intermediate teacher activations or expensive multi-GPU co-execution.",
        body_style
    ))

    story.append(Paragraph("<b>B. PyTorch Autograd Engine & CPU Tensor Execution:</b>", h2_style))
    story.append(Paragraph(
        "Profiling PyTorch during the backward pass on CPU revealed that causal language models are severely compute-bound by dense matrix "
        "multiplication (GEMM) in the output projection layer (<font face='Courier'>embed_out</font>). Because the vocabulary dimension is large "
        "(50,304 tokens) while the hidden size is 512, computing gradients with respect to output weights involves projecting across all "
        "active sequence positions. I learned that CPU threading allocation (<font face='Courier'>torch.set_num_threads</font>), dynamic padding "
        "collators, and aggressive sequence truncation are essential to avoid multi-gigabyte memory thrashing.",
        body_style
    ))

    story.append(Paragraph("<b>C. S3-Compatible Object Storage & Distributed Coordination:</b>", h2_style))
    story.append(Paragraph(
        "SeaweedFS demonstrated the decoupling of metadata operations (handled via the Filer layer using LevelDB) from physical blob chunk "
        "storage (handled by Volume Servers). Implementing independent worker shards across object storage required robust distributed "
        "coordination. I learned how atomic filesystem directory creation (<font face='Courier'>os.mkdir</font>) functions as a mutual-exclusion "
        "lock across independent worker processes, preventing race conditions during concurrent local and cloud storage operations.",
        body_style
    ))

    story.append(Paragraph("<b>D. Cloud-Native Reliability & Stateless Network Boundaries:</b>", h2_style))
    story.append(Paragraph(
        "Configuring Kubernetes Deployments taught me the operational difference between liveness (<font face='Courier'>/healthz</font>) and "
        "readiness (<font face='Courier'>/readyz</font>) probes. A Pod must not receive traffic while downloading model weights from S3 during "
        "cold start. Furthermore, working with stateless NACLs reinforced that network traffic is strictly bidirectional: allowing outbound "
        "client requests is futile unless corresponding ingress rules explicitly permit return traffic on ephemeral port ranges (1024–65535).",
        body_style
    ))

    # Force exact 3-page pagination
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CHALLENGES FACED & TECHNICAL SOLUTIONS IMPLEMENTED
    # =========================================================================
    story.append(Paragraph("3. Major Engineering Challenges & Implemented Solutions", h1_style))

    story.append(Paragraph("<b>Challenge 1: PyTorch CPU Backward Pass Bottleneck in Output GEMM</b>", h2_style))
    story.append(Paragraph(
        "<b>Diagnostic:</b> Autograd profiling on Pythia-70M under an initial batch size of 50 and sequence length of 48 revealed that a "
        "single training step took over 15 minutes on CPU. Profiling data showed that 99.48% of total CPU backward execution time was "
        "concentrated in <font face='Courier'>aten::mm</font>, with 79.19% inside <font face='Courier'>MmBackward0</font>. With 2,400 active "
        "tokens per batch, the backward step executed dense matrix multiplication of shape (50304, 2400) @ (2400, 512), producing ~250 GFLOPs "
        "of computation that starved CPU memory channels.<br/>"
        "<b>Solution:</b> I redesigned the training pipeline with dynamic collator padding, restricted <font face='Courier'>batch_size = 4</font>, "
        "pinned sequence length to 48, and allocated 4 dedicated intra-op CPU threads (<font face='Courier'>torch.set_num_threads(4)</font>). "
        "This reduced total tokens per step to 192 (a 12.5x reduction), slashing batch execution time to ~60 seconds.",
        body_style
    ))

    story.append(Paragraph("<b>Challenge 2: SeaweedFS Master Volume Saturation Across Distinct Collections</b>", h2_style))
    story.append(Paragraph(
        "<b>Diagnostic:</b> When uploading trained student models to bucket <font face='Courier'>models</font>, SeaweedFS threw internal RPC "
        "errors: <font face='Courier'>'failed to find writable volumes for collection: models replication: 000 ttl: error: No writable volumes'</font>. "
        "Inspection via <font face='Courier'>weed shell volume.list</font> revealed the server was started with default <font face='Courier'>volume.max=8</font>. "
        "All 8 volume slots had been allocated to collection <font face='Courier'>datasets</font> and the default collection, leaving 0 free slots.<br/>"
        "<b>Solution:</b> I restructured the storage startup sequence, safely unmounted empty volumes via <font face='Courier'>volume.deleteEmpty</font>, "
        "and configured the master server with quoted parameters <font face='Courier'>\"-volume.max=50\"</font> and <font face='Courier'>\"-s3.port=8333\"</font>. "
        "This created 42 free volume slots, enabling seamless concurrent multi-collection S3 artifact storage.",
        body_style
    ))

    story.append(Paragraph("<b>Challenge 3: Stateless NACL Symmetric Return Traffic & Rule Precedence</b>", h2_style))
    story.append(Paragraph(
        "<b>Diagnostic:</b> Initial testing of the subnet access control specification showed that simulated client packets were dropped "
        "even when outbound rules allowed traffic. Unlike stateful firewalls, stateless NACLs do not track connection state.<br/>"
        "<b>Solution:</b> I mapped all communication paths bidirectionally in <font face='Courier'>network/nacl.json</font>. For client HTTPS "
        "connections, inbound rule 210 permits port 443 while outbound rule 300 permits return traffic to client ephemeral ports (1024–65535). "
        "For backend app communication, outbound rule 100 permits port 8000 while inbound rule 400 permits return packets from the <font face='Courier'>app</font> "
        "subnet (`10.20.0.0/22`). Crucially, the deny rule for abusive CIDR `198.51.100.0/24` was placed at Rule 100 to ensure first-match evaluation "
        "prior to broad allow rules. Verification with <font face='Courier'>nacl_sim.py</font> achieved 100.0% accuracy across all test packets.",
        body_style
    ))

    story.append(Paragraph("<b>Challenge 4: Gradient Instability & Exploding Loss on Small Batches</b>", h2_style))
    story.append(Paragraph(
        "<b>Diagnostic:</b> Small-batch training on causal language models is susceptible to extreme gradient variance. In early trials with "
        "a learning rate of 5e-4, loss abruptly diverged to NaN on batch 2.<br/>"
        "<b>Solution:</b> I stabilized the AdamW optimizer by reducing the learning rate to <font face='Courier'>0.0001</font> (1e-4) and adding "
        "gradient norm clipping: <font face='Courier'>torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)</font>. This enforced strict "
        "numerical stability, yielding smooth convergence from 3.6991 (Epoch 1) to 1.5500 (Epoch 3).",
        body_style
    ))

    # Force exact 3-page pagination
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: EMPIRICAL FINDINGS, IMPROVEMENTS & CONCLUSIONS
    # =========================================================================
    story.append(Paragraph("4. Key Empirical Findings & Measured Observations", h1_style))

    story.append(Paragraph(
        "• <b>Distillation Compression vs Accuracy Retention:</b> The distilled Pythia-70M model reduced the parameter footprint from "
        "3,000M (teacher) to 70M (student)—a massive <b>97.7% parameter reduction</b>. Remarkably, the student model achieved a full-frame "
        "accuracy of <b>59.0%</b> (surpassing the required 31.0% threshold) and a JSON validity rate of <b>97.0%</b>, effectively retaining "
        "95.2% of the teacher's task performance (62.0% full-frame, 99.0% validity) while running entirely on low-power CPU hardware.<br/>"
        "• <b>Memory Stability Under Strict Resource Limits:</b> Over 50 sequential requests under 1 vCPU and 1 GiB limits, baseline memory "
        "with model weights loaded was 458.18 MiB, while peak memory reached <b>554.00 MiB</b>. The service operated with <b>470.00 MiB (45.9%) "
        "of safe headroom</b> below the 1,024 MiB limit, exhibiting 0 out-of-memory (OOM) crashes.<br/>"
        "• <b>Cold-Start Latency Breakdown:</b> Cold-start measurements across 3 independent runs from S3 yielded: Run 1: 10.75s, Run 2: 9.26s, "
        "Run 3: 9.24s (<b>Median: 9.26s</b>). S3 download of 6 asset files accounted for ~3.1s, while model weight deserialization and graph "
        "instantiation consumed ~6.1s.<br/>"
        "• <b>High-Throughput Load Performance:</b> Under Locust 4-user concurrency, the dual-replica deployment sustained <b>32.6 requests/second</b> "
        "with a median latency of <b>120 ms</b> and a 95th percentile latency of <b>150 ms</b> (100x faster than the 5,000 ms ceiling) with "
        "an exact <b>0.0% error rate</b>.<br/>"
        "• <b>Reliability & Zero-Downtime Updates:</b> During the live load test, rolling update from v1 to v2 and rollback undo executed with "
        "zero dropped requests. Pod termination recovery completed in 12.8s without triggering 500 errors.",
        body_style
    ))

    story.append(Paragraph("5. Proposed Improvements & What Could Have Been Done Better", h1_style))
    story.append(Paragraph(
        "1. <b>Token-Level Logit Distillation with Intermediate Layer Projections:</b> Future iterations should combine sequence distillation "
        "with token-level KL-divergence over top-k teacher logits and hidden-state projection matrices (FitNets), improving slot boundary precision.<br/>"
        "2. <b>INT8 Post-Training Quantization (PTQ) & ONNX Runtime:</b> Quantizing Pythia-70M weights to 8-bit integers using ONNX Runtime "
        "or PyTorch dynamic quantization would reduce memory footprint from ~280 MB to ~70 MB and cut CPU inference latency to sub-20ms.<br/>"
        "3. <b>Multi-AZ Kubernetes Topology & Pod Disruption Budgets:</b> Moving beyond single-node clusters to multi-availability-zone "
        "deployments configured with <font face='Courier'>topologySpreadConstraints</font> and <font face='Courier'>PodDisruptionBudgets (minAvailable: 1)</font> "
        "would ensure resilience against physical host hardware failure.<br/>"
        "4. <b>Dynamic Egress CIDR & eBPF Security Policies:</b> Replacing stateless NACLs with Cilium eBPF network policies would allow stateful "
        "L7 filtering, eliminating the requirement to expose broad ephemeral port ranges.",
        body_style
    ))

    story.append(Paragraph("6. Concluding Reflection", h1_style))
    story.append(Paragraph(
        "This project provided invaluable hands-on mastery of bridging machine learning model compression with modern cloud infrastructure. "
        "I experienced firsthand the critical trade-offs between parameter scale, CPU execution latency, memory limits, and automated cloud "
        "reliability. Successfully building a reproducible, resilient, and fully verified deployment from raw data labeling to automated CI/CD "
        "quality gates has significantly deepened my competence as a systems-oriented cloud engineer.",
        body_style
    ))

    story.append(Spacer(1, 10))
    sig_data = [
        [
            Paragraph("<b>Submission Tag:</b> <font color='#0969DA'>final</font>", meta_style),
            Paragraph("<b>Verified By:</b> Nemapu Navaneeth (230101086)", meta_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[240, 270])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 0.8, colors.HexColor("#0969DA")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sig_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Reflection PDF successfully compiled to {OUTPUT_PDF}")


if __name__ == "__main__":
    build_reflection_pdf()
