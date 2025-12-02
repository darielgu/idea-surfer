"""
Docstring for backend.app.services.visualizer.visualize

This module provides functionality to visualize high-dimensional embeddings
stored in a Supabase database by reducing their dimensionality to 3D using PCA
and plotting them in a 3D scatter plot.

"""

import os
from dotenv import load_dotenv
import numpy as np
from supabase import create_client, Client
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# pull embeddings (adjust table/column names as needed)
res = supabase.table("projects").select("id, embedding").execute()

rows = res.data
print("Number of rows:", len(rows))

# Supabase returns the vector column as a Python list; we stack into a matrix
ids = [r["id"] for r in rows]
# Validate and clean embeddings before constructing the matrix
valid_rows = []
invalid = []
for r in rows:
    emb = r.get("embedding")
    rid = r.get("id")
    if emb is None:
        invalid.append((rid, "None"))
        continue
    # If embedding stored as JSON/string, try to parse
    if isinstance(emb, str):
        try:
            import json

            emb = json.loads(emb)
        except Exception:
            try:
                emb = eval(emb)  # fallback for python-list-like strings
            except Exception:
                invalid.append((rid, "string-unparseable"))
                continue
    # Ensure iterable
    if not hasattr(emb, "__iter__"):
        invalid.append((rid, "not-iterable"))
        continue
    # Convert to numeric numpy array
    try:
        emb_arr = np.array(list(emb), dtype=float)
    except Exception:
        invalid.append((rid, "non-numeric"))
        continue
    valid_rows.append((rid, emb_arr))

if not valid_rows:
    raise ValueError("No valid embeddings found in `projects.embedding`. Check your table data.")

from collections import Counter
lengths = [v.shape[0] for _, v in valid_rows]
most_common_len = Counter(lengths).most_common(1)[0][0]
filtered = [(i, v) for i, v in valid_rows if v.shape[0] == most_common_len]
if len(filtered) < len(valid_rows):
    print(f"Warning: {len(valid_rows)-len(filtered)} embeddings had differing dimensionality and were dropped.")

ids = [i for i, _ in filtered]
embeddings = np.vstack([v for _, v in filtered])  # shape: (N, D)
print("Embeddings shape:", embeddings.shape)
if invalid:
    print(f"Dropped {len(invalid)} invalid rows. Examples: {invalid[:5]}")

pca = PCA(n_components=3)
embeddings_3d = pca.fit_transform(embeddings)

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")

ax.scatter(
    embeddings_3d[:, 0],
    embeddings_3d[:, 1],
    embeddings_3d[:, 2],
    s=5,
    alpha=0.6,
)

ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")
ax.set_title("projects – 3D view of embeddings (PCA)")

plt.tight_layout()
plt.show()