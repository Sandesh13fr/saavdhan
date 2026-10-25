"""Unit tests never use live model or telemetry credentials."""
import os

os.environ["BAKAYA_ENABLE_LLM"]="false"
for name in ("NEATLOGS_API_KEY","NEATLOGS_PROJECT_TOKEN"):
    # Empty values also prevent dotenv from reloading local live credentials.
    os.environ[name]=""
