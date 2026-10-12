r"""
Indulge Global — Production Server Launcher
============================================
Runs the Indulge Flask application via the Waitress WSGI server
to ensure rock-solid stability and prevent terminal closure on Windows.
"""
import sys
from waitress import serve
from app import app

if __name__ == "__main__":
    print("=" * 60)
    print("  INDULGE GLOBAL - PRODUCTION WSGI SERVER (Waitress)")
    print("  Serving at: http://localhost:5000")
    print("=" * 60)
    sys.stdout.flush()
    serve(app, host="0.0.0.0", port=5000, threads=6)
