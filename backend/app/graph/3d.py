import json

import matplotlib.pyplot as plt
import numpy as np
from app.services.db.supa_base_client import supa_base_client
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

EMBED_COL = "embedding"
TITLE_COL = "name"
LIMIT = 2000


def fetch_embeddings():
    res = (
        supa_base_client.table("projects")  # type: ignore
        .select(f"id, {TITLE_COL}, {EMBED_COL}")
        .limit(LIMIT)
        .execute()
    )
    rows = res.data or []
    rows = [r for r in rows if r.get(EMBED_COL)]  # type: ignore
    if not rows:
        raise RuntimeError("No rows with non-empty embeddings found in 'projects'.")

    ids = [r["id"] for r in rows]  # type: ignore
    titles = [r.get(TITLE_COL, "Untitled") for r in rows]  # type: ignore

    def parse_embedding(e):
        if isinstance(e, list):
            return e
        if isinstance(e, str):
            # embeddings stored as string like "[0.1, 0.2, ...]"
            return json.loads(e)
        raise TypeError(f"Unexpected embedding type: {type(e)}")

    vectors = np.array([parse_embedding(r[EMBED_COL]) for r in rows], dtype=float)  # type: ignore
    return ids, titles, vectors


def reduce_to_3d(vectors: np.ndarray):
    if vectors.shape[1] <= 3:
        return vectors
    pca = PCA(n_components=3)
    return pca.fit_transform(vectors)


def main():
    ids, titles, vectors = fetch_embeddings()
    reduced = reduce_to_3d(vectors)

    x, y, z = reduced[:, 0], reduced[:, 1], reduced[:, 2]

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(x, y, z, s=5, c="grey", alpha=0.4)  # type: ignore

    ax.set_title("projects – 3D view of embeddings (PCA)")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_zlabel("PC3")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
