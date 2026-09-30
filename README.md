# AI Study Hub

A Django (MVT) web application that helps students organize tasks, notes, and
learning resources, with an integrated AI study assistant.

Built for the "Django Web Development" course project — see
`AI_Study_Hub_Project_Specification.docx` for the original brief.

## Features

- **Authentication**: register, login, logout, profile page, password change/reset, email verification
- **Dashboard**: task/note/resource counters, priority chart, recent activity feed
- **Study Planner**: full task CRUD, due dates, priorities, completion toggle, categories
- **Notes**: full CRUD, categories, search, AI-generated summaries
- **Resources**: full CRUD, resource types, categories, thumbnails
- **Global live search** (JavaScript, no page reload) across notes/tasks/resources
- **AI Chat Assistant**: multi-conversation chat backed by any OpenAI-compatible API
- **Dark mode**, **pagination**, **image upload**, **PDF export** of tasks, **charts** (Chart.js)
- Plain Django (MVT) throughout — **no Django REST Framework**

## Tech stack

Django · PostgreSQL · HTML/CSS/JavaScript (vanilla) · Chart.js · ReportLab (PDF)

## Project structure

```
ai_study_hub/
├── accounts/       # Auth, Profile, email verification
├── planner/        # Task model + CRUD
├── notes/          # Note + Category models + CRUD + AI summarize
├── resources/      # Resource + ResourceType models + CRUD
├── ai_assistant/   # Conversation + Message models, chat views, AI service layer
├── dashboard/       # Dashboard view, PDF export
├── core/           # Shared ActivityLog model, global search, dark-mode toggle
├── templates/       # All HTML templates (base.html + per-app folders)
├── static/          # CSS + JS
├── config/          # Django project settings/urls
└── manage.py
```

## Setup

### 1. Clone & create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:
- Set `DJANGO_SECRET_KEY` to any random string.
- Fill in your PostgreSQL credentials (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`).
  Create the database first: `createdb ai_study_hub` (or via pgAdmin).
- **Quick testing without Postgres**: set `USE_SQLITE=True` and skip the DB_* settings.
- To enable real AI responses, get an API key from an OpenAI-compatible provider
  and set `AI_API_KEY` (and `AI_API_URL` / `AI_MODEL` if not using OpenAI itself).
  **Without a key, the AI assistant still works** — it returns a clearly-labelled
  placeholder response so the rest of the app can be demoed/graded offline.
- For real password-reset/verification emails, set `EMAIL_BACKEND` to an SMTP
  backend and fill in `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`. Left as-is,
  emails are printed to the console — fine for local demos.

### 3. Run migrations & load starter data

```bash
python manage.py migrate
python manage.py loaddata resources/fixtures/resource_types.json
python manage.py createsuperuser
```

### 4. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`, register an account, and explore. The admin
site is at `/admin/`.

## AI feature — how it works

`ai_assistant/services.py` wraps any OpenAI-compatible `/chat/completions`
endpoint. `chat_reply()` powers the multi-turn chat assistant (`/ai/`) and
`summarize_text()` powers the "Generate summary" button on each note. Swap
providers by changing `AI_API_URL` / `AI_MODEL` in `.env` — e.g. Groq,
OpenRouter, or a self-hosted OpenAI-compatible server all work without code
changes.

## Database design (ERD)

11 related tables, using both One-to-Many and Many-to-Many relationships:

```
User (Django built-in)
 │ 1─1
 ▼
Profile ───────────────────────────────┐
 │                                       │
 │ 1─N                                   │ 1─N
 ▼                                       ▼
EmailVerificationToken            ActivityLog

User 1──N Task ───────M2M──────── Category ──M2M── Resource
              (categories)                      (categories)
                                     │ N─1
                                     ▼
                                    User

User 1──N Note ──M2M── Category
User 1──N Resource ──N─1── ResourceType

User 1──N Conversation 1──N Message
```

**Tables**: User, Profile, EmailVerificationToken, Category, Task, Note,
Resource, ResourceType, Conversation, Message, ActivityLog.

**Relationships**:
- One-to-One: `User` ↔ `Profile`
- One-to-Many: `User → Task`, `User → Note`, `User → Resource`,
  `User → Category`, `User → Conversation`, `Conversation → Message`,
  `User → ActivityLog`, `ResourceType → Resource`
- Many-to-Many: `Task ↔ Category`, `Note ↔ Category`, `Resource ↔ Category`

## Screenshots

_Add screenshots of the running app here before submission (Dashboard, Tasks,
Notes, Resources, AI Chat, Dark mode)._

## Deliverables checklist (per spec)

- [x] Complete source code
- [ ] PostgreSQL database backup (`pg_dump ai_study_hub > backup.sql` once you have real data)
- [x] requirements.txt
- [x] README.md
- [ ] Screenshots
- [ ] Git & GitHub (push this folder to a new repo)
- [x] ERD (see above)
- [ ] LinkedIn video post (optional)
