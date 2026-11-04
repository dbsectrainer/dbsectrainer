<!-- GitHub profile README for @dbsectrainer -->

<h1 align="center">Hi, I'm Donnivis Baker 👋</h1>

<p align="center">
  <strong>Senior Software Engineer · Cloud &amp; Security Architect · DevOps Leader</strong><br>
  I build secure cloud, compliance, and AI systems — and document the evidence that they work.
</p>

<p align="center">
  <a href="https://github.com/dbsectrainer">GitHub</a> ·
  <a href="https://www.linkedin.com/in/dbsectrainer/">LinkedIn</a> ·
  <a href="https://www.npmjs.com/~dbsectrainer">npm</a> ·
  <a href="https://registry.modelcontextprotocol.io">MCP Registry</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" alt="Rainbow divider" width="100%">
</p>

<!-- GitHub prefixes explicit anchor ids with "user-content-"; the TOC targets those rendered ids. -->

## 📑 Table of Contents

- [About Me](#user-content-about-me)
- [Current Focus](#user-content-current-focus)
- [Selected Work](#user-content-selected-work)
- [MCP Servers](#user-content-mcp-servers)
- [Open Source](#user-content-open-source)
- [Tech Stack](#user-content-tech-stack)
- [Let's Connect](#user-content-lets-connect)
- [Repository Verification](#user-content-repository-verification)

<a id="about-me"></a>
## 🧭 About Me

I work at the intersection of cloud security, federal compliance, and applied AI. My public repositories are reference implementations built to be run, tested, and audited — not just read.

Recent work includes **AEGIS** (multi-cloud FedRAMP High, NIST 800-53 Rev. 5, DoD Cloud SRG, and Zero Trust controls), an **AI Safety & Governance Platform**, a **NIST 800-53 evidence-driven scanner**, a **Secure Generative AI platform on AWS**, and six **MCP servers** for agent observability, cost, data, evaluation, legal, and health workflows.

The larger reference implementations include a `docs/evidence/verification-report.md` with commands, test results, screenshots, and explicit non-goals. If a capability was not verified, it is labeled that way.

```python
class Engineer:
    def __init__(self):
        self.focus = ["cloud security", "federal compliance", "AI governance"]
        self.method = ["threat model", "automate", "test", "show evidence"]
        self.stack = ["Python", "TypeScript", "Terraform", "AWS · Azure · GCP"]
```

<a id="current-focus"></a>
## 🎯 Current Focus

- **Federal compliance automation** — NIST 800-53 Rev. 5, FedRAMP High, CMMC 2.0 / NIST 800-171, OSCAL, and policy-as-code.
- **AI governance and safety** — model registry, RBAC, monitoring, privacy and regulatory checks, and secure RAG.
- **MCP developer tooling** — local-first servers for tracing, cost, data, evaluation, legal, and health workflows.

<a id="selected-work"></a>
## 🚀 Selected Work

| Project | What it does |
| --- | --- |
| **[AEGIS](https://github.com/dbsectrainer/AEGIS)** | Multi-cloud federal security framework aligned to FedRAMP High, NIST 800-53 Rev. 5, DoD Cloud SRG, and NIST 800-207; Terraform modules plus authorization artifacts.<br>**Stack:** Terraform · AWS/Azure/GCP · LocalStack |
| **[AI Safety & Governance](https://github.com/dbsectrainer/ai-safety-governance)** | Full-stack model governance: JWT/RBAC, model registry, host monitoring, GDPR/HIPAA/CCPA checks, audit trail, and Docker deployment.<br>**Stack:** Python · FastAPI · React · TypeScript · SQLite/PostgreSQL |
| **[NIST 800-53 Scanner](https://github.com/dbsectrainer/nist_800_53_scanner)** | Evidence-driven Rev. 5 assessment: read-only collectors, versioned policy-as-code rules, OSCAL output, and Prometheus/Grafana monitoring.<br>**Stack:** Python · Flask · OSCAL · Docker |
| **[Secure GenAI on AWS](https://github.com/dbsectrainer/Secure-Generative-AI-Platform-on-AWS)** | Bedrock + RAG reference platform with Guardrails, PII redaction, WAF/GuardDuty, and SAM-local end-to-end tests.<br>**Stack:** Python · AWS SAM · Terraform · Bedrock |
| **[ICRAF](https://github.com/dbsectrainer/integrated-cyber-risk-compliance)** | Browser-only CMMC 2.0 / NIST 800-171 dashboard: 110-practice tracker, risk register, and IaC/CI control verifier.<br>**Stack:** React 19 · TypeScript · Vite |
| **[Federal Document Triage](https://github.com/dbsectrainer/federal-doc-triage-agent)** | LangGraph workflow for document intake, classification, routing, and approval, with optional Bedrock/Comprehend/Textract integrations.<br>**Stack:** Python · LangGraph · AWS |

Each repository states what is verified and what is not; see its `docs/evidence/verification-report.md` where present.

**Also shipped:**

- [Label Check](https://github.com/dbsectrainer/label-check) ([live](https://label-check-puce.vercel.app)) — human-in-the-loop alcohol label verification.
- [Enterprise Checklist Dashboard](https://github.com/dbsectrainer/enterprise-grade-checklists) ([live](https://dbsectrainer.github.io/enterprise-grade-checklists/)) — eight-domain progress tracker.
- [Cloud Security Best Practices](https://github.com/dbsectrainer/cloud-security-best-practices) ([live](https://dbsectrainer.github.io/cloud-security-best-practices/)) — FedRAMP/NIST documentation hub.
- [Mandarin Pathways](https://github.com/dbsectrainer/Mandarin-Pathways) ([live](https://dbsectrainer.github.io/Mandarin-Pathways/)) — Mandarin learning PWA and Flutter app.

<a id="mcp-servers"></a>
## 🔌 MCP Servers

Six local-first servers, published on npm and listed in the [official MCP registry](https://registry.modelcontextprotocol.io). Each repository documents its tools and configuration. Node.js 20.19+ is required (trace-inspector and eval-runner require 22.5+).

| Server | What it does |
| --- | --- |
| **[mcp-agent-trace-inspector](https://github.com/dbsectrainer/mcp-agent-trace-inspector)** · [npm](https://www.npmjs.com/package/mcp-agent-trace-inspector) | Local-first tracing, cost estimates, diffs, and audit logs for MCP agent workflows. |
| **[mcp-cost-tracker-router](https://github.com/dbsectrainer/mcp-cost-tracker-router)** · [npm](https://www.npmjs.com/package/mcp-cost-tracker-router) | Offline token/cost tracking, budget alerts, and model-routing suggestions. |
| **[mcp-data-pipeline-connector](https://github.com/dbsectrainer/mcp-data-pipeline-connector)** · [npm](https://www.npmjs.com/package/mcp-data-pipeline-connector) | Cross-source SQL over CSV/JSON, PostgreSQL, and REST via embedded DuckDB. |
| **[mcp-eval-runner](https://github.com/dbsectrainer/mcp-eval-runner)** · [npm](https://www.npmjs.com/package/mcp-eval-runner) | YAML-driven regression tests for MCP servers and agent workflows. |
| **[mcp-legal-doc-analyzer](https://github.com/dbsectrainer/mcp-legal-doc-analyzer)** · [npm](https://www.npmjs.com/package/mcp-legal-doc-analyzer) | Local clause extraction, risk flagging, compliance checks, and version diffs. |
| **[mcp-server-health-monitor](https://github.com/dbsectrainer/mcp-server-health-monitor)** · [npm](https://www.npmjs.com/package/mcp-server-health-monitor) | MCP-native health checks, schema-drift detection, and local history. |

<a id="open-source"></a>
## 🤝 Open Source

- **Merged:** [microsoft/generative-ai-for-beginners #698](https://github.com/microsoft/generative-ai-for-beginners/pull/698) — grammar and function-calling documentation fixes.
- **Proposed:** [microsoft/data-formulator #90](https://github.com/microsoft/data-formulator/pull/90) (Docker support), [MetaGPT #1735](https://github.com/FoundationAgents/MetaGPT/pull/1735) (Ollama URL wrappers), and [ScoutSuite #1695](https://github.com/nccgroup/ScoutSuite/pull/1695) (recursion fix); these PRs were closed without merge.

<a id="tech-stack"></a>
## 🧰 Tech Stack

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&amp;logo=python&amp;logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&amp;logo=typescript&amp;logoColor=white">
  <img alt="AWS" src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&amp;logo=amazonwebservices&amp;logoColor=white">
  <img alt="Azure" src="https://img.shields.io/badge/Azure-0078D4?style=for-the-badge&amp;logo=microsoftazure&amp;logoColor=white">
  <img alt="GCP" src="https://img.shields.io/badge/GCP-4285F4?style=for-the-badge&amp;logo=googlecloud&amp;logoColor=white">
  <img alt="Terraform" src="https://img.shields.io/badge/Terraform-844FBA?style=for-the-badge&amp;logo=terraform&amp;logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&amp;logo=docker&amp;logoColor=white">
  <img alt="Kubernetes" src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&amp;logo=kubernetes&amp;logoColor=white">
</p>

| Area | Tools |
| --- | --- |
| Languages | Python · TypeScript · JavaScript · SQL · HCL · Bash |
| Cloud & platforms | AWS · Azure · GCP · Docker · Kubernetes · Terraform · GitHub Actions |
| Security & compliance | NIST 800-53 · FedRAMP · CMMC 2.0 · NIST 800-171 · Zero Trust · OSCAL · OPA · SBOM |
| AI/ML | PyTorch · TensorFlow · scikit-learn · LangGraph · Amazon Bedrock · RAG |

<a id="lets-connect"></a>
## 📬 Let's Connect

- **GitHub:** [@dbsectrainer](https://github.com/dbsectrainer)
- **LinkedIn:** [dbsectrainer](https://www.linkedin.com/in/dbsectrainer/)
- **npm:** [~dbsectrainer](https://www.npmjs.com/~dbsectrainer)
- **MCP Registry:** [published servers](https://registry.modelcontextprotocol.io)

The best way to reach me is through GitHub or LinkedIn.

<a id="repository-verification"></a>
## 🧪 Repository Verification

<details>
<summary><strong>Verification &amp; maintenance commands</strong></summary>

This repository is the source for my GitHub profile README. There is no application server or build step: GitHub renders `README.md` directly.

**Prerequisites:** Python 3.12+; Playwright 1.55+ for screenshots; Node.js 20.19+ only for the optional MCP package audit.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m playwright install chromium

make check          # unit tests + README structure, assets, secrets, and links
make preview        # render README through GitHub's Markdown API
make screenshots    # capture desktop/mobile evidence with Playwright
```

The link and registry checks require network access. No secrets or environment variables are required. `GITHUB_TOKEN` is optional and only raises GitHub API rate limits for `make preview`.

Validation report, screenshots, and residual risks: [docs/evidence/verification-report.md](https://github.com/dbsectrainer/dbsectrainer/blob/main/docs/evidence/verification-report.md).

</details>

<p align="center">
  <i>Secure by design. Verified by evidence.</i>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" alt="Rainbow divider" width="100%">
</p>
