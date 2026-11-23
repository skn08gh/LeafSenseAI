"""
LeafSense AI + PlantPal
Plant identification, plant-care chatbot, environmental plant recommendations,
and analysis history.

Keep this file in the LeafSenseAI project folder beside:
- plant_model.h5
- class_names.json
- chatbot.py
- plant_data.py
- recommendations.py
- history.py
- plant_recommender.py
"""

import html
import json
import os
from typing import Any

import gradio as gr
import numpy as np
import tensorflow as tf

from chatbot import chat
from plant_data import PLANTS
from recommendations import get_recommendations
from history import save_analysis, get_history
from plant_recommender import recommend_plants
from plantcare_reminders import build_reminders_ui, CSS as REMINDER_CSS


# ============================================================
# LOAD THE TRAINED PLANT-IDENTIFICATION MODEL
# ============================================================

MODEL_PATH = "plant_model.h5"
CLASS_NAMES_PATH = "class_names.json"

model = None
class_names = []

if os.path.exists(CLASS_NAMES_PATH):
    try:
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as file:
            class_names = json.load(file)
        print("✅ class_names.json loaded")
    except Exception as exc:
        print(f"❌ Could not read class_names.json: {exc}")
else:
    print("⚠️ class_names.json was not found.")

if os.path.exists(MODEL_PATH):
    try:
        with tf.keras.utils.custom_object_scope({"TrueDivide": tf.math.divide}):
            model = tf.keras.models.load_model(MODEL_PATH)
        print("✅ plant_model.h5 loaded")
    except Exception as exc:
        print(f"❌ MODEL ERROR: {exc}")
else:
    print("⚠️ plant_model.h5 was not found.")


# ============================================================
# PLANT NAME ALIASES
# ============================================================

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
    "hemerocallis": "hemerocallis",
    "daylily": "hemerocallis",
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


def normalize_plant_name(value: Any) -> str:
    """Normalize a model label for matching with the plant profiles."""
    return str(value).lower().replace("_", " ").replace("-", " ").strip()


def model_to_plant(label: str):
    """Convert a model label into a key from plant_data.PLANTS."""
    normalized = normalize_plant_name(label)

    if normalized in ALIASES:
        return ALIASES[normalized]

    for alias, plant_key in ALIASES.items():
        if alias in normalized:
            return plant_key

    # Allow exact matches against the project's plant-profile keys.
    if normalized in PLANTS:
        return normalized

    return None


# ============================================================
# PLANT IMAGE ANALYSIS
# ============================================================

def predict_plant(image):
    """Identify the plant, return a care summary, and update selected-plant state."""
    if image is None:
        return "⚠️ Please upload a plant image first.", None

    if model is None:
        return (
            "❌ The identification model could not be loaded. "
            "Check that `plant_model.h5` and `class_names.json` are in "
            "the LeafSenseAI project folder.",
            None,
        )

    try:
        image = image.convert("RGB").resize((224, 224))
        image_array = np.asarray(image, dtype=np.float32) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        predictions = model.predict(image_array, verbose=0)
        prediction_values = predictions[0]
        index = int(np.argmax(prediction_values))
        confidence = float(np.max(prediction_values)) * 100.0

        if index < len(class_names):
            label = str(class_names[index])
        else:
            label = f"Class {index}"

        save_analysis(label, f"{confidence:.2f}%")

        plant_key = model_to_plant(label)
        care_recommendation = get_recommendation(label)

        report = f"""
## 🌿 Plant Analysis

### **{html.escape(label)}**

**Identification confidence:** {confidence:.2f}%

---

### 🪴 Initial Care

{care_recommendation}
"""

        if plant_key and plant_key in PLANTS:
            display_name = PLANTS[plant_key].get("display", plant_key)
            report += f"""

---

### 💬 PlantPal

PlantPal matched this result to **{html.escape(str(display_name))}**.
Open the **PlantPal** tab to continue with personalized plant-care questions.
"""
        else:
            report += """

---

### 💬 PlantPal

This prediction could not be matched automatically to a plant profile.
Choose your plant manually in the **PlantPal** tab.
"""

        return report, plant_key

    except Exception as exc:
        return f"❌ Image analysis error: `{exc}`", None


# ============================================================
# PLANTPAL CHATBOT
# ============================================================

PLANT_CHOICES = [
    (data.get("display", key), key)
    for key, data in PLANTS.items()
]


def send_message(message, history, selected_plant):
    """Handle a normal chat message using Gradio's messages history format."""
    history = list(history or [])

    if not message or not str(message).strip():
        return history, selected_plant, ""

    try:
        result = chat(str(message).strip(), selected_plant)
        reply = result.get("reply", "Sorry, I couldn't prepare a reply.")
        updated_plant = result.get("plant") or selected_plant
    except Exception as exc:
        reply = f"Sorry, PlantPal encountered an error: {exc}"
        updated_plant = selected_plant

    history.append({"role": "user", "content": str(message).strip()})
    history.append({"role": "assistant", "content": str(reply)})

    return history, updated_plant, ""


def quick_question(question, history, selected_plant):
    """Send a preset question through the same chatbot function."""
    return send_message(question, history, selected_plant)


# ============================================================
# ENVIRONMENTAL PLANT RECOMMENDATIONS
# ============================================================

def _safe_text(value):
    """Escape dynamic text before inserting it into an HTML card."""
    return html.escape(str(value))


def recommend_plants_ui(temperature, light, humidity, soil_moisture):
    """
    Call the project's recommender and render ranked results as cards.
    Expected recommender output: a list of dictionaries containing plant,
    percentage, score, match flags, and explanation.
    """
    if temperature is None or humidity is None:
        return """
        <div class="recommendation-empty">
            ⚠️ Please enter both temperature and humidity.
        </div>
        """

    try:
        results = recommend_plants(
            float(temperature),
            str(light).strip().lower(),
            float(humidity),
            str(soil_moisture).strip().lower(),
        )
    except Exception as exc:
        return f"""
        <div class="recommendation-empty">
            ❌ Could not generate recommendations: {_safe_text(exc)}
            <br><br>
            Check that <code>plant_recommender.py</code> defines
            <code>recommend_plants(temperature, user_light, humidity, soil_moisture)</code>.
        </div>
        """

    if not results:
        return """
        <div class="recommendation-empty">
            No matching plants were returned. Try adjusting the environmental conditions.
        </div>
        """

    cards = []
    for rank, item in enumerate(results, start=1):
        if not isinstance(item, dict):
            continue

        plant_name = _safe_text(item.get("plant", "Unknown plant"))
        percentage = item.get("percentage", item.get("compatibility", 0))
        try:
            percentage = float(percentage)
        except (TypeError, ValueError):
            percentage = 0.0
        percentage = max(0.0, min(100.0, percentage))

        explanation = _safe_text(
            item.get("explanation", "Recommended based on the selected conditions.")
        )

        def match_status(key):
            if item.get(key) is True:
                return '<span class="match-good">✓ Ideal</span>'
            if item.get(key) is False:
                return '<span class="match-close">• Needs attention</span>'
            return '<span class="match-unknown">— Not available</span>'

        temperature_status = match_status("temperature_match")
        light_status = match_status("light_match")
        humidity_status = match_status("humidity_match")
        soil_status = match_status("soil_moisture_match")

        cards.append(f"""
        <section class="plant-card">
            <div class="plant-card-heading">
                <h3>#{rank} 🌱 {plant_name}</h3>
                <div class="compatibility">{percentage:.1f}% compatibility</div>
            </div>
            <div class="compatibility-track">
                <div class="compatibility-fill" style="width:{percentage:.1f}%"></div>
            </div>
            <div class="condition-grid">
                <div class="condition-pill"><strong>🌡 Temperature</strong>{temperature_status}</div>
                <div class="condition-pill"><strong>☀️ Light</strong>{light_status}</div>
                <div class="condition-pill"><strong>💧 Humidity</strong>{humidity_status}</div>
                <div class="condition-pill"><strong>🪴 Soil moisture</strong>{soil_status}</div>
            </div>
            <div class="why-card">
                <strong>💡 Why this plant?</strong>
                <p>{explanation}</p>
            </div>
        </section>
        """)

    if not cards:
        return """
        <div class="recommendation-empty">
            The recommender returned results in an unexpected format.
        </div>
        """

    return f"""
    <style>
      .recommendations-wrap {{
        color: var(--body-text-color, #1f2937);
        font-family: inherit;
      }}
      .recommendations-intro {{
        margin: 0 0 16px 0;
        line-height: 1.6;
      }}
      .plant-card {{
        border: 1px solid var(--border-color-primary, #d9deea);
        border-radius: 14px;
        padding: 20px;
        margin: 16px 0;
        background: var(--background-fill-primary, #ffffff);
        box-shadow: 0 2px 8px rgba(25, 35, 60, 0.05);
      }}
      .plant-card-heading {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 12px;
        flex-wrap: wrap;
      }}
      .plant-card h3 {{
        margin: 0;
        font-size: 1.25rem;
      }}
      .compatibility {{
        font-weight: 700;
        white-space: nowrap;
      }}
      .compatibility-track {{
        height: 9px;
        border-radius: 999px;
        background: #e7eaf1;
        overflow: hidden;
        margin: 14px 0 18px;
      }}
      .compatibility-fill {{
        height: 100%;
        border-radius: 999px;
        background: #6c63f5;
      }}
      .condition-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
        gap: 10px;
      }}
      .condition-pill {{
        border: 1px solid var(--border-color-primary, #e1e5ed);
        border-radius: 9px;
        padding: 11px 12px;
        display: flex;
        flex-direction: column;
        gap: 7px;
      }}
      .match-good {{ color: #16834a; font-weight: 650; }}
      .match-close {{ color: #a46b09; font-weight: 650; }}
      .match-unknown {{ color: #6b7280; }}
      .why-card {{
        margin-top: 16px;
        padding: 13px 15px;
        border-radius: 9px;
        background: var(--background-fill-secondary, #f2f4ff);
        line-height: 1.6;
      }}
      .why-card p {{ margin: 5px 0 0; }}
      .recommendation-empty {{
        padding: 18px;
        border: 1px solid var(--border-color-primary, #d9deea);
        border-radius: 10px;
      }}
    </style>
    <div class="recommendations-wrap">
      <h2>🌱 Your Top Recommendations</h2>
      <p class="recommendations-intro">
        Based on your environmental conditions, LeafSense AI found these plants.
      </p>
      {''.join(cards)}
    </div>
    """


# ============================================================
# BUILD THE GRADIO INTERFACE
# IMPORTANT: ALL COMPONENTS AND .click() EVENTS MUST BE INSIDE
# THIS gr.Blocks CONTEXT.
# ============================================================

with gr.Blocks(title="LeafSense AI + PlantPal", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        """
# 🌿 LeafSense AI + PlantPal
### Plant identification • Health analysis • Personalized plant care
"""
    )

    selected_plant = gr.State(None)

    # --------------------------------------------------------
    # TAB 1: PLANT HEALTH ANALYZER
    # --------------------------------------------------------
    with gr.Tab("🔍 Plant Health Analyzer"):
        gr.Markdown(
            "Upload a plant photograph to identify it and view its initial care guidance."
        )

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(
                    type="pil",
                    label="📷 Upload Plant Image",
                )
                analyze_button = gr.Button(
                    "🌿 Analyze Plant",
                    variant="primary",
                )

            with gr.Column():
                diagnosis_output = gr.Markdown(
                    "Your plant analysis will appear here."
                )

        analyze_button.click(
            fn=predict_plant,
            inputs=image_input,
            outputs=[diagnosis_output, selected_plant],
        )

    # --------------------------------------------------------
    # TAB 2: ENVIRONMENTAL PLANT RECOMMENDER
    # --------------------------------------------------------
    with gr.Tab("🪴 Plant Recommendations"):
        gr.Markdown(
            """
## 🌱 Plant Recommendation AI
Find plants that best match the environmental conditions in your space.
Enter the conditions below and click **Find My Best Plants**.
"""
        )

        with gr.Row():
            with gr.Column():
                temperature_input = gr.Number(
                    value=25,
                    label="🌡 Temperature (°C)",
                    minimum=-10,
                    maximum=60,
                    step=1,
                )
                humidity_input = gr.Number(
                    value=60,
                    label="💧 Humidity (%)",
                    minimum=0,
                    maximum=100,
                    step=1,
                )

            with gr.Column():
                light_input = gr.Dropdown(
                    choices=["low", "medium", "bright"],
                    value="medium",
                    label="☀️ Light Level",
                    info="Choose the light available where the plant will grow.",
                )
                soil_moisture_input = gr.Dropdown(
                    choices=["dry", "moderate", "moist"],
                    value="moderate",
                    label="🪴 Soil Moisture",
                    info="Choose the current moisture level of your soil."
                )
        
        with gr.Accordion("💡 Not sure what to choose? See the guide", open=False):
            gr.Markdown("""
    ## ☀️ Light Guide

    **🌑 Low light**  
    A darker indoor area with little direct sunlight.

    **🌤️ Medium light**  
    A reasonably bright area with indirect or filtered sunlight.

    **☀️ Bright light**  
    A very bright location receiving plenty of light, sometimes including direct sunlight.

    ---

    ## 🌱 Soil Moisture Guide

    **🏜️ Dry**  
    The soil feels dry to the touch.

    **💧 Moderate**  
    The soil feels slightly damp, but not wet or soggy.

    **💦 Moist**  
    The soil feels noticeably damp, but the plant is not sitting in water.
    """)

        recommend_button = gr.Button(
            "🌿 Find My Best Plants",
            variant="primary",
        )

        recommendation_output = gr.HTML(
            """
            <div class="recommendation-empty">
              🌱 Your recommendations will appear here.
              <br><br>
              Enter your environmental conditions and click
              <strong>Find My Best Plants</strong>.
            </div>
            """
        )

        recommend_button.click(
            fn=recommend_plants_ui,
            inputs=[
                temperature_input,
                light_input,
                humidity_input,
                soil_moisture_input,
            ],
            outputs=recommendation_output,
        )

        with gr.Accordion("ℹ️ How the recommendation system works", open=False):
            gr.Markdown(
                """
The recommender compares your selected temperature, light, humidity,
and soil-moisture conditions with the preferred conditions of supported
plant species. It ranks the plants by compatibility and explains the
match for each environmental factor.

The percentages are compatibility scores from this project's rule-based
recommender, not a guarantee that a plant will thrive in every location.
"""
            )

    # --------------------------------------------------------
    # TAB 3: PLANTPAL CHATBOT
    # --------------------------------------------------------
    with gr.Tab("💬 PlantPal"):
        gr.Markdown(
            """
## 🌱 PlantPal
Choose a plant and ask about watering, light, yellow leaves, pests,
growth, soil, repotting, or personalized care.
"""
        )

        plant_dropdown = gr.Dropdown(
            choices=PLANT_CHOICES,
            label="🌿 Choose your plant",
            value=None,
        )

        plant_dropdown.change(
            fn=lambda value: value,
            inputs=plant_dropdown,
            outputs=selected_plant,
        )

        chatbot = gr.Chatbot(
    height=420,
    label="PlantPal",
)

        with gr.Row():
            routine_button = gr.Button("🪴 Care Routine")
            watering_button = gr.Button("💧 Watering")
            light_button = gr.Button("☀️ Light")
            leaves_button = gr.Button("🍂 Yellow Leaves")

        with gr.Row():
            pest_button = gr.Button("🐛 Pests")
            growth_button = gr.Button("📈 Growth")
            repot_button = gr.Button("🪴 Repotting")
            droop_button = gr.Button("🥀 Drooping")

        message_box = gr.Textbox(
            label="Message PlantPal",
            placeholder="e.g. My Monstera has yellow leaves...",
            lines=2,
        )
        send_button = gr.Button("Send 🌱", variant="primary")

        chat_inputs = [message_box, chatbot, selected_plant]
        chat_outputs = [chatbot, selected_plant, message_box]

        send_button.click(
            fn=send_message,
            inputs=chat_inputs,
            outputs=chat_outputs,
        )
        message_box.submit(
            fn=send_message,
            inputs=chat_inputs,
            outputs=chat_outputs,
        )

        # Each quick button uses the same chatbot handler.
        routine_button.click(
            fn=lambda history, plant: quick_question(
                "Make me a personalized care routine.", history, plant
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        watering_button.click(
            fn=lambda history, plant: quick_question(
                "How should I water this plant?", history, plant
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        light_button.click(
            fn=lambda history, plant: quick_question(
                "How much light does this plant need?", history, plant
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        leaves_button.click(
            fn=lambda history, plant: quick_question(
                "My plant has yellow leaves. What should I check?",
                history,
                plant,
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        pest_button.click(
            fn=lambda history, plant: quick_question(
                "I think my plant has pests. What should I check?",
                history,
                plant,
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        growth_button.click(
            fn=lambda history, plant: quick_question(
                "My plant is not growing well. What should I check?",
                history,
                plant,
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        repot_button.click(
            fn=lambda history, plant: quick_question(
                "Should I repot this plant?", history, plant
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )
        droop_button.click(
            fn=lambda history, plant: quick_question(
                "My plant is drooping. What should I check first?",
                history,
                plant,
            ),
            inputs=[chatbot, selected_plant],
            outputs=chat_outputs,
        )

    # --------------------------------------------------------
    # TAB 4: PLANT CARE REMINDERS
    # --------------------------------------------------------
    with gr.Tab("⏰ Plant Care Reminders"):
        build_reminders_ui(demo)

    # --------------------------------------------------------
    # TAB 5: ANALYSIS HISTORY
    # --------------------------------------------------------
    with gr.Tab("📜 History"):
        gr.Markdown("## Previous plant analyses")
        refresh_history_button = gr.Button("🔄 Refresh History")
        history_output = gr.JSON(
            label="Analysis History",
            value=get_history(),
        )
        refresh_history_button.click(
            fn=get_history,
            inputs=[],
            outputs=history_output,
        )

    # --------------------------------------------------------
    # PROJECT INFORMATION
    # --------------------------------------------------------
    gr.Markdown("---")

    with gr.Row():
        with gr.Column():
            gr.Markdown(
                """
### 🔍 What LeafSense AI Does

**1. Plant Identification**  
Uses a trained deep-learning model to identify the uploaded plant.

**2. Initial Care Guidance**  
Displays care information associated with the predicted plant.
"""
            )

        with gr.Column():
            gr.Markdown(
                """
### 🌍 Project Goal

LeafSense AI helps people make informed decisions about indoor-plant
care using artificial intelligence and environmental compatibility.

**Project alignment:** 🌱 UN Sustainable Development Goal 15 — Life on Land.
"""
            )

    gr.Markdown(
        """
---
<div style="text-align:center">
🌿 LeafSense AI • AI-Based Houseplant Health Analyzer
</div>
"""
    )


# ============================================================
# LAUNCH
# ============================================================

if __name__ == "__main__":
    print("\n🌿 LeafSense AI + PlantPal starting...\n")
    demo.launch(inbrowser=True, css=REMINDER_CSS)
