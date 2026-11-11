"""
=============================================================================
         STUDENT SQL DATABASE - WEB DASHBOARD (Local Entry Point)
=============================================================================
This file runs the application locally on your computer.
For Vercel serverless deployment, Vercel uses `api/index.py`.
=============================================================================
"""

import webbrowser
import threading
from api.index import app

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print(" [START] STUDENT DATABASE WEB APPLICATION")
    print("=" * 65)
    print(" Access the website at: http://127.0.0.1:5000")
    print(" Opening browser automatically in 1 second...")
    print(" Press Ctrl + C in terminal to stop the server.")
    print("=" * 65 + "\n")

    threading.Timer(1.2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
