from langchain_google_vertexai import ChatVertexAI
import logging
import os

from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# Logger
# --------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------
# GCP Configuration
# --------------------------------------------------

GCP_PROJECT_ID = os.getenv(
    "GCP_PROJECT_ID",
    "announcement-ai-project"
)

GOOGLE_LOCATION = os.getenv(
    "GOOGLE_LOCATION",
    "us-central1"
)

# --------------------------------------------------
# Chat Model Factory
# --------------------------------------------------

def get_chat_model(**overrides):

    config = {
        "model": "gemini-2.5-flash",
        "temperature": 0.0,
        "project": GCP_PROJECT_ID,
        "location": GOOGLE_LOCATION
    }

    config.update(overrides)

    return ChatVertexAI(**config)

# --------------------------------------------------
# Generate Response
# --------------------------------------------------

def generate(prompt: str) -> str:

    try:

        llm = get_chat_model()

        response = llm.invoke(
            prompt
        )

        return response.content

    except Exception as ex:

        logger.exception(
            "Gemini generation failed"
        )

        raise Exception(
            f"Gemini Error: {str(ex)}"
        )