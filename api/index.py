"""
Vercel Python serverless entrypoint for the WestAI HPC Assistant.

Vercel detects the ASGI `app` exported here and runs the whole FastAPI backend
as a serverless function — no long-running server needed. All requests are
routed here by vercel.json; FastAPI dispatches /api/* and serves the frontend.
"""

import os
import sys

# Make the backend package importable from the function's working dir.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app  # noqa: E402  (ASGI app Vercel will serve)
