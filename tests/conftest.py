"""Unit tests never use live model or telemetry credentials."""
import os

os.environ["BAKAYA_ENABLE_LLM"]="false"
for name in ("OPENAI_API_KEY","LITELLM_API_KEY"):
    # Empty values also prevent dotenv from reloading local live credentials.
    os.environ[name]=""
