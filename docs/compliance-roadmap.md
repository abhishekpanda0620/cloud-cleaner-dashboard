# Security & Compliance Roadmap

This roadmap adds a **Security & Compliance** tab to the Cloud Cleaner Dashboard, extending it from **cost optimization** to **audit‑ready security posture management**.

---

## 🎯 Goal

Provide **read‑only, auditor‑safe visibility** into cloud security posture and map technical findings to major compliance frameworks without claiming certification.

---

## 🧭 Phase 0 – Foundations (Week 0–1)

### Objectives
- Prepare architecture for security controls
- Avoid breaking existing cost‑optimization features

### Tasks
- Add new navigation tab: **Security & Compliance**
- Define internal terminology:
  - *Check*
  - *Control*
  - *Framework*
  - *Evidence*
- Create base data models:
  - SecurityCheck
  - ControlResult
  - FrameworkMapping
- Add feature flags for security scanning

### Deliverables
- Empty Security tab (UI)
- DB schema for security data

---

## 🧱 Phase 1 – Full CIS AWS Foundations (Week 1–4)

### Goal
Achieve **100% coverage** of the CIS AWS Foundations Benchmark v1.4.0 (58 Controls).
This forms the baseline for all other frameworks (SOC2, HIPAA, GDPR).

### Coverage Areas
- **Identity (IAM)**: 21 controls (Passwords, MFA, Keys, Roles)
- **Logging**: 11 controls (CloudTrail, S3, KMS)
- **Monitoring**: 15 controls (CloudWatch Alarms, Metrics)
- **Networking**: 4 controls (Security Groups, NACLs, VPC)

### Deliverables
- Complete set of 58 automated checks
- Detailed "Pass/Fail" evidence for each
- CIS Compliance Scorecard


---

## 🔗 Phase 2 – Framework Mapping (Week 3–4)

### Supported Frameworks
- SOC 2 (Trust Services Criteria)
- PCI‑DSS
- HIPAA
- GDPR
- DPDP Act (India)

### Approach
Frameworks **map to CIS**, not direct checks.

Example:
SOC2 CC6.1 → CIS 1.2 → Root MFA Enabled

### Tasks
- Build mapping table:
  - Framework → Control → CIS ID
- Allow filtering by framework
- Generate framework‑specific reports

### UI
- Dropdown: Select Framework
- View compliance % per framework
- Show mapped CIS controls

### Deliverables
- SOC2 / PCI / HIPAA views
- Mapping engine
- Framework report export (PDF/CSV)

---

## 🧾 Phase 3 – Audit Evidence & Reporting (Week 4–5)

### Evidence Types
- Configuration snapshots
- API responses
- Timestamps
- AWS Account ID & Region

### Features
- Evidence retention history
- One‑click “Audit Evidence Export”
- Time‑based compliance trends

### Deliverables
- Audit‑ready PDF
- Evidence ZIP export
- Historical compliance graph

---

## 🔐 Phase 4 – Advanced Security Checks (Week 5–7)

### New Controls
- IAM unused permissions
- Access key rotation (>90 days)
- Public RDS snapshots
- Default VPC usage
- EBS encryption by default
- CloudWatch log retention

### Risk Scoring
- Low / Medium / High
- Security vs Cost impact

### Deliverables
- Risk‑based prioritization
- High‑risk alerting
- Security posture score

---

## 🇮🇳 Phase 5 – Indian Compliance (Week 7–8)

### Supported
- DPDP Act 2023
- CERT‑In logging rules
- RBI cybersecurity guidelines (infra‑level)

### Checks
- Log retention ≥ 180 days
- Time sync enabled
- Encryption at rest
- Access control policies

### Deliverables
- India‑specific compliance view
- DPDP‑mapped reports
- Local audit language

---

## 🤖 Phase 6 – Automation & Guardrails (Optional)

### Features
- Alert‑only mode (default)
- Auto‑remediation (opt‑in)
- Terraform / IaC scanning
- GitHub PR comments

### Deliverables
- Policy‑as‑Code engine (OPA)
- CI/CD security gate
- Drift detection

---

## 🚨 What This Tool Will NOT Claim

❌ “Certified GDPR / SOC2 compliant”  
❌ Legal compliance guarantees  
❌ Data‑level inspection

✅ “Provides technical compliance evidence”  
✅ “Supports audit readiness”  

---

## 🏁 Final Outcome

Cloud Cleaner becomes:
- Cost Optimization Tool
- Security Posture Dashboard
- Compliance Evidence Generator
- Auditor‑Friendly Platform

---

## 📌 Suggested Naming

**Cloud Cleaner Secure™**  
or  
**Cloud Cleaner – Security & Compliance**

---

*This roadmap intentionally aligns with how Wiz, Prisma Cloud, and AWS Security Hub operate — but in a lightweight, open‑source‑friendly way.*
