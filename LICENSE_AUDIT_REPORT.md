# Software Licensing & Copyright Documentation Audit Report

**Project Name:** LoanGuard AI (Loan Default Risk Prediction)  
**Repository Path:** `e:\Project\ML Project\Loan-Verification-Prediction`  
**Audit Date:** October 17, 2026  
**Auditor Role:** Software Licensing & Copyright Documentation Analyst  
**Document Status:** Final Audit  

---

## 1. Executive Summary

This audit provides an independent evaluation of the software license, copyright notices, registration evidence, and third-party dependencies of the **LoanGuard AI** repository.

| Audit Parameter | Finding | Status / Risk Level |
|---|---|---|
| **License Type** | MIT License (Expat Variant) | ✅ Permissive & Industry-Standard |
| **Commercial & Modification Rights** | Fully permitted without royalty | ✅ Unrestricted |
| **Copyright Owner Attribution** | **Missing** (Notice reads `Copyright (c) 2026` without a name) | ⚠️ **Action Required** |
| **Formal Registration Evidence** | **None found** in repository files, git logs, or metadata | ℹ️ Unregistered (Common Law / Berne Convention status only) |
| **Third-Party Dependency Risk** | Direct dependencies use MIT, BSD-3-Clause, Apache-2.0, PSF | ✅ Highly Compatible (No Copyleft detected) |
| **Dataset Provenance** | `Data/Loan_Data.csv` (38k+ records) lacks distinct license/provenance notice | ⚠️ Separation of Data & Code recommended |

---

## 2. Analysis of the Existing License

### 2.1 Exact License Type
The repository contains a standard **MIT License** (specifically the **Expat** variant, approved by the Open Source Initiative - OSI, and categorized by the Free Software Foundation - FSF as a permissive, non-copyleft free software license).

The text matches the standard 1988 MIT text consisting of 22 lines:
- Lines 5–10: Grant of permissions.
- Lines 12–13: Core condition of compliance.
- Lines 15–21: Disclaimer of warranty and limitation of liability.

### 2.2 Permissions Granted
The MIT license grants broad, royalty-free permissions to any recipient:
1. **Commercial Use:** The software, source code, and binaries may be incorporated into proprietary commercial applications and sold or hosted as a paid service (e.g., SaaS credit underwriting portal).
2. **Modification:** Downstream users may alter, refactor, add to, or delete any portion of the source code.
3. **Distribution & Redistribution:** Users may distribute original or modified copies to third parties in source or binary form.
4. **Sublicensing:** Users may sublicense their derivatives under different terms (including proprietary, closed-source licenses), provided the original MIT copyright notice remains intact for original portions.
5. **Private / Internal Use:** Organizations may run and modify the application internally without public disclosure.

### 2.3 Obligations & Conditions
The MIT license is minimalist, imposing only **one mandatory condition**:
> *"The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."* (Lines 12–13)

- **Obligation:** Anyone redistributing the code (or substantial parts of it) must retain the original copyright notice and the full MIT license text.
- **No Patent Clause:** Unlike the Apache 2.0 license, the MIT license contains no express patent grant or patent retaliation clause.
- **No Reciprocal Share-Alike (Non-Copyleft):** Unlike the GNU General Public License (GPL) family, modifications do not need to be published under the same open-source terms.

### 2.4 Warranty & Liability Disclaimer
Lines 15–21 contain standard capital-letter disclaimer language designed to protect authors and copyright holders:
- **"AS IS" Provision:** The software is delivered without warranties of any kind, whether express, statutory, or implied.
- **Disclaimed Guarantees:** Specifically disclaims merchantability, fitness for a particular purpose (e.g., automated credit decisioning accuracy or regulatory compliance with banking standards like Fair Lending / FCRA), and non-infringement.
- **Limitation of Liability:** In no event shall the authors or copyright holders be held liable for any damages (direct, indirect, consequential, or punitive) arising from the use of, or inability to use, the software.

---

## 3. Copyright Information & Ownership Audit

### 3.1 Inspection of Repository Assets

| File / Component | Existing Notice / Header | Finding |
|---|---|---|
| `LICENSE` | `Copyright (c) 2026` | ⚠️ **Incomplete**: Missing copyright holder entity/name. |
| `README.md` | `[![License: MIT](...)](LICENSE)` | Contains license badge & link, but specifies no author or copyright holder. |
| `app.py` | None | No file-level SPDX header or author attribution. |
| `streamlit_app.py` | None | No file-level SPDX header or author attribution. |
| `src/Loan_Prediction.py` | None | No file-level SPDX header or author attribution. |
| `templates/index.html` | Branding: `LoanGuard AI` | UI branding present; no copyright footer or legal entity cited. |
| Git Commit Log | `Author: Sreeram Ganesh S <sreeramganesh00719@gmail.com>` | Git authorship recorded in version control history. |
| Git Remotes | `github.com/sreeramganesh/loan-default-risk-prediction.git` | Personal repository ownership recorded. |

### 3.2 Key Issues & Risks Identified
1. **Omission of Copyright Holder Name in `LICENSE`:**
   - Under international copyright norms (Universal Copyright Convention and Berne Convention), a valid copyright notice traditionally contains three elements:
     1. The symbol © (or the word "Copyright" / "(c)").
     2. The year of first publication (here: `2026`).
     3. **The name of the copyright owner** (individual or organization).
   - Because Line 3 of `LICENSE` omits the owner name, it creates legal ambiguity as to **who** is legally granting the license and **who** enjoys the limitation of liability protections in Line 18.
2. **Git Metadata is Not a Substitute for a Legal Copyright Notice:**
   - While git commits record `Sreeram Ganesh S` as the committer, git author logs can be rewritten or squashed, and do not constitute an explicit declaration of copyright ownership in downstream source packages.
3. **Disaggregation of Components (Not Every Component is Owned by the Repository Author):**
   - **Custom Code:** Scripts such as `app.py`, `streamlit_app.py`, `src/Loan_Prediction.py`, `src/Random_Forest.py`, and `templates/index.html` represent original literary/software expressions authored for this project.
   - **Machine Learning Models (`Models/*.pkl`):** Trained scikit-learn model weights (`loan_prediction.pkl`, `feature_encoders.pkl`, `target_encoder.pkl`) are mathematical representations derived from training data. Legal jurisdictions (including the US and India) generally evaluate ML model weights differently from source code; they may not be protected as traditional literary works unless bundled with code pipelines.
   - **Dataset (`Data/Loan_Data.csv` & `Data/Loan_Data.xlsx`):** A tabular loan dataset with 38,000+ entries covering loan performance and borrower financials. This dataset appears to be derived from public credit benchmark data (e.g., LendingClub loan histories). The repository owner **does not automatically own copyright in third-party credit data**. Raw factual data is not copyrightable; compilations/databases may carry third-party database rights or specific data usage licenses (e.g., CC0, CC-BY, ODbL). Applying an MIT software license to a third-party dataset is legally imprecise.
   - **Fonts & Visual Assets:** `templates/index.html` loads Google Fonts (`Outfit`, `Plus Jakarta Sans`, `JetBrains Mono`). These are governed by their respective SIL Open Font License (OFL 1.1) and Apache 2.0 terms, not the project's MIT license.

---

## 4. Evidence of Formal Copyright Registration

### 4.1 Audit Findings
A systematic search was performed across all source files, documentation, commit messages, git tags, and configuration files for indicators of statutory copyright registration:
- **Diary Numbers:** None found.
- **Register of Copyrights (ROC) Numbers (e.g., `SW-XXXXX/YYYY`):** None found.
- **Registration Certificates (PDF/Images):** None found.
- **Application References or Official Correspondence:** None found.

**Conclusion:** There is **zero verifiable evidence** in the repository indicating that this project has been formally registered with any government intellectual property office.

### 4.2 Legal Distinction: License vs. Formal Registration

```
┌────────────────────────────────────────┐       ┌────────────────────────────────────────┐
│         OPEN-SOURCE LICENSE            │       │      FORMAL COPYRIGHT REGISTRATION     │
│             (e.g., MIT)                │       │     (e.g., Indian Copyright Office)    │
├────────────────────────────────────────┤       ├────────────────────────────────────────┤
│ • Unilateral legal permission granted  │  VS   │ • Statutory certification issued by an │
│   by an author to the public.          │       │   official government intellectual     │
│ • Self-declared; no government review  │       │   property registry (e.g., DPIIT).     │
│   or official approval required.       │       │ • Creates public legal record in the   │
│ • Defines how others may use the code. │       │   Register of Copyrights (ROC).        │
│ • Does NOT confer government proof of  │       │ • Serves as prima facie evidence of    │
│   authorship, priority, or ownership.  │       │   ownership in court of law.           │
└────────────────────────────────────────┘       └────────────────────────────────────────┘
```

- **Automatic Subsistence (Berne Convention & Indian Copyright Act, 1957, Section 17):** Copyright protection originates automatically upon the creation and tangible fixation of original source code. Registration is **voluntary** in India and most Berne Convention signatory nations.
- **Value of Registration (Indian Copyright Act, Section 45 & 48):** While not mandatory, registering a software application (classified as a "Computer Software / Literary Work") with the Copyright Office provides a Certificate of Registration and entry in the Register of Copyrights (ROC), which serves as **prima facie evidence** of copyright ownership in civil and criminal infringement proceedings.
- Inclusion of `LICENSE` in GitHub merely declares licensing terms; **it does not constitute or imply registration**.

### 4.3 Guide for Independent Verification in India

To independently verify if an application has been submitted or registered under the **Copyright Office of India** (Department for Promotion of Industry and Internal Trade - DPIIT, Ministry of Commerce and Industry):

#### Method A: Tracking an Application via Diary Number
1. Access the official portal: **[https://copyright.gov.in](https://copyright.gov.in)**.
2. Under the top navigation or quick links, select **"Status of Application"** (Direct URL: `https://copyright.gov.in/SearchStatus.aspx`).
3. Enter the official **Diary Number** (Format: `XXXXX/YYYY-CO`, e.g., `12345/2026-CO`).
4. Click **View Status** to inspect the real-time workflow status:
   - *Marked for Scrutiny*
   - *Waiting for Mandatory Work Submission / DD Verification*
   - *Discrepancy Letter Issued*
   - *Hearing Scheduled*
   - *Re-scrutiny*
   - *Registered / ROC Generated*

#### Method B: Searching Registered Software Works (ROC Search)
1. Go to **[https://copyright.gov.in](https://copyright.gov.in)** and select **"Search Registered Works"**.
2. Select the search criteria:
   - **Registration Number:** Software works follow the format `SW-XXXXX/YYYY` (e.g., `SW-14250/2026`).
   - **Title of Work:** Search by exact or partial title, such as `"LoanGuard AI"` or `"Loan Default Risk Prediction"`.
   - **Name of Applicant / Author:** Search by the legal name of the author (e.g., `"Sreeram Ganesh S"`).
3. If registered, the portal displays:
   - Registration Number and Date.
   - Title of the Work and Language.
   - Name and Address of Applicant / Author.
   - Class of Work (`Literary / Software`).

#### Method C: Submitting a Fresh Copyright Application in India
If formal registration is desired:
1. Register an account on the **e-Filing Portal** (`https://copyright.gov.in/eFiling/user_login.aspx`).
2. Complete **Form XIV** (Application for Registration of Copyright).
3. Complete the **Statement of Particulars (SoP)** and **Statement of Further Particulars (SoFP)**.
4. Select Class of Work: **Computer Software / Literary Work**.
5. Upload a PDF containing the source code extract (standard practice requires the first 10 pages and last 10 pages of unredacted source code or full code if under 20 pages).
6. Pay the statutory fee (currently ₹500 for an individual / natural person / startup for Literary / Computer Software Works).
7. Submit the signed physical copy along with acknowledgment if requested, and wait for the mandatory 30-day objection period.

---

## 5. Third-Party Dependency Audit & License Compatibility

### 5.1 Manifest Analysis (`requirements.txt`)
The project lists 11 direct Python dependencies. An inspection of package metadata yields the following licensing profile:

| Package | Version Range | Installed Version | Declared License | OSI Approved | Risk Rating |
|---|---|---|---|---|---|
| `streamlit` | `>=1.30.0` | `1.65.0` | **Apache-2.0** | Yes | Low (Permissive) |
| `scikit-learn` | `>=1.4.0` | `1.9.0` | **BSD-3-Clause** | Yes | Low (Permissive) |
| `pandas` | `>=2.0.0` | `3.0.3` | **BSD-3-Clause** | Yes | Low (Permissive) |
| `numpy` | `>=1.24.0` | `2.5.1` | **BSD-3-Clause / Multi-license** | Yes | Low (Permissive) |
| `joblib` | `>=1.3.0` | `1.5.3` | **BSD-3-Clause** | Yes | Low (Permissive) |
| `matplotlib` | `>=3.7.0` | `3.11.0` | **PSF / BSD-compatible** | Yes | Low (Permissive) |
| `seaborn` | `>=0.12.0` | `0.13.2` | **BSD-3-Clause** | Yes | Low (Permissive) |
| `pillow` | `>=10.0.0` | `12.3.0` | **MIT-CMU / Historical PIL** | Yes | Low (Permissive) |
| `openpyxl` | `>=3.1.0` | `3.1.5` | **MIT** | Yes | Low (Permissive) |
| `Flask` | `>=3.0.0` | `3.1.3` | **BSD-3-Clause** | Yes | Low (Permissive) |
| `flask-cors` | `>=4.0.0` | `6.0.5` | **MIT** | Yes | Low (Permissive) |

### 5.2 License Compatibility Evaluation
1. **Absence of Copyleft:**
   - None of the direct dependencies use strong copyleft (e.g., GPL v2/v3, AGPL v3) or weak copyleft (e.g., LGPL, MPL 2.0).
   - This ensures there is **no risk of viral relicensing**, meaning the project code does not face any legal pressure to open-source private or proprietary extensions.
2. **Compatibility with Project's MIT License:**
   - **MIT + MIT:** Identical terms (`openpyxl`, `flask-cors`).
   - **MIT + BSD-3-Clause:** Fully compatible. The 3-clause BSD requires keeping the copyright notice and warranty disclaimer, and contains a clause restricting using the authors' names for endorsement without prior permission. This is readily compatible with an MIT project.
   - **MIT + Apache-2.0:** Fully compatible when distributing Apache-2.0 libraries as external dependencies or modules. Apache-2.0 requires retaining copyright notices, license text, and NOTICE files if provided.
   - **MIT + PSF:** Fully compatible permissive license.
3. **Audit Scope Limitation (Transitive Dependencies):**
   - The virtual environment contains over 50 transitive sub-dependencies (e.g., `Jinja2`, `Werkzeug`, `altair`, `pyarrow`, `protobuf`, `requests`, `urllib3`, `certifi`, etc.).
   - While primary transitive dependencies are recognized open-source libraries, a full legal audit of every sub-dependency was not performed. Projects targeting commercial production distribution should generate an automated Software Bill of Materials (SBOM) using tools like `pip-licenses` or `cyclonedx-python`.

---

## 6. Actionable Recommendations

### 6.1 Recommended Corrections (Step-by-Step)

#### 1. Complete the Copyright Header in `LICENSE`
*Current Text:*
```text
MIT License

Copyright (c) 2026
```
*Recommended Correction (Replace with legitimate author or organizational name):*
```text
MIT License

Copyright (c) 2026 Sreeram Ganesh S
```
*(Or your legal business/entity name if developing under a company or institutional affiliation).*

#### 2. Add Author & License Details to `README.md`
Add an explicit Authorship & Copyright section at the bottom of [README.md](README.md):
```markdown
## ⚖️ License & Copyright

Copyright (c) 2026 Sreeram Ganesh S.

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for the complete text.
```

#### 3. Standardize Source Code File Headers (SPDX)
Insert standard SPDX identifiers at the top of core Python files (`app.py`, `streamlit_app.py`, `src/Loan_Prediction.py`):
```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Sreeram Ganesh S
```

#### 4. Explicitly Disclaim and Document Dataset Provenance
Create a `DATA_LICENSE.md` or a dedicated note in the `README.md` clarifying that the sample credit records in `Data/Loan_Data.csv` are included for educational/demonstrative modeling purposes and originate from public benchmark financial records, distinguishing data terms from source code terms.

#### 5. Generate a Third-Party Notice File
Before packaging the application for enterprise or commercial distribution, compile a `THIRD_PARTY_NOTICES.md` file listing all runtime dependencies, their license types, and their respective copyright notices to satisfy the attribution conditions of Apache-2.0 and BSD-3-Clause dependencies.

---

## 7. Summary Checklist

- [x] License identified: **MIT (Expat)**
- [x] Commercial, modification, and redistribution permissions: **Allowed**
- [x] Obligations verified: **Attribution & Notice retention required**
- [x] Copyright notice audited: **Year present (2026); Owner name missing**
- [x] Formal registration checked: **No registration evidence found (Common-law protection active)**
- [x] Third-party dependencies audited: **11/11 direct packages verified permissive**
- [x] Official Indian registration verification process documented: **`copyright.gov.in`**
- [x] Report generated without altering original code or project files: **Completed**

---
*Report generated on October 17, 2026.*
