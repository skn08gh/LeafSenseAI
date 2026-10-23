import gradio as gr

from history import save_analysis
from models import identify_plant
from health_analyzer import analyze_health
from recommendations import get_recommendations


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
        top_prediction["score"] * 100,
        2
    )

    # -----------------------------------------------------
    # 2. HEALTH ANALYSIS
    # -----------------------------------------------------

    health_result = analyze_health(image)

    print("Health result:", health_result)

    health = health_result["health"]
    severity = health_result["severity"]
    explanation = health_result["explanation"]

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

## 📊 Analysis Summary

| Feature | Result |
|---|---|
| Plant | {plant_name} |
| Confidence | {confidence}% |
| Health | {health} |
| Severity | {severity} |

---

> **Note:** This analysis is based on visible features in the uploaded image
> and is intended as a general plant-care guide.
"""

    return report


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