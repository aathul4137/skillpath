"""
Wraps calls to a local Ollama server to generate a personalized roadmap.

Ollama must be running locally, e.g.:
    ollama serve
    ollama pull llama3.1

If Ollama is unreachable, unresponsive, or returns malformed JSON, we
transparently fall back to the rule-based recommendation engine so the
app never breaks for the end user.
"""
import json
import logging

import requests
from django.conf import settings

from . import recommendation

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = """You are a career mentor AI that builds personalized learning roadmaps.

Student profile:
- Current skills: {skills}
- Education: {education}
- Interests: {interests}
- Target job: {target_job}

Suggested reference path for this target job (use as grounding, adapt as needed
based on the student's existing skills and interests — skip anything they
already know):
{reference_path}

Task: Produce a step-by-step learning roadmap (4 to 7 steps) that takes this
student from their current skills to being job-ready for the target role.

Respond with ONLY valid JSON (no markdown, no commentary) in exactly this shape:
{{
  "steps": [
    {{"title": "Short skill/topic name", "description": "One sentence on why/what to learn"}}
  ]
}}
"""


def _build_prompt(profile) -> str:
    reference = recommendation.recommend(profile)
    reference_lines = "\n".join(f"- {s['title']}: {s['description']}" for s in reference)
    return PROMPT_TEMPLATE.format(
        skills=profile.current_skills,
        education=profile.education,
        interests=profile.interests,
        target_job=profile.target_job,
        reference_path=reference_lines,
    )


def _parse_llm_json(text: str) -> list:
    text = text.strip()
    # Models sometimes wrap JSON in ```json fences despite instructions.
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.lower().startswith("json"):
            text = text[4:]
    data = json.loads(text)
    steps = data["steps"]
    if not isinstance(steps, list) or not steps:
        raise ValueError("No steps returned by model")
    cleaned = []
    for s in steps:
        cleaned.append(
            {
                "title": str(s.get("title", "")).strip() or "Untitled step",
                "description": str(s.get("description", "")).strip(),
            }
        )
    return cleaned


def generate_roadmap(profile):
    """
    Returns a tuple: (steps, source, raw_response)
      steps -> list[{"title", "description"}]
      source -> "llm" or "rules"
      raw_response -> raw text from the model (empty string if not used)
    """
    prompt = _build_prompt(profile)
    url = f"{settings.OLLAMA_HOST}/api/generate"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.4},
    }

    try:
        response = requests.post(url, json=payload, timeout=settings.OLLAMA_TIMEOUT)
        response.raise_for_status()
        raw_text = response.json().get("response", "")
        steps = _parse_llm_json(raw_text)
        return steps, "llm", raw_text
    except Exception as exc:  # noqa: BLE001 - any failure should trigger fallback
        logger.warning("Ollama generation failed, falling back to rules: %s", exc)
        steps = recommendation.recommend(profile)
        return steps, "rules", ""
