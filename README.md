# 🛡️ FORTIS — Autonomous Multi-Agent SOC Intelligence Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io/)
[![Run on Replit](https://replit.com/badge/github/THEPUCHU/s-o-c)](https://replit.com/github/THEPUCHU/s-o-c)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FTHEPUCHU%2Fs-o-c)

> **FORTIS** is an enterprise-grade, real-time autonomous Multi-Agent Security Operations Center (SOC) platform designed to ingest high-severity alert telemetry, decompose complex cyber incidents, execute automated SOAR containment playbooks, and generate executive breach reports with explicit Threat Neutralization Verdicts.

---

## ⚡ Instant Cloud Deployment Options

### 1. 🎈 Streamlit Community Cloud (Recommended for Streamlit Users)
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select Repository: `THEPUCHU/s-o-c` | Branch: `main` | Main file path: `app.py`.
4. Click **Deploy!**

---

### 2. 🌀 Replit (1-Click Instant Cloud Container)
1. Go to [Replit.com](https://replit.com/).
2. Click **"+ Create Repl"** -> **"Import from GitHub"**.
3. Paste repository URL: `https://github.com/THEPUCHU/s-o-c`
4. Click **"Import from GitHub"**. Replit will auto-detect `.replit` and launch `app.py` automatically!

---

### 3. 📐 Vercel / Netlify / GitHub Pages (Zero-Config Web App)
- **Vercel**: Import `https://github.com/THEPUCHU/s-o-c` into Vercel dashboard. It deploys `index.html` instantly.
- **GitHub Pages**:
  1. Go to GitHub repo settings: `https://github.com/THEPUCHU/s-o-c/settings/pages`.
  2. Under **Source**, select `main` branch and `/ (root)` directory.
  3. Save! Your app will be live at `https://THEPUCHU.github.io/s-o-c/`.

---

## 💻 Local Operating Instructions

### Option A: Running via Streamlit (Python)
```bash
git clone https://github.com/THEPUCHU/s-o-c.git
cd s-o-c
pip install -r requirements.txt
streamlit run app.py
```

### Option B: Running via Python HTTP Server
```bash
git clone https://github.com/THEPUCHU/s-o-c.git
cd s-o-c
python -m http.server 8100
```
Open [http://localhost:8100/](http://localhost:8100/) in your browser.

---

## ✨ Features

- **🛡️ 8 Specialized Autonomous Agents**:
  1. **FORTIS Master Orchestrator (SOC Coordinator)** — Decomposes complex alerts into sub-tasks and synthesizes consensus.
  2. **Threat Intelligence Agent** — Queries VirusTotal, AbuseIPDB, and Shodan APIs for IP and hash reputation scoring.
  3. **Log Correlation Agent** — SIEM pattern matching using Sigma rules.
  4. **Malware Inspector** — Static YARA signature scanning and memory entropy evaluation.
  5. **Cloud Guardian Agent** — AWS IAM, CloudTrail, and GCP audit analyzer.
  6. **SOAR Countermeasures Engine** — Automated host isolation, edge firewall rule creation, and OAuth token revocation.
  7. **Compliance Evaluator** — Assesses regulatory impacts (GDPR Art. 33, PCI-DSS CDE).
  8. **HITL Guardrail Agent** — Enforces Human-in-the-Loop approval for high-risk containment actions (Risk Score > 85%).

- **🔥 Cyber Attack Simulator Console**:
  - Interactive attack injection with customizable Target Asset Host, Attacker Source IP, and execution speed.
  - Threat vectors including APT29 Ransomware & Data Exfiltration, Cloud IAM Access Key Hijacking, and LSASS Credential Dumping.

- **⚡ HTML5 Canvas Attack Vector Visualizer**:
  - Dynamic node packet animation connecting Attacker, Firewall, Target Endpoint, and Data Vault nodes.
  - Active animation streaming during execution, settling into a protected shield state upon mitigation.

- **🔍 Expandable Telemetry Drawers**:
  - Clean log streams with `Show Technical Telemetry ▼` drawers exposing raw JSON tool payloads.

- **📄 Executive Incident Report Generator**:
  - Professional, PDF-ready executive incident report with prominent **THREAT REMOVAL VERDICT: SUCCESSFUL MITIGATION** banner, Indicators of Compromise (IoCs) table, and MITRE ATT&CK technique mapping.

---

## 📜 License
MIT License. Developed for Advanced Security Operations Centers and Autonomous Agent Intelligence Applications.
