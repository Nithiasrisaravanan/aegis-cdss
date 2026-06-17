import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from nih_api import search_disease_evidence

model = SentenceTransformer('all-MiniLM-L6-v2')

def build_index(articles: list):
    texts = []
    for a in articles:
        text = f"{a['title']}. {a.get('abstract', '')}"
        texts.append(text)
    if not texts:
        return None, [], []
    embeddings = model.encode(texts, convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index, embeddings, texts

def query_index(index, texts, articles, query: str, top_k: int = 5):
    q_emb = model.encode([query], convert_to_numpy=True)
    q_emb = q_emb / np.linalg.norm(q_emb, axis=1, keepdims=True)
    scores, indices = index.search(q_emb, min(top_k, len(texts)))
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < len(articles):
            article = articles[idx].copy()
            article["relevance"] = round(float(score) * 100, 1)
            results.append(article)
    results.sort(key=lambda x: x["relevance"], reverse=True)
    return results

def retrieve_evidence(disease: str, features: list, query: str = None, top_k: int = 10) -> list:
    articles = search_disease_evidence(disease, features, max_results=top_k)
    if not articles:
        return []
    index, embeddings, texts = build_index(articles)
    if index is None:
        return articles
    search_query = query or f"{disease} {' '.join(features[:3])}"
    ranked = query_index(index, texts, articles, search_query, top_k=top_k)
    return ranked

if __name__ == '__main__':
    print("Building FAISS index from PubMed...")
    results = retrieve_evidence(
        disease="heart disease",
        features=["chest pain", "cholesterol", "thalach"],
        query="heart disease risk factors diagnosis"
    )
    print(f"\nTop {len(results)} ranked articles:")
    for r in results[:3]:
        print(f"\n  [{r['relevance']}%] {r['title'][:70]}")
        print(f"  PMID: {r['pmid']} | {r['journal']} | {r['year']}")
