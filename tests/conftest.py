"""Unit tests never use live model or telemetry credentials."""
import os

os.environ["SAAVDHAN_ENABLE_LLM"]="false"
for name in ("OPENAI_API_KEY","LITELLM_API_KEY"):
    # Empty values also prevent dotenv from reloading local live credentials.
    os.environ[name]=""

# Rate limiting is tested explicitly in test_hardening.py.
os.environ["SAAVDHAN_RATE_MAX"]="100000"
