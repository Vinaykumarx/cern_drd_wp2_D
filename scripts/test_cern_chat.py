import requests
import json
import time

API_BASE = "http://localhost:8020/api"

print("1. Creating Session...")
sess_res = requests.post(f"{API_BASE}/sessions", json={"title": "Automated Testing"})
session_id = sess_res.json()["id"]
print(f"Session ID: {session_id}")

print("2. Asking Question about CERN Yellow Reports...")
payload = {
    "session_id": session_id,
    "message": "What does the CERN Yellow Report recommend regarding radiation shielding and experimental safety parameters?",
    "temperature": 0.1,
    "model": "anthropic/claude-3.5-sonnet"
}

start_time = time.time()
chat_res = requests.post(f"{API_BASE}/chat", json=payload)
end_time = time.time()

if chat_res.status_code == 200:
    data = chat_res.json()
    print(f"\n[Response Time: {end_time - start_time:.2f}s]")
    print("\n--- Answer ---")
    print(data.get("content", ""))
    
    print("\n--- Sources (Hits) ---")
    for idx, hit in enumerate(data.get("hits", [])):
        print(f"Hit {idx+1}: Score={hit.get('score', 'N/A')} Doc={hit.get('doc_id')} Page={hit.get('page')} Topic={hit.get('topic')}")
        
    print("\n--- Suggested Links ---")
    for link in data.get("suggested_links", []):
        print(f"Link: {link}")
else:
    print(f"Error: {chat_res.status_code}")
    print(chat_res.text)

