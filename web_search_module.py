from duckduckgo_search import DDGS

def search_web(query: str, max_results: int = 3) -> str:
    """Searches the web for the query and returns formatted text results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
            if not results:
                return "No results found."
                
            formatted_results = []
            for r in results:
                title = r.get("title", "")
                body = r.get("body", "")
                href = r.get("href", "")
                formatted_results.append(f"Title: {title}\nSummary: {body}\nLink: {href}")
                
            return "\n\n".join(formatted_results)
            
    except Exception as e:
        return f"Search failed: {e}"