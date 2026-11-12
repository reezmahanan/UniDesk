# UniDesk — AI University Help Desk & Ticketing Platform

An enterprise-grade, full-stack AI help desk, document ingestion, and support ticketing platform tailored for higher education institutions in Sri Lanka.

UniDesk preserves its signature **violet glassmorphic aesthetic**, responsive sidebar, dynamic dark/light themes, and real-time browser text-to-speech (TTS), while replacing prototype client-side stubs with a secure, production-ready architecture powered by **Vue 3, TypeScript, Vite, Tailwind CSS, FastAPI, SQLAlchemy, Alembic, PostgreSQL with pgvector, and Google Gemini with grounded Retrieval-Augmented Generation (RAG)**.

---

## 📸 Visual Identity & Branding

UniDesk features a premium, responsive glassmorphic user interface:
* **Dark Theme:** Deep violet gradient background (`#1d103c` to `#080811`), glowing purple accents (`#a855f7`), and frosted glass panels with backdrop blur (`rgba(26, 26, 46, 0.55)`).
* **Light Theme:** High-contrast crisp lavender-white aesthetic with violet borders and glowing badges.
* **Text-to-Speech (TTS):** Browser Web SpeechSynthesis API with speech toggle and multi-language voice detection.
* **Tri-Lingual Navigation:** Full interface and workflow translations for **English**, **Sinhala (සිංහල)**, and **Tamil (தமிழ்)**.

---

## 🏛️ Project Purpose & University Support Areas

UniDesk serves university students, academic staff, and administrative officers in Sri Lanka:

1. **Admissions & UGC Registration:** Minimum GCE A/L stream requirements, Z-Score criteria, and UGC degree intake processes.
2. **Academic Procedures:** Course enrollment windows, examination deferments, add/drop periods, and GPA grading regulations.
3. **IT & LMS Support:** Campus WiFi setup (`UniDesk-Secure`), student Microsoft 365 webmail, and student LMS login resets.
4. **Mahapola & Bursary Verification:** UGC criteria, Grama Niladhari income certificate verification, Bank of Ceylon (BOC) student account linkage, and monthly stipend voucher collections.
5. **Library Services:** Campus library opening hours, book reservations, cubicle bookings, and fine waivers.
6. **General Campus Services:** Campus facilities, faculty locations, and administration contacts.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vue 3 (Composition API), TypeScript, Vite 6, Vue Router 4, Pinia 2 |
| **Styling & Icons** | Tailwind CSS 3, Lucide Icons for Vue (`lucide-vue-next`) |
| **Backend API** | Python 3.11+, FastAPI, Pydantic v2 |
| **ORM & Migrations** | SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 with `pgvector` extension (with SQLite local dev compatibility) |
| **AI Generation** | Google Gemini (`google-genai` / `gemini-1.5-flash`) + Grounded Mock AI Engine |
| **Embeddings & Search** | Gemini Embeddings (`text-embedding-004`) + Deterministic Vector & BM25 Lexical Fallback |
| **Document Processing** | `pypdf` (PDF extraction with scanned document detection) and `python-docx` (DOCX extraction) |
| **Authentication & Security** | JWT tokens, Bcrypt password hashing, HttpOnly cookies, CSRF protection, In-memory rate limiting |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 👥 Roles & Authorization Matrix

UniDesk implements strict role-based access control (RBAC):

| Capability | STUDENT | STAFF | ADMIN |
| :--- | :---: | :---: | :---: |
| Self-Registration (Public signup) | ✅ | ❌ | ❌ |
| Browse Published FAQs, Notices & Services | ✅ | ✅ | ✅ |
| Ask Grounded AI Chatbot & View Own Chat History | ✅ | ✅ | ✅ |
| Submit & Manage Own Support Tickets | ✅ | ❌ (Own dept) | ✅ (All) |
| View Public Ticket Replies & Post Responses | ✅ | ✅ | ✅ |
| View Staff Internal Notes (Confidential) | ❌ **Strictly Hidden** | ✅ | ✅ |
| Add Staff Internal Notes | ❌ | ✅ | ✅ |
| Reassign Department or Assign Staff Officers | ❌ | ✅ | ✅ |
| Access AI Ticket Summaries & AI Draft Replies | ❌ | ✅ | ✅ |
| Upload & Archive Knowledge Documents | ❌ | ❌ | ✅ |
| Manage Users & Department Affiliations | ❌ | ❌ | ✅ |

---

## 🤖 Grounded RAG & Citation Validation

The chatbot does not hallucinate arbitrary facts or claim 100% accuracy. It follows a Retrieval-Augmented Generation pipeline:

```
Student Inquiry 
   │
   ▼
Active Knowledge Document Filter (PUBLISHED, non-expired only)
   │
   ▼
Hybrid Search (Semantic Cosine Similarity + BM25 Lexical Overlap)
   │
   ▼
Context Assembly (Top relevant text chunks)
   │
   ▼
Gemini API / Grounded Mock AI Provider
   │
   ▼
Server-Side Citation Validation (Citation IDs verified against retrieved chunks)
   │
   ▼
Grounded Answer + Document Title + Page Number + Section Heading + Download Link
```

* **Server-Side Citation Verification:** Citations returned in answers are strictly validated against active database chunk IDs. Hallucinated citation references are discarded on the server.
* **Insufficient Information Fallback:** When no verified document covers the question, UniDesk clearly states that sufficient information is not available and prompts the user to create a support ticket.
* **Document Archiving:** When an admin archives a document, all of its chunks are excluded from student retrieval immediately.
* **Scanned Document Detection:** When a scanned PDF with no extractable text is uploaded, the ingestion pipeline warns the administrator that text extraction failed and notes that OCR is a planned future capability.
* **Offline / Demo AI Mode:** When `MOCK_AI_MODE=true` (or when `GEMINI_API_KEY` is not provided), UniDesk uses an intelligent deterministic grounded synthesizer that extracts facts directly from retrieved document chunks, clearly labelled as Demo AI mode.

---

## 🔄 Chat-to-Ticket Handoff & Staff AI Assistance

### 1. Student Handoff Flow
1. If the chatbot cannot resolve an issue or if the student requires administrative intervention, the student clicks **"Create Support Ticket"**.
2. UniDesk drafts a suggested **Subject**, **Issue Summary**, and routes to the appropriate **Department** (e.g. Welfare for Mahapola inquiries, IT for LMS locks).
3. The student reviews and edits the draft in a dedicated modal.
4. The student explicitly checks or unchecks whether to include recent chat transcript excerpts.
5. The ticket is submitted only upon explicit confirmation.

### 2. Staff AI Assistance
* **Staff Ticket Summary:** In the ticket workspace, staff officers can click "Summarize Issue" to generate a synthesized brief of the student's problem, key facts, and missing documentation.
* **Staff Reply Draft:** Staff can click "Draft Reply" to produce a suggested response grounded in approved university policies. The draft is placed into an editable text box so staff can review, edit, and confirm before sending.

---

## 💻 Quick Start & Deployment

### Option 1: Docker Compose (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/reezmahanan/Apex-Bot.git
   cd Apex-Bot
   ```

2. Copy the environment configuration file:
   ```bash
   cp .env.example .env
   ```

3. Launch the complete platform (PostgreSQL with pgvector, FastAPI backend, and Nginx Vue frontend):
   ```bash
   docker compose up --build
   ```

4. Open your browser:
   * **Frontend Application:** [http://localhost:5173](http://localhost:5173) or [http://localhost](http://localhost)
   * **Interactive API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **API OpenAPI Schema:** [http://localhost:8000/api/openapi.json](http://localhost:8000/api/openapi.json)

---

### Option 2: Local Development Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *The database tables and demo content are initialized automatically on startup.*

#### Frontend Setup

1. In a separate terminal, navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 🔑 Pre-Configured Demo Accounts

For local evaluation, four demonstration accounts are seeded with distinct permissions:

| Account | Email | Password | Role & Description |
| :--- | :--- | :--- | :--- |
| **Kasun Jayasundara** | `student@apex.edu.lk` | `student123` | **STUDENT** • Computing • Index: `2026/SE/048` |
| **Sanduni Perera** | `sanduni@apex.edu.lk` | `student123` | **STUDENT** • Business • Index: `2026/BM/102` |
| **Dr. Priyantha Alwis** | `staff@apex.edu.lk` | `staff123` | **STAFF** • Senior IT Support Officer |
| **University Admin** | `admin@apex.edu.lk` | `admin123` | **ADMIN** • System & Knowledge Administrator |

*A one-click **"Demo Role"** switcher is integrated into the top bar during development so you can switch perspectives.*

---

## 🧪 Automated Testing & Verification

UniDesk includes a comprehensive automated test suite testing authorization, student isolation, department boundaries, internal note privacy, ticket transitions, and grounded RAG citations.

Run the test suite:
```bash
cd backend
.\venv\Scripts\pytest -v
```

**Results:**
```
============================== test session starts ==============================
collected 15 items

tests/test_auth.py::test_student_registration PASSED                      [  6%]
tests/test_auth.py::test_login_success PASSED                             [ 13%]
tests/test_auth.py::test_login_invalid_password PASSED                    [ 20%]
tests/test_auth.py::test_get_current_user_profile PASSED                  [ 26%]
tests/test_auth.py::test_unauthenticated_request_rejected PASSED          [ 33%]
tests/test_rag_and_citations.py::test_rag_grounded_answer_with_citations PASSED [ 40%]
tests/test_rag_and_citations.py::test_rag_insufficient_information_fallback PASSED [ 46%]
tests/test_rag_and_citations.py::test_archived_documents_excluded_from_retrieval PASSED [ 53%]
tests/test_rag_and_citations.py::test_chat_to_ticket_handoff_draft PASSED [ 60%]
tests/test_rag_and_citations.py::test_staff_ai_assistance_endpoints PASSED [ 66%]
tests/test_tickets.py::test_student_ticket_isolation PASSED               [ 73%]
tests/test_tickets.py::test_internal_note_privacy PASSED                  [ 80%]
tests/test_tickets.py::test_student_cannot_add_internal_note PASSED       [ 86%]
tests/test_tickets.py::test_ticket_creation_and_reply PASSED              [ 93%]
tests/test_tickets.py::test_ticket_status_transition_rules PASSED         [100%]

============================== 15 passed in 3.19s ===============================
```

Compile the Vue TypeScript production build:
```bash
cd frontend
npm run build
```

**Results:**
```
✓ built in 11.81s with 0 errors
```

---

## 🔒 Security & Data Privacy

* **Authorization on Every Operation:** Every protected endpoint (ticket views, document downloads, attachment retrieval, chat deletion) verifies ownership and role permissions in the backend.
* **Internal Notes Protection:** Internal notes recorded by staff members are filtered out on the server and never sent in student API responses.
* **Credential Protection:** AI API keys and database credentials are kept exclusively on the backend. No tokens or secrets are committed or exposed in frontend builds.
* **Session Management:** Sensitive tokens are kept out of localStorage by utilizing secure HttpOnly cookies with SameSite lax protection and CSRF token verification for mutating requests.
* **File Upload Hardening:** Server-side UUID filename generation, strict extension and MIME-type validation, size limits (<= 10MB), and path traversal prevention.
* **Prompt Injection Resilience:** User queries and retrieved document chunks are treated as untrusted data wrapped in strict system boundaries.

---

## ⚠️ Known Limitations & Future Roadmap

* **Scanned PDF OCR:** PDFs without embedded text layers generate a clear notification explaining that text could not be extracted. Tesseract / Cloud Vision OCR extraction is planned as a documented future upgrade.
* **WebSockets / Live Updates:** Ticket updates and chat responses currently use standard authenticated REST endpoints. A WebSocket or SSE push notification layer can be added for live multi-agent ticket collaboration.
* **External SIS Integration:** Simulated GPAs and credit totals from the previous client-side demo have been replaced with real database metrics. Live registrar API connections can be plugged into the student profile service via university LDAP / SIS connectors.
