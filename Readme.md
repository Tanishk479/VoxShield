# VoxShield 🛡️
> Real-Time Voice Cloning & Indian Scam Protection Engine

> **⚠️ DEMO MVP NOTICE**  
> This project is currently a **Demonstration Minimum Viable Product (Demo MVP)** developed for testing and proof-of-concept evaluation. Certain features, detection thresholds, and integrations are actively in progress.

---

## 🏗️ Architecture

- **Frontend**: Next.js 16 (App Router), Tailwind CSS, Recharts, Lucide Icons
- **Backend**: FastAPI (Python), Uvicorn, Asynchronous Stream Processing
- **Detection Mesh**: Acoustic spectral verification, multilingual ASR analysis, contextual heuristic scoring

---

## 🚀 Quick Start

### 1. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
2. Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
Open http://localhost:3000 to view the VoxShield Operations Center.
```
⚙️ Environment Variables

Frontend (frontend/.env.local)

NEXT_PUBLIC_API_URL=http://localhost:8000

Backend (backend/.env)

SECRET_KEY=your_secret_key_here

📦 Deployment Status

Frontend: Live on Vercel

Backend: FastAPI / Render
