import logging
import os

import vertexai

from dotenv import load_dotenv
from langchain_google_vertexai import ChatVertexAI

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

# --------------------------------------------------
# Logger
# --------------------------------------------------

logger = logging.getLogger(__name__)

# --------------------------------------------------
# Google Cloud Configuration
# --------------------------------------------------

PROJECT_ID = os.getenv(
    "PROJECT_ID",
    "ai-service-502218"
)

LOCATION = os.getenv(
    "LOCATION",
    "asia-southeast1"
)

MODEL_NAME = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

# --------------------------------------------------
# Initialize Vertex AI
# --------------------------------------------------

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION
)

# --------------------------------------------------
# Chat Model Factory
# --------------------------------------------------

def get_chat_model(**overrides):

    config = {
        "model": MODEL_NAME,
        "temperature": 0.0
    }

    config.update(overrides)

    return ChatVertexAI(**config)

# --------------------------------------------------
# Generate Response
# --------------------------------------------------

def generate(prompt: str) -> str:

    try:

        llm = get_chat_model()

        response = llm.invoke(prompt)

        return response.content

    except Exception as ex:

        logger.exception(
            "Gemini generation failed"
        )

        raise Exception(
            f"Gemini Error: {str(ex)}"
        )