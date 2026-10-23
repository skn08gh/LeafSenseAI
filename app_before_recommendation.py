import gradio as gr

from history import save_analysis
from chatbot import chat
from models import identify_plant
from health_analyzer import analyze_health
from recommendations import get_recommendations

print("🌱 PlantPal chatbot loaded successfully!")


# =========================================================
# MAIN AI ANALYSIS FUNCTION
# =========================================================

def analyze_plant(image):

    if image is None:
        return "⚠️ Please upload a plant image first."

    print("Image received!")

    # -----------------------------------------------------
    # 1. PLANT IDENTIFICATION
    # -----------------------------------------------------

    results = identify_plant(image)

    print("Plant results:", results)

    top_prediction = results[0]

    plant_name = top_prediction["label"]

    confidence = round(
        top_prediction["score"] * 100, 2)

    # -----------------------------------------------------
    # 1A. CHECK IDENTIFICATION CONFIDENCE
    # -----------------------------------------------------

    if confidence < 80:
        return f"""
    # 🌿 LeafSense AI

    ## ⚠️ Identification Uncertain

    LeafSense AI could not identify the plant with enough confidence.

    **Most likely identification:**  
    ### {plant_name}

    **Identification Confidence:**     
    ### {confidence}%

    Please upload a clearer photograph showing the leaves and
    overall structure of the plant.

    > Health analysis and personalized recommendations were
    > not performed because the plant identification confidence
    > is too low.
    """


    # -----------------------------------------------------
    # 2. HEALTH ANALYSIS
    # -----------------------------------------------------

    health_result = analyze_health(image, plant_name)

    print("Health result:", health_result)

    health = health_result["health"]
    severity = health_result["severity"]
    explanation = health_result["explanation"]
    green_ratio = health_result["green_ratio"]
    yellow_ratio = health_result["yellow_ratio"]
    brown_ratio = health_result["brown_ratio"]
    stress_score = health_result["stress_score"]

    # -----------------------------------------------------
    # 3. PERSONALIZED RECOMMENDATIONS
    # -----------------------------------------------------

    recommendations = get_recommendations(
        plant_name,
        severity
    )

    watering = recommendations["watering"]
    light = recommendations["light"]
    care = recommendations["care"]
    urgency = recommendations["urgency"]

    print("Recommendations generated!")

    # -----------------------------------------------------
    # 4. SAVE ANALYSIS TO HISTORY
    # -----------------------------------------------------

    save_analysis(
        plant_name=plant_name,
        confidence=confidence,
        health=health,
        severity=severity,
        explanation=explanation,
        watering=watering,
        light=light
    )

    # -----------------------------------------------------
    # 5. CREATE PROFESSIONAL REPORT
    # -----------------------------------------------------

    report = f"""
# 🌿 LeafSense AI
### AI-Powered Houseplant Health Analysis

---

## 🌱 Plant Identification

**Detected Plant:**  
### {plant_name}

**Identification Confidence:**  
### {confidence}%

---

## 🩺 Health Assessment

**Overall Health:**  
### {health}

**Severity Level:**  
### {severity}

**AI Explanation:**  
{explanation}

---

## 💡 Personalized Care Plan

### 💧 Watering
{watering}

### ☀️ Light Requirements
{light}

### 🌿 General Care
{care}

### ⚠️ What To Do Now
{urgency}

---

## 📊 Visual Analysis

| Feature | Result |
|---|---|
| 🟢 Green Coverage | {green_ratio}% |
| 🟡 Yellow Areas | {yellow_ratio}% |
| 🟤 Brown Areas | {brown_ratio}% |
| 📈 Visual Stress Score | {stress_score} |

---

## 📋 Analysis Summary

| Feature | Result |
|---|---|
| Plant | {plant_name} |
| Identification Confidence | {confidence}% |
| Health | {health} |
| Severity | {severity} |

---

> **Note:** This analysis is based on visible features in the uploaded image
> and is intended as a general plant-care guide.
"""

    return report

# =========================================================
# PLANTPAL CHAT
# =========================================================

def send_message(message, history, selected_plant):

    if not message or not message.strip():
        return history or [], selected_plant, ""

    result = chat(
        message.strip(),
        selected_plant
    )

    history = history or []

    history.append({
        "role": "user",
        "content": message.strip()
    })

    history.append({
        "role": "assistant",
        "content": result["reply"]
    })

    return (
        history,
        result["plant"] or selected_plant,
        ""
    )

# =========================================================
# CUSTOM CSS
# =========================================================

custom_css = """
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}

#title {
    text-align: center;
}

#subtitle {
    text-align: center;
    font-size: 18px;
}

.upload-box {
    border-radius: 15px;
}

.report-box {
    border-radius: 15px;
}

.footer {
    text-align: center;
    margin-top: 20px;
    opacity: 0.7;
}
"""


# =========================================================
# BUILD INTERFACE
# =========================================================

with gr.Blocks(
    title="LeafSense AI",
    css=custom_css,
    theme=gr.themes.Soft()
) as app:
    selected_plant = gr.State(None)
    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    gr.Markdown(
        """
        # 🌿 LeafSense AI
        """,
        elem_id="title"
    )

    gr.Markdown(
        """
        ### Intelligent Plant Health Analysis for Indoor Houseplants

        Upload a photograph of your plant and let LeafSense AI
        identify the species, assess visible health conditions,
        estimate severity, and generate personalized care advice.
        """,
        elem_id="subtitle"
    )

    gr.Markdown("---")

    # -----------------------------------------------------
    # MAIN AREA
    # -----------------------------------------------------

    with gr.Row():

        # LEFT SIDE — IMAGE

        with gr.Column(scale=1):

            gr.Markdown("## 📷 Upload Your Plant")

            image_input = gr.Image(
                type="pil",
                label="Plant Image",
                elem_classes="upload-box"
            )

            analyze_button = gr.Button(
                "🔍 Analyze Plant",
                variant="primary",
                size="lg"
            )

            clear_button = gr.ClearButton(
                components=[image_input],
                value="🗑️ Clear Image"
            )

        # RIGHT SIDE — REPORT

        with gr.Column(scale=1):

            gr.Markdown("## 📋 AI Analysis Report")

            report_output = gr.Markdown(
                value="""
                ### Your plant analysis will appear here 🌱

                Upload an image and click **Analyze Plant**.
                """,
                elem_classes="report-box"
            )

    # -----------------------------------------------------
    # PLANTPAL CHATBOT
    # -----------------------------------------------------

    with gr.Tab("💬 PlantPal"):

        gr.Markdown(
            """
            ## 🌱 PlantPal

            Your friendly AI plant-care companion.

            Ask about watering, light, yellow leaves,
            pests, growth, soil, repotting, or general care.
            """
        )

        plant_dropdown = gr.Dropdown(
            choices=[
                ("Aloe Vera", "aloe vera"),
                ("Anthurium", "anthurium"),
                ("Asparagus Fern", "asparagus fern"),
                ("Bird of Paradise", "bird of paradise"),
                ("Bird's Nest Fern", "birds nest fern"),
                ("Boston Fern", "boston fern"),
                ("Cast Iron Plant", "cast iron plant"),
                ("Chinese Money Plant", "chinese money plant"),
                ("Chinese Evergreen", "chinese evergreen"),
                ("Jade Plant", "jade plant"),
                ("Kalanchoe", "kalanchoe"),
                ("Hemerocallis", "hemerocallis"),
                ("Monstera Deliciosa", "monstera deliciosa"),
                ("Orchid", "orchid"),
                ("Parlor Palm", "parlor palm"),
                ("Peace Lily", "peace lily"),
                ("Pothos / Money Plant", "pothos"),
                ("Rattlesnake Plant", "rattlesnake plant"),
                ("Rubber Plant", "rubber plant"),
                ("Sago Palm", "sago palm"),
                ("Snake Plant", "snake plant"),
                ("Venus Flytrap", "venus flytrap"),
                ("ZZ Plant", "zz plant"),
                ("Tulip", "tulip")
            ],
            label="🌿 Choose your plant"
        )

        plant_dropdown.change(
            fn=lambda x: x,
            inputs=plant_dropdown,
            outputs=selected_plant
        )

        chatbot = gr.Chatbot(
            height=450,
            label="PlantPal"
        )

        message_box = gr.Textbox(
            label="Message PlantPal",
            placeholder="e.g. My Peace Lily has yellow leaves...",
            lines=2
        )

        send_button = gr.Button(
            "Send 🌱",
            variant="primary"
        )

        send_button.click(
            fn=send_message,
            inputs=[
                message_box,
                chatbot,
                selected_plant
            ],
            outputs=[
                chatbot,
                selected_plant,
                message_box
            ]
        )

        message_box.submit(
            fn=send_message,
            inputs=[
                message_box,
                chatbot,
                selected_plant
            ],
            outputs=[
                chatbot,
                selected_plant,
                message_box
            ]
        )        

    # -----------------------------------------------------
    # BUTTON ACTION
    # -----------------------------------------------------

    analyze_button.click(
        fn=analyze_plant,
        inputs=image_input,
        outputs=report_output
    )

    # -----------------------------------------------------
    # PROJECT INFORMATION
    # -----------------------------------------------------

    gr.Markdown("---")

    with gr.Row():

        with gr.Column():
            gr.Markdown(
                """
                ### 🔍 What LeafSense AI Does

                **1. Plant Identification**  
                Uses a trained deep-learning model to identify
                the uploaded houseplant.

                **2. Health Analysis**  
                Examines visible characteristics of the plant
                to estimate its health condition.

                **3. Severity Estimation**  
                Categorizes the detected condition into
                different severity levels.

                **4. Personalized Recommendations**  
                Generates plant-specific watering, lighting,
                and care recommendations.
                """
            )

        with gr.Column():
            gr.Markdown(
                """
                ### 🌍 Project Goal

                LeafSense AI aims to help people maintain
                healthier indoor plants through accessible
                artificial intelligence.

                **Project Alignment:**  
                🌱 **UN Sustainable Development Goal 15**

                **Life on Land**

                Healthy plants contribute to greener homes,
                schools, communities, and ecosystems.
                """
            )

    gr.Markdown(
        """
        <div class="footer">
        🌿 LeafSense AI • AI-Based Houseplant Health Analyzer
        </div>
        """
    )


# =========================================================
# LAUNCH
# =========================================================

app.launch(inbrowser=True)