"""
This script reads a JSON file that was outputed from devpost.py scraper. It will use all of the data from the JSON
in order to append to the Supabase 'projects' table with embeddings generated from OpenAI.
"""
import os 
from supabase import create_client, Client
from openai import OpenAI
import json
import dotenv

dotenv.load_dotenv()

url: str = os.getenv("SUPABASE_URL")
apiKey: str = os.getenv("SUPABASE_API_KEY")
openAiKey = os.getenv("OPENAI_API_KEY")

supabase: Client = create_client(url, apiKey)
openmod = OpenAI(api_key=openAiKey)
EMBED_MODEL = "text-embedding-3-small"

# Load the JSON file
# THE FILE MUST BE IN SAME DIRECTORY AS THIS FOLDER, RIGHT NOW IT IS IN /backend/app/services/scraper/
# CHANGE PATH WHEN NEEDED
with open("devpost_dump.json", "r", encoding="utf-8") as f:
    projects = json.load(f)
    #print(projects)

count = 0

def supaCheck(link: str) -> bool:
    """
    Return True if the link already exists in projects.url, else False.
    On error, returns True to avoid duplicate inserts.
    """
    if not link:
        return False 

    try:
        res = (
            supabase.table("projects")
            .select("url", count="exact")
            .eq("url", link)
            .limit(1)
            .execute()
        )
        # res.data is [] when not found
        return bool(res.data)
    except Exception as e:
        print(f"Error checking link {link}: {e}")
        return True  # fail closed


#Iterate through every item in the projects json file
for item in projects:

    # Prepare the text to embed
    embed_text = " ".join(filter(None, [
        item.get("name"),
        item.get("short_description"),
        item.get("long_description"),
        item.get("source"),
    ]))

    # Check if the URL is already in the supabase table
    if supaCheck(item.get("url")):
        print("Skipping project since found in supabase:", item.get("url"))
        continue

    # create embedding
    response = openmod.embeddings.create(
        input=embed_text,
        model=EMBED_MODEL,
    )
    emb = response.data[0].embedding

    #Print the number of the item being inserted:
    count += 1
    print(f"Inserting project # {count}, Name: {item.get('name')}")

    # insert
    supaResponse = (
        supabase.table("projects")
        .insert({
            "name": item.get("name"),
            "short_description": item.get("short_description"),
            "long_description": item.get("long_description"),
            "tags": item.get("tags") or [],
            "source": item.get("source"),
            "url": item.get("url"),
            "embedding": emb,
        })
        .execute()
    )
    print(supaResponse)