# UniDesk — AI University Help Desk & Ticketing Platform

> A full-stack AI-powered university support portal built for Sri Lankan university students.  
> Built with **Vue 3 + FastAPI + Google Gemini AI**

---

## 📌 About This Project

**UniDesk** is a university help desk and ticketing system that I developed as a personal project to simulate how a real university student support portal could work in Sri Lanka.

Students can chat with an AI assistant that answers questions about Mahapola scholarships, LMS access, exam results, library hours, admissions requirements, and more — all grounded in official university documents. When the AI cannot help, students can raise a support ticket which is handled by department staff.

---

## ✨ Features

- 🤖 **AI Chatbot** — Answers student questions using official university documents (RAG-based, no hallucinations)
- 🎫 **Support Tickets** — Students raise tickets; staff respond and resolve them
- 📢 **University Notices** — Important announcements from the university
- 📚 **Knowledge Base** — Mahapola, LMS, exams, admissions, library docs
- 🔐 **Role-Based Access** — Student / Staff / Admin with separate dashboards
- 🌐 **Tri-Lingual** — English, Sinhala (සිංහල), Tamil (தமிழ்)
- 🔊 **Text-to-Speech** — Read AI answers aloud
- 📄 **Document Upload** — Admins upload PDF/DOCX; AI reads and indexes them

---

## 🛠️ Tech Stack

| Part | Technology |
|------|-----------|
| Frontend | Vue 3, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite (dev) / PostgreSQL (production) |
| AI | Google Gemini API + RAG (Retrieval-Augmented Generation) |
| Auth | JWT tokens, Bcrypt password hashing |
| Deploy | Docker, Docker Compose, Nginx |

---

## 🚀 How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/reezmahanan/UniDesk.git
cd UniDesk
```

### 2. Start the Backend

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

> ✅ The database is created and seeded automatically on first run.  
> Backend runs at: **http://localhost:8000**  
> API docs: **http://localhost:8000/docs**

---

### 3. Start the Frontend

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

> Frontend runs at: **http://localhost:5173**

---

### 4. Using Docker (Optional — Runs Everything Together)

```bash
# Copy environment file
cp .env.example .env

# Build and run everything
docker compose up --build
```

> Opens at: **http://localhost**

---

## 👤 Demo Login Accounts

Use these accounts to explore the platform:

| Name | Email | Password | Role |
|------|-------|----------|------|
| Kasun Jayasundara | `student@apex.edu.lk` | `student123` | 🎓 Student |
| Sanduni Perera | `sanduni@apex.edu.lk` | `student123` | 🎓 Student |
| Dr. Priyantha Alwis | `staff@apex.edu.lk` | `staff123` | 👨‍💼 Staff |
| University Admin | `admin@apex.edu.lk` | `admin123` | 🔑 Admin |

> 💡 You can also switch demo roles using the **Demo Role** button in the top bar.

---

## 🤖 How the AI Works

The chatbot uses a **RAG (Retrieval-Augmented Generation)** approach:

1. Student asks a question
2. System searches university documents for relevant information
3. Retrieved content is passed to **Google Gemini AI**
4. AI generates a grounded answer with document citations
5. If no relevant document is found → suggests creating a support ticket

This means the AI only answers from approved university documents — it does **not** make things up.

---

## 📂 Project Structure

```
UniDesk/
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── api/           # API route handlers
│   │   ├── models/        # Database models
│   │   ├── services/      # RAG, embeddings, file processing
│   │   └── seed.py        # Demo data seeder
│   ├── storage/documents/ # University knowledge documents
│   └── requirements.txt
│
├── frontend/              # Vue 3 frontend
│   └── src/
│       ├── views/         # Pages (Chat, Tickets, Dashboard...)
│       ├── components/    # Reusable components
│       ├── stores/        # Pinia state management
│       └── router/        # Vue Router
│
├── docker-compose.yml
└── README.md
```

---

## 📖 University Topics the AI Can Answer

- 🏦 **Mahapola Scholarship** — How to collect vouchers, eligibility, BOC payment
- 💻 **LMS / Student Portal** — Password reset, account locked, WiFi setup
- 📝 **Examinations** — How to check results, re-sit exams, transcripts
- 🎓 **Admissions** — A/L requirements, student ID, registration documents
- 📚 **Library** — Opening hours, book reservations

---

## ⚠️ Note

This is a **student project** built for learning purposes. The university name "Apex University" and all data used are fictional demo data.

---

## 👨‍💻 Developer

**Reezmahanan**  
GitHub: [@reezmahanan](https://github.com/reezmahanan)
