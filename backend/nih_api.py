import requests
import time

BASE_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
BASE_EFETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
BASE_ESUM    = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def search_pubmed(query: str, max_results: int = 10) -> list:
    params = {
        "db": "pubmed", "term": query,
        "retmax": max_results, "retmode": "json"
    }
    r = requests.get(BASE_ESEARCH, params=params, timeout=30)
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    return ids

def fetch_summaries(pmids: list) -> list:
    if not pmids:
        return []
    params = {
        "db": "pubmed", "id": ",".join(pmids),
        "retmode": "json"
    }
    r = requests.get(BASE_ESUM, params=params, timeout=30)
    result = r.json().get("result", {})
    articles = []
    for pmid in pmids:
        item = result.get(pmid, {})
        if not item:
            continue
        authors = item.get("authors", [])
        author_str = authors[0].get("name", "") if authors else "Unknown"
        articles.append({
            "pmid": pmid,
            "title": item.get("title", "No title"),
            "journal": item.get("fulljournalname", "Unknown Journal"),
            "year": item.get("pubdate", "")[:4],
            "authors": author_str,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        })
    time.sleep(0.34)
    return articles

def fetch_abstract(pmid: str) -> str:
    params = {
        "db": "pubmed", "id": pmid,
        "rettype": "abstract", "retmode": "text"
    }
    r = requests.get(BASE_EFETCH, params=params, timeout=30)
    return r.text.strip()

def search_disease_evidence(disease: str, features: list, max_results: int = 10) -> list:
    feature_str = " OR ".join(features[:3])
    query = f"({disease}[Title/Abstract]) AND ({feature_str}[Title/Abstract])"
    pmids = search_pubmed(query, max_results)
    articles = fetch_summaries(pmids)
    for article in articles:
        abstract = fetch_abstract(article["pmid"])
        article["abstract"] = abstract[:500] if abstract else "Abstract not available."
    return articles

if __name__ == '__main__':
    results = search_disease_evidence(
        "heart disease",
        ["chest pain", "cholesterol", "blood pressure"]
    )
    print(f"Found {len(results)} articles")
    for a in results[:2]:
        print(f"\n  {a['title'][:80]}")
        print(f"  {a['journal']} · {a['year']} · PMID: {a['pmid']}")