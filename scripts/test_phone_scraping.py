import os
import env_loader
import sys
import requests
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TAVILY_KEY = os.environ.get("TAVILY_API_KEYS", "").split(",")[0].strip()

def test_phone_dork(query):
    payload = {
        'api_key': TAVILY_KEY,
        'query': query,
        'max_results': 5
    }
    resp = requests.post('https://api.tavily.com/search', json=payload, timeout=10)
    if resp.status_code == 200:
        results = resp.json().get('results', [])
        print(f"\n🔍 Query: {query}")
        print("="*60)
        for r in results:
            content = r.get('content', '')
            title = r.get('title', '')
            url = r.get('url', '')
            
            # Extract international phone numbers (+971, +966, etc.)
            phones = re.findall(r'(?:\+971|\+966|\+974|00971|00966)[\s\d-]{8,14}', content)
            print(f"Title: {title}")
            print(f"URL: {url}")
            if phones:
                print(f"📞 Detected Phone Numbers: {list(set(phones))}")
            else:
                print("No direct mobile pattern in snippet.")
            print("-" * 50)

if __name__ == "__main__":
    # Test 1: UAE Family Office Principal / Chairman
    test_phone_dork('"Al Habtoor Group" ("Chairman" OR "Executive Office") contact ("+971" OR "phone")')
    
    # Test 2: Dubai Real Estate Founder / Managing Director
    test_phone_dork('"Sobha Realty" "PNC Menon" OR "Francis Alfred" ("+971" OR "phone" OR "office")')

    # Test 3: UAE Executive Office / Secretary Direct Line
    test_phone_dork('"Damac Properties" "Hussain Sajwani" office phone OR contact')
