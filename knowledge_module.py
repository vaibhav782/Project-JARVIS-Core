import chromadb
import os

# Initialize a persistent local database in a folder named "jarvis_db"
client = chromadb.PersistentClient(path="./jarvis_db")

# Create or get a collection (like a table in SQL)
collection = client.get_or_create_collection(name="jarvis_knowledge")

def ingest_document(file_path: str):
    """Reads a text file and stores it in the vector database."""
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
        
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    # Create a unique ID based on the filename
    doc_id = os.path.basename(file_path)
    
    # Add to the database
    collection.add(
        documents=[content],
        metadatas=[{"source": doc_id}],
        ids=[doc_id]
    )
    return f"Successfully ingested {doc_id} into JARVIS's memory."

def query_knowledge(query: str, n_results: int = 1):
    """Searches the database for information related to the query."""
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    if results['documents']:
        return results['documents'][0][0]
    return "No relevant knowledge found."

if __name__ == "__main__":
    # Auto-ingest all files in the knowledge_base folder
    folder_path = "knowledge_base"
    if os.path.exists(folder_path):
        print(f"Scanning {folder_path} for documents to ingest...")
        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)
                print(ingest_document(file_path))
    else:
        print("knowledge_base folder not found.")
        
    # Test query
    print("\nQuerying JARVIS knowledge...")
    print(query_knowledge("What is the business plan?"))