import os
import env_loader
import sys
import requests
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TAVILY_KEY = os.environ.get("TAVILY_API_KEYS", "").split(",")[0].strip()

queries = [
    'site:linkedin.com/in/ "Dubai" "Family Office Principal" "+971"',
    'site:linkedin.com/in/ "Dubai" "Founder" ("+971 50" OR "+971 52" OR "+971 55" OR "+971 54")',
    'site:linkedin.com/in/ "Riyadh" ("Founder" OR "CEO") ("+966 5" OR "+9665")',
    '"Family Office" "Dubai" ("Founder" OR "CEO") email OR contact "+971"'
]

for q in queries:
    print(f"\n🔍 Testing Dork: {q}")
    r = requests.post('https://api.tavily.com/search', json={'api_key': TAVILY_KEY, 'query': q, 'max_results': 4})
    if r.status_code == 200:
        for item in r.json().get('results', []):
            title = item.get('title', '')
            content = item.get('content', '')
            phones = re.findall(r'(?:\+971|\+966|00971|00966)[\s\d-]{8,15}', content + ' ' + title)
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content)
            print(f"  • Title: {title}")
            print(f"    URL: {item.get('url')}")
            if phones:
                print(f"    📞 Phone(s): {list(set(phones))}")
            if emails:
                print(f"    ✉️ Email(s): {list(set(emails))}")
            if not phones and not emails:
                print("    Snippet: " + content[:120] + "...")
