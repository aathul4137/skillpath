# SkillPath AI — Personalized Learning Roadmap Generator

A Django app that takes a student's current skills, education, interests,
and target job, and generates a step-by-step learning roadmap — using a
local LLM (via Ollama) with a rule-based fallback so it always works.

```
Current skills → [LLM / rule engine] → Ordered roadmap steps → rendered UI
```

## Project layout

```
skillpath_ai/
├── manage.py
├── requirements.txt
├── skillpath_ai/            # Django project settings/urls
└── roadmap/                 # Main app
    ├── models.py            # StudentProfile, Roadmap, RoadmapStep
    ├── forms.py              # Intake form
    ├── views.py              # home (form) + result (roadmap display)
    ├── urls.py
    ├── admin.py
    ├── services/
    │   ├── recommendation.py # Rule-based path generator (per target job)
    │   └── ollama_service.py # Builds prompt, calls Ollama, parses JSON
    └── templates/roadmap/    # home.html, result.html, base.html
```

## How the recommendation logic works

1. `recommendation.py` holds hand-curated learning paths per target job
   (Data Analyst, Data Scientist, Backend Developer, AI/ML Engineer, Web
   Developer — easy to extend) and fuzzy-matches the student's stated
   target job and existing skills against them.
2. `ollama_service.py` uses that curated path as **grounding context**
   inside the LLM prompt, then asks the local model to adapt/personalize
   it based on the student's interests and education, returning strict
   JSON.
3. If Ollama is unreachable, times out, or returns malformed JSON, the
   view transparently falls back to the pure rule-based path — the user
   never sees an error.

## Setup

```bash
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Visit http://127.0.0.1:8000/

### Enabling the LLM (optional but recommended)

```bash
# Install Ollama: https://ollama.com/download
ollama pull llama3.1
ollama serve
```

By default the app looks for Ollama at `http://localhost:11434` using the
`llama3.1` model. Override with environment variables:

```bash
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.1
```

If Ollama isn't running, roadmaps are still generated via the rule-based
engine — no setup required to demo the app.

## Extending

- **New target jobs**: add an entry to `JOB_PATHS` in
  `roadmap/services/recommendation.py`.
- **Swap the LLM provider**: replace the `requests.post` call in
  `ollama_service.py` with any other chat/completion API — the JSON
  contract (`{"steps": [{"title", "description"}]}`) is all `views.py`
  depends on.
- **Persist richer profiles**: `StudentProfile` currently stores free text
  for skills/interests; swap to `ManyToManyField` relations to a `Skill`
  model if you want structured tagging/search later.
