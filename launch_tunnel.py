r"""
Indulge Global — Cloudflare Public Tunnel Launcher
===================================================
Establishes an instant, free, SSL-encrypted public URL via Cloudflare
forwarding directly to http://localhost:5000 with the full functional Python backend.
Zero registration, zero tokens required.
"""
import sys
import time
from pycloudflared import try_cloudflare

if __name__ == "__main__":
    print("=" * 65)
    print("  LAUNCHING CLOUDFLARE PUBLIC TUNNEL FOR CLIENT ACCESS")
    print("  Forwarding to: http://localhost:5000")
    print("=" * 65)
    sys.stdout.flush()

    try:
        # try_cloudflare starts cloudflared in the background and returns public URL
        tunnel_url = try_cloudflare(port=5000)
        print("\n" + "*" * 65)
        print(f"  >>> CLIENT PUBLIC URL: {tunnel_url.tunnel}")
        print("*" * 65 + "\n")
        sys.stdout.flush()

        with open("PUBLIC_URL.txt", "w", encoding="utf-8") as f:
            f.write(tunnel_url.tunnel)

        # Keep alive
        while True:
            time.sleep(10)
    except Exception as e:
        print(f"[!] Tunnel error: {e}")
        sys.stdout.flush()
