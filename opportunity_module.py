from duckduckgo_search import DDGS
import datetime

def find_iot_gigs() -> str:
    """Searches the web for high-value IoT and Python freelance jobs."""
    # Simplified query targeting specific platforms
    query = "freelance ESP32 developer OR freelance Python IoT OR remote IoT engineer jobs"
    
    try:
        with DDGS() as ddgs:
            # region='wt-wt' means global, helps bypass local blocks on cloud servers
            results = list(ddgs.text(query, max_results=5, region='wt-wt'))
            
            if not results:
                return "No new opportunities found today. DuckDuckGo may have rate-limited the search."
                
            formatted_leads = []
            for r in results:
                title = r.get("title", "Unknown Title")
                href = r.get("href", "")
                body = r.get("body", "No description.")
                
                formatted_leads.append(f"💡 {title}\n\n{body}\n\nApply Here: {href}")
                
            return "\n\n-------------------\n\n".join(formatted_leads)
            
    except Exception as e:
        return f"Opportunity search failed: {e}"

if __name__ == "__main__":
    print(f"Scanning market for opportunities at {datetime.datetime.now()}...")
    print(find_iot_gigs())