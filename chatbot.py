
"""
PlantPal chatbot powered by the Lyzr Agent API.
Compatible with the existing LeafSense Gradio application.
"""

import os
import re
import uuid

import requests
from dotenv import load_dotenv
from plant_data import PLANTS

# Load credentials from the project's .env file
load_dotenv()

LYZR_API_URL = os.getenv(
    "LYZR_API_URL",
    "https://agent-prod.studio.lyzr.ai/v3/inference/chat/"
)
LYZR_API_KEY = os.getenv("LYZR_API_KEY", "").strip()
LYZR_AGENT_ID = os.getenv("LYZR_AGENT_ID", "").strip()

LYZR_USER_ID = os.getenv("LYZR_USER_ID", "leafsense_user")
LYZR_SESSION_ID = os.getenv(
    "LYZR_SESSION_ID", f"leafsense-{uuid.uuid4().hex}"
)

TIMEOUT = 45


# Supported plant aliases from the LeafSense database
ALIASES = {
    "aloe": "aloe vera",
    "aloe vera": "aloe vera",
    "anthurium": "anthurium",
    "asparagus fern": "asparagus fern",
    "bird of paradise": "bird of paradise",
    "birds nest fern": "birds nest fern",
    "bird's nest fern": "birds nest fern",
    "boston fern": "boston fern",
    "cast iron plant": "cast iron plant",
    "chinese money plant": "chinese money plant",
    "pilea": "chinese money plant",
    "chinese evergreen": "chinese evergreen",
    "aglaonema": "chinese evergreen",
    "jade plant": "jade plant",
    "jade": "jade plant",
    "kalanchoe": "kalanchoe",
    "daylily": "hemerocallis",
    "hemerocallis": "hemerocallis",
    "monstera": "monstera deliciosa",
    "monstera deliciosa": "monstera deliciosa",
    "orchid": "orchid",
    "parlor palm": "parlor palm",
    "peace lily": "peace lily",
    "pothos": "pothos",
    "money plant": "pothos",
    "rattlesnake plant": "rattlesnake plant",
    "calathea": "rattlesnake plant",
    "rubber plant": "rubber plant",
    "ficus elastica": "rubber plant",
    "sago palm": "sago palm",
    "snake plant": "snake plant",
    "sansevieria": "snake plant",
    "venus flytrap": "venus flytrap",
    "zz plant": "zz plant",
    "zamioculcas": "zz plant",
    "tulip": "tulip",
}


def detect_plant(text):
    """Detect a supported plant name in the user's message."""
    text = str(text or "").lower()

    for alias, plant in sorted(
        ALIASES.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        pattern = r"(?<!\w)" + re.escape(alias) + r"(?!\w)"
        if re.search(pattern, text) and plant in PLANTS:
            return plant

    return None


def get_plant_context(plant_name):
    """Get plant information from the existing local database."""
    if not plant_name or plant_name not in PLANTS:
        return (
            "No specific plant has been selected. Answer general "
            "plant-care questions and ask which plant if necessary."
        )

    plant = PLANTS[plant_name]
    display = plant.get("display", plant_name)

    details = [f"Selected plant: {display}"]

    for key, label in [
        ("light", "Light"),
        ("water", "Watering"),
        ("humidity", "Humidity"),
        ("soil", "Soil"),
        ("notes", "Care notes"),
    ]:
        if plant.get(key):
            details.append(f"{label}: {plant[key]}")

    return "\n".join(details)


def extract_reply(data):
    """Extract an answer from common JSON response structures."""
    if isinstance(data, str):
        return data.strip() or None

    if isinstance(data, list):
        for item in reversed(data):
            answer = extract_reply(item)
            if answer:
                return answer
        return None

    if isinstance(data, dict):
        for key in (
            "response", "message", "answer", "output",
            "result", "text", "content", "reply"
        ):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

        for key in (
            "data", "response_data", "agent_response", "choices"
        ):
            if key in data:
                answer = extract_reply(data[key])
                if answer:
                    return answer

        # Support OpenAI-style response wrappers too.
        choices = data.get("choices")
        if isinstance(choices, list):
            for choice in reversed(choices):
                if isinstance(choice, dict):
                    answer = extract_reply(
                        choice.get("message", {}).get("content")
                        if isinstance(choice.get("message"), dict)
                        else choice.get("text")
                    )
                    if answer:
                        return answer

    return None


def call_lyzr(message, plant_name, user_id=None, session_id=None):
    """Send the user's question to the Lyzr agent."""
    if not LYZR_API_KEY:
        raise RuntimeError(
            "LYZR_API_KEY is missing from your .env file."
        )

    if not LYZR_AGENT_ID:
        raise RuntimeError(
            "LYZR_AGENT_ID is missing from your .env file."
        )

    prompt = f"""
You are PlantPal, the plant-care assistant inside LeafSense.

Answer the user's actual question naturally. You can answer
open-ended questions about plant care; do not restrict yourself
to a fixed list of questions.

Give practical, clear advice. Explain possible causes when
diagnosing plant problems, and do not claim certainty when
there may be several explanations. Ask follow-up questions
when important details are missing.

Plant information from the LeafSense database:
{get_plant_context(plant_name)}

User's question:
{message}
"""

    payload = {
        "user_id": str(user_id or LYZR_USER_ID),
        "agent_id": LYZR_AGENT_ID,
        "session_id": str(session_id or LYZR_SESSION_ID),
        "message": prompt,
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LYZR_API_KEY,
    }

    try:
        response = requests.post(
            LYZR_API_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
    except requests.Timeout as exc:
        raise RuntimeError(
            "Lyzr timed out. Please try again."
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not connect to Lyzr. Check your internet connection."
        ) from exc

    if response.status_code in (401, 403):
        raise RuntimeError(
            "Lyzr rejected the API key. Check your credentials."
        )

    if response.status_code == 404:
        raise RuntimeError(
            "Lyzr returned 404. Check your agent ID and API endpoint."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "Lyzr rate limit or quota reached. Try again later."
        )

    if not response.ok:
        raise RuntimeError(
            f"Lyzr API returned HTTP {response.status_code}: "
            f"{response.text[:300]}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "Lyzr returned an invalid JSON response."
        ) from exc

    answer = extract_reply(data)

    if not answer:
        raise RuntimeError(
            "Lyzr responded, but the answer field was not recognized. "
            "The API response format may need adjustment."
        )

    return answer


def chat(message, selected_plant=None, user_id=None, session_id=None):
    """
    Main entry point used by the existing Gradio app.

    Returns the same dictionary structure as the previous chatbot:
    {"reply": "...", "plant": "..."}
    """
    message = str(message or "").strip()

    plant_name = (
        selected_plant
        if selected_plant in PLANTS
        else detect_plant(message)
    )

    if not message:
        return {
            "reply": "🌱 Type a plant-care question to get started!",
            "plant": plant_name,
        }

    try:
        reply = call_lyzr(
            message,
            plant_name,
            user_id=user_id,
            session_id=session_id,
        )
    except RuntimeError as exc:
        reply = (
            "🌱 PlantPal couldn't complete your request.\n\n"
            f"{exc}"
        )
    except Exception:
        reply = (
            "🌱 An unexpected error occurred while contacting "
            "PlantPal. Check the VS Code terminal for details."
        )

    return {
        "reply": reply,
        "plant": plant_name,
    }

