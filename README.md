# LeafSense AI

LeafSense AI is a Gradio app for plant identification, plant recommendations,
PlantPal chat, analysis history, and plant-care reminders.

## Requirements

- Python 3.11 or newer
- The Python packages listed in `requirements.txt`

## Install and run

From the project directory, create and activate a virtual environment, then
install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Open the local URL printed in the terminal (normally
`http://127.0.0.1:7860`).

## Plant identification model

Plant identification requires these files in the project directory:

- `plant_model.h5`
- `class_names.json`

The class names must correspond to the output classes of the model, in the
same order. These model files are not included in this repository. Without
them, the rest of the app can run, but plant identification will be
unavailable. Obtain the matching files from the project maintainer and place
them beside `app.py`.

## PlantPal configuration

PlantPal uses the Lyzr Agent API. Create a local `.env` file in the project
directory and set:

```text
LYZR_API_KEY=your_api_key
LYZR_AGENT_ID=your_agent_id
```

Never commit `.env` or publish API credentials. The app's other features,
including plant-care reminders, do not require these credentials.

## Plant-care reminders

Open the **Plant Care Reminders** tab, add a plant, and enter its last watering
and fertilizing dates. The app calculates estimated due dates from
`PlantCare_AI_Simple_Schedule.csv`. Reminder data is stored in the browser
that you use; it does not send operating-system notifications or sync between
devices.
