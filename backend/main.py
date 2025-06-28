#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api:app", host="0.0.0.0", port=8000, reload=True)
