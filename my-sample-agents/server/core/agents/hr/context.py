from datetime import datetime
from config.config import LANGUAGE, LANGUAGE_CODE
import uuid

DEFAULT_LANGUAGE = LANGUAGE or "English (United Kingdom)"

class AgentContext:
    INTERVIEW_CONTEXT = {
        #"language":DEFAULT_LANGUAGE,
        "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    AUDITOR_CONTEXT = {
        #"language":DEFAULT_LANGUAGE,
        "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    RAG_CONTEXT = {
        #"language":DEFAULT_LANGUAGE,
        "current_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }