from duckduckgo_search import DDGS
import datetime

def find_iot_gigs() -> str:
    """Searches the web for high-value IoT and Python freelance jobs."""
    # Targeting specific job boards and high-value keywords
    query = "(ESP32 OR IoT OR Python) AND (freelance OR contract OR hiring) -senior -manager"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "No new opportunities found today."
                
            formatted_leads = []
            for r in results:
                title = r.get("title", "Unknown Title")
                href = r.get("href", "")
                body = r.get("body", "No description.")
                
                # Format the lead for Telegram
                formatted_leads.append(f"💡 *{title}*\n\n_{body}_\n\n🔗 [Apply Here]({href})")
                
            return "\n\n-------------------\n\n".join(formatted_leads)
            
    except Exception as e:
        return f"Opportunity search failed: {e}"

if __name__ == "__main__":
    print(f"Scanning market for opportunities at {datetime.datetime.now()}...")
    print(find_iot_gigs())