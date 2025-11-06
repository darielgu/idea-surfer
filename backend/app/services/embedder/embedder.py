from app.services.db.supa_base_client import supa_base_client
from openai import OpenAI

openai_client = OpenAI()

EMBEDDING_MODEL = "text-embedding-3-small"


def store_in_db(projects):
    """Generate Embedding and store in Supabase."""
    for project in projects:
        text_to_embed = f"""
        Project name: {project["name"]}
        Short description: {project.get("short_description")}
        Long description: {project.get("long_description")}
        Tags: {", ".join(project.get("tags", []))}
        Batch: {project.get("batch")}
        Source: {project.get("source")}
        """
