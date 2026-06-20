"""
Template Engine — Jinja2 configuration for dynamic emails and documents.
"""

from pathlib import Path
from fastapi.templating import Jinja2Templates

# Base directory for templates
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template to a string."""
    template = templates.get_template(template_name)
    return template.render(context)
