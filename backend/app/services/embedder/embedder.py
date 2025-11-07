import os

from app.services.db.supa_base_client import supa_base_client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai_client = OpenAI(api_key=OPENAI_KEY)

EMBEDDING_MODEL = "text-embedding-3-small"


def embded_query(text: str):
    """Generate embedding for a given text query."""
    embedding = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return embedding.data[0].embedding


def store_in_db_yc(projects):
    """Generate Embedding and store in Supabase."""
    for project in projects:
        existing = (
            supa_base_client.table("projects")
            .select("id")
            .eq("url", project.url)
            .execute()
        )
        if existing.data:
            print(f"Skipping storing : {project.name}")
            continue
        # ---- Generate embedding with important fields ----
        text_to_embed = f"""
        Project name: {project.name}
        Short description: {project.short_description}
        Long description: {project.long_description}
        Tags: {", ".join(project.tags)}
        Batch: {project.batch}
        Source: {project.source}
        """
        embedding = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text_to_embed,
        )

        # ---- Group data and store in Supabase ----
        data = {
            "name": project.name,
            "short_description": project.short_description,
            "long_description": project.long_description,
            "tags": project.tags,
            "source": project.source,
            "url": project.url,
            "embedding": embedding.data[0].embedding,
            "metadata": {
                "batch": project.batch,
                "founded": project.founded,
                "team_size": project.team_size,
                "status": project.status,
                "primary_partner": project.primary_partner,
                "location": project.location,
            },
        }
        supa_base_client.table("projects").insert(data).execute()
