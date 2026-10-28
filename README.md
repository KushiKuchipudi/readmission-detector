# 🛡️ Readmission Detector: Clinical Data Sanity Checker

> *"A report that's wrong looks exactly like a report that's right."*

An automated data quality assertion framework for post-acute and outpatient EHR pipelines. Built to detect silent ETL schema drops—such as unmapped transfer billing codes—before dirty metrics reach executive dashboards.

---

## 🎯 Validation Rules Summary

| Rule ID | Severity | Category | Assertion Logic |
| :--- | :--- | :--- | :--- |
| **RULE_001** | `CRITICAL` | Silent Failure | Flags facilities (>50 beds) reporting **0 hospital transfers** in a 30-day window (detects unmapped staging keys). |
| **RULE_002** | `HIGH` | Temporal Anomaly | Ensures Discharge Date $\ge$ Admission Date. |
| **RULE_003** | `HIGH` | Clinical Safety | Flags Daily MME > 90 without explicit clinician override flags. |
| **RULE_004** | `MEDIUM` | Data Hygiene | Detects out-of-bounds readmission intervals ($\le 0$ or $>365$ days). |
| **RULE_005** | `LOW` | Schema Compliance | Flags null or unmapped payer categories (`UNMAPPED`, `UNKNOWN`, `NaN`). |

---

## 🚀 Quick Start

1. **Clone & Setup**:
   ```bash
   git clone [https://github.com/kushikuchipudi/readmission-detector.git](https://github.com/kushikuchipudi/readmission-detector.git)
   cd readmission-detector
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
