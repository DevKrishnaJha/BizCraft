# BizCraft

### Your business. Your website. Built by AI.

BizCraft is an AI-powered website builder designed specifically for local businesses and small business owners.

Instead of starting with a blank page, business owners can provide their business information, receive an AI-generated business analysis and website blueprint, choose a design, preview their website and export the finished website as a ZIP file.

## Features

- **Business onboarding:** Add business information manually.
- **AI business analysis:** Analyse business information and identify important website requirements.
- **Website blueprint:** Generate a structured plan for the business website.
- **Design selection:** Choose from multiple design styles.
- **AI website generation:** Generate complete static websites.
- **Live preview:** Preview generated websites in desktop and mobile layouts.
- **ZIP export:** Download generated websites and their assets.
- **Business lookup:** Retrieve business information using supported search and lookup integrations.
- **Business management:** View and delete saved business profiles.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript |
| Styling | Tailwind CSS |
| Icons | Lucide React |
| Backend | Python, FastAPI |
| Database | SQLite |
| AI | Groq API |
| Business lookup | Browser Search / location data integrations |
| Website output | HTML, CSS, JavaScript |
| Version control | Git, GitHub |

## Architecture

BizCraft uses a separate frontend and backend.

```text
BizCraft/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── generators/
│   │   ├── providers/
│   │   ├── schemas/
│   │   └── services/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   └── components/
│   ├── package.json
│   └── vite.config.ts
│
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js and npm
- Git
- Required API credentials for enabled integrations

### 1. Clone the repository

```bash
git clone https://github.com/DevKrishnaJha/BizCraft.git
cd BizCraft
```

### 2. Set up the backend

```bash
cd backend

python -m venv venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```powershell
Copy-Item .env.example .env
```

Add the required API credentials and configuration to `backend/.env`.

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Backend: `http://127.0.0.1:8000`

API documentation: `http://127.0.0.1:8000/docs`

### 3. Set up the frontend

Open another terminal:

```bash
cd frontend

npm install
npm run dev
```

Frontend: `http://localhost:5173`

## Generated Websites

BizCraft generates static websites using:

- HTML5
- CSS3
- Vanilla JavaScript

Generated websites can be previewed within BizCraft and exported as ZIP archives.

## Security

- API credentials belong in environment variables.
- Never commit `.env` files or private API keys.
- The backend handles integrations requiring secret credentials.

## Project Status

**BizCraft V1**

Core website-building functionality has been implemented, including business onboarding, AI-assisted planning, website generation, previews, ZIP export and business management.

Deployment and further improvements are ongoing.

## Future Improvements

Potential future development includes:

- Public website publishing
- More design templates
- Improved business data accuracy
- Additional customization options
- Persistent production database storage

## Repository

[GitHub - DevKrishnaJha/BizCraft](https://github.com/DevKrishnaJha/BizCraft)

---

**BizCraft**

*Built to make professional websites more accessible to local businesses.*