"""
=============================================================================
INDULGE GLOBAL - PORT 25 LIVE SMTP HANDSHAKE VERIFIER
=============================================================================
Tests MX mail deliverability on Port 25 for generated corporate permutations.
Handles Microsoft 365, Google Workspace, Proofpoint, Mimecast, etc.
=============================================================================
"""

import socket
import dns.resolver

_mx_cache = {}

def get_mx_record(domain):
    domain = domain.strip().lower()
    if domain in _mx_cache:
        return _mx_cache[domain]
    
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        sorted_answers = sorted(answers, key=lambda r: r.preference)
        mx_host = str(sorted_answers[0].exchange).rstrip('.')
        _mx_cache[domain] = mx_host
        return mx_host
    except Exception:
        _mx_cache[domain] = None
        return None

def verify_email_smtp(email, mx_host, timeout=3.5):
    if not mx_host or not email:
        return False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((mx_host, 25))
        s.recv(1024)
        
        s.sendall(b"HELO verify-agent.com\r\n")
        s.recv(1024)
        
        s.sendall(b"MAIL FROM:<check@verify-agent.com>\r\n")
        s.recv(1024)
        
        s.sendall(f"RCPT TO:<{email}>\r\n".encode())
        resp = s.recv(1024).decode('utf-8', errors='ignore')
        
        s.sendall(b"QUIT\r\n")
        s.close()
        
        # 250 OK or 251 user not local but forwarded
        if "250" in resp or "251" in resp:
            return True
        return False
    except Exception:
        return False

def generate_email_permutations(first_name, last_name, domain):
    f = first_name.strip().lower()
    l = last_name.strip().lower()
    d = domain.strip().lower()
    
    # Strip any special non-alpha chars
    f = "".join(c for c in f if c.isalnum())
    l = "".join(c for c in l if c.isalnum())
    
    if not f or not l:
        return []
    
    return [
        f"{f}.{l}@{d}",
        f"{f}@{d}",
        f"{f}{l}@{d}",
        f"{f[0]}{l}@{d}",
        f"{f}.{l[0]}@{d}",
        f"{l}.{f}@{d}",
        f"{f}_{l}@{d}"
    ]
