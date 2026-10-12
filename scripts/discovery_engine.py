"""
=============================================================================
INDULGE GLOBAL - MULTI-API ROTATING DISCOVERY ENGINE
=============================================================================
Combines Tavily API multi-key pool, BrowserAct, and Fallback SERP
to discover Middle East HNI/UHNI executives with zero rate-limit blocks.
=============================================================================
"""

import time
import requests
import re

import os
import env_loader

TAVILY_KEYS = [k.strip() for k in os.environ.get("TAVILY_API_KEYS", "").split(",") if k.strip()]
if not TAVILY_KEYS:
    TAVILY_KEYS = [k.strip() for k in os.environ.get("TAVILY_API_KEYS", "").split(",") if k.strip()]

BROWSERACT_KEY = os.environ.get("BROWSERACT_KEY", "")

_current_key_idx = 0

def get_next_tavily_key():
    global _current_key_idx
    key = TAVILY_KEYS[_current_key_idx]
    _current_key_idx = (_current_key_idx + 1) % len(TAVILY_KEYS)
    return key

def search_tavily(query_str, max_results=7):
    attempts = len(TAVILY_KEYS)
    for _ in range(attempts):
        key = get_next_tavily_key()
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {
                'api_key': key,
                'query': query_str,
                'max_results': max_results
            }
            resp = requests.post('https://api.tavily.com/search', json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                return [{"title": r.get("title", ""), "snippet": r.get("content", ""), "link": r.get("url", "")} for r in results]
            elif resp.status_code == 429:
                time.sleep(1.0)
                continue
        except Exception:
            time.sleep(0.5)
            continue
    return []

def search_bing_fallback(query_str, max_results=7):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        }
        url = f"https://www.bing.com/search?q={requests.utils.quote(query_str)}"
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, 'html.parser')
            items = []
            for b in soup.find_all('li', class_='b_algo')[:max_results]:
                t_tag = b.find('h2')
                a_tag = t_tag.find('a') if t_tag else None
                s_tag = b.find('div', class_='b_caption')
                if t_tag and a_tag:
                    title = t_tag.get_text().strip()
                    link = a_tag.get('href', '').strip()
                    snippet = s_tag.get_text().strip() if s_tag else ""
                    items.append({"title": title, "snippet": snippet, "link": link})
            return items
    except Exception:
        pass
    return []

def discover_profiles(query_str, max_results=7):
    results = search_tavily(query_str, max_results=max_results)
    if not results:
        results = search_bing_fallback(query_str, max_results=max_results)
    return results

def clean_human_name_and_title(raw_title):
    # Example format: "Sultan Ahmed Bin Sulayem - Group Chairman and CEO at DP World | LinkedIn"
    clean = re.sub(r'\(.*?\)', '', raw_title)
    clean = re.sub(r' - LinkedIn.*', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r' \| LinkedIn.*', '', clean, flags=re.IGNORECASE)
    
    parts = clean.split(' - ')
    if len(parts) == 2:
        name_part, role_part = parts[0].strip(), parts[1].strip()
    else:
        parts_pipe = clean.split(' | ')
        if len(parts_pipe) == 2:
            name_part, role_part = parts_pipe[0].strip(), parts_pipe[1].strip()
        else:
            name_part = parts[0].strip()
            role_part = ""

    # Clean non-alpha
    clean_name = re.sub(r'[^a-zA-Z\s.-]', '', name_part).strip()
    name_tokens = clean_name.split()

    # Filter out junk titles, media, geography or organizations mistaken for names
    junk = {
        "linkedin", "profile", "jobs", "hiring", "company", "executive", "director",
        "group", "holdings", "properties", "breaking", "news", "weather", "updates",
        "report", "media", "times", "post", "gazette", "alabama", "jazeera", "reuters",
        "bloomberg", "forbes", "chief", "officer", "vice", "president", "head", "lead"
    }
    filtered_tokens = [t for t in name_tokens if t.lower() not in junk]

    if len(filtered_tokens) >= 2:
        fn = filtered_tokens[0].capitalize()
        ln = filtered_tokens[-1].capitalize()
        if len(fn) >= 2 and len(ln) >= 2 and fn.isalpha() and ln.isalpha():
            return fn, ln, role_part
            
    return None, None, role_part
            
    return None, None, role_part
