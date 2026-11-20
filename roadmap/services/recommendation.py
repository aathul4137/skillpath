"""
Rule-based recommendation logic.

This acts as:
1. A guaranteed fallback if Ollama is unreachable or returns something
   unparsable, so the product always works end-to-end.
2. A source of "known good" learning paths that can be fed into the LLM
   prompt as grounding context, so the model doesn't hallucinate a path
   that skips fundamentals.

Extend JOB_PATHS with more roles as needed.
"""
from difflib import SequenceMatcher

JOB_PATHS = {
    "data analyst": [
        ("Pandas", "Data manipulation and cleaning with the Pandas library."),
        ("Data Visualization", "Communicate insights using Matplotlib/Seaborn/Plotly."),
        ("Statistics", "Descriptive & inferential statistics for analysis."),
        ("Power BI", "Build interactive dashboards for business stakeholders."),
        ("SQL for Analytics", "Window functions, CTEs, and query optimization."),
        ("Portfolio Projects", "3 end-to-end analysis projects for your resume."),
    ],
    "data scientist": [
        ("Pandas & NumPy", "Core data wrangling and numerical computing."),
        ("Statistics & Probability", "Hypothesis testing, distributions, A/B testing."),
        ("Machine Learning Fundamentals", "Regression, classification, clustering with scikit-learn."),
        ("Data Visualization", "Storytelling with data using Seaborn/Plotly."),
        ("Deep Learning Basics", "Neural networks with PyTorch or TensorFlow."),
        ("Portfolio Projects", "Kaggle competitions or applied ML projects."),
    ],
    "backend developer": [
        ("Advanced Python", "OOP, decorators, async, and testing."),
        ("Django / REST APIs", "Build and secure production-grade APIs."),
        ("Databases", "Relational modeling, indexing, migrations."),
        ("Docker & Deployment", "Containerize and ship your applications."),
        ("System Design Basics", "Caching, load balancing, scaling."),
        ("Portfolio Projects", "2-3 deployed backend projects with docs."),
    ],
    "ai/ml engineer": [
        ("Python for ML", "NumPy, Pandas, and vectorized computation."),
        ("Machine Learning", "Core algorithms with scikit-learn."),
        ("Deep Learning", "PyTorch/TensorFlow, CNNs, RNNs, Transformers."),
        ("MLOps Basics", "Model versioning, deployment, monitoring."),
        ("LLMs & Prompt Engineering", "Working with open and closed-source LLMs."),
        ("Portfolio Projects", "Deploy at least one ML model as an API."),
    ],
    "web developer": [
        ("HTML/CSS/JavaScript", "Solid fundamentals of the web platform."),
        ("Frontend Framework", "React or Vue for interactive UIs."),
        ("Backend Basics", "Django/Node.js and REST APIs."),
        ("Databases", "SQL/NoSQL fundamentals."),
        ("Deployment", "CI/CD, hosting, and domains."),
        ("Portfolio Projects", "3 deployed full-stack projects."),
    ],
}

DEFAULT_PATH = [
    ("Core Fundamentals", "Solidify the basics relevant to your target role."),
    ("Applied Practice", "Hands-on exercises using real datasets/problems."),
    ("Specialized Tools", "Industry-standard tools for the target role."),
    ("Portfolio Projects", "Build 2-3 projects to showcase on your resume."),
]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _closest_job_key(target_job: str, threshold: float = 0.5):
    target_job = target_job.lower().strip()
    if target_job in JOB_PATHS:
        return target_job
    best_key, best_score = None, 0.0
    for key in JOB_PATHS:
        score = _similarity(target_job, key)
        if score > best_score:
            best_key, best_score = key, score
    return best_key if best_score >= threshold else None


def _already_known(skill_title: str, known_skills: list) -> bool:
    return any(_similarity(skill_title, known) > 0.6 for known in known_skills)


def recommend(profile) -> list:
    """
    Returns an ordered list of dicts: [{"title": ..., "description": ...}, ...]
    tailored to the student's profile using simple rule-based matching.
    """
    job_key = _closest_job_key(profile.target_job)
    path = JOB_PATHS.get(job_key, DEFAULT_PATH)
    known_skills = profile.skills_list()

    steps = []
    for title, description in path:
        if not _already_known(title, known_skills):
            steps.append({"title": title, "description": description})

    # If the student already knows everything on the path, still give them
    # something to do next.
    if not steps:
        steps = [{"title": "Advanced Specialization", "description": "Deepen expertise and build advanced projects."}]

    return steps
