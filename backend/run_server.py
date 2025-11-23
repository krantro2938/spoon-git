# run_server.py
import os

import uvicorn

if __name__ == "__main__":
    # Ensure environment variables are loaded if needed, e.g., from a .env file
    # for local development (install python-dotenv for this)
    # from dotenv import load_dotenv
    # load_dotenv()

    # The port and host can be configured
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
