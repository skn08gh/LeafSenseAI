"""Gradio plant-care reminders based on the supplied care schedule dataset."""

import csv
import difflib
import html
import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import gradio as gr


_APP_DIR = Path(__file__).resolve().parent
_DATASET_CANDIDATES = (
    _APP_DIR / "data" / "plant_care_schedule.csv",
    _APP_DIR / "PlantCare_AI_Simple_Schedule.csv",
)
DATASET_PATH = next(
    (path for path in _DATASET_CANDIDATES if path.is_file()),
    _DATASET_CANDIDATES[0],
)
WATER_COLUMN = "When to water"
FERTILIZER_COLUMN = "When to add fertilizer"


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def load_schedules(path: Path = DATASET_PATH) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as dataset:
        rows = list(csv.DictReader(dataset))
    required_columns = {"Plant", WATER_COLUMN, FERTILIZER_COLUMN, "Sunlight / where to keep it"}
    if not rows or not required_columns.issubset(rows[0]):
        raise ValueError(f"The care schedule dataset is missing required columns: {path}")
    return rows


def interval_days(instruction: str) -> int | None:
    """Estimate a reminder interval from an explicit cadence in the dataset."""
    text = instruction.lower().replace("–", "-").replace("—", "-")

    if re.search(r"\bdo not\b|\bdon't\b|\bnever\b", text):
        return None

    frequency = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s+times?\s+(?:a|per)\s+week",
        text,
    )
    if frequency:
        low = float(frequency.group(1))
        high = float(frequency.group(2) or low)
        return max(1, round(7 / ((low + high) / 2)))
    if "several times a week" in text:
        return 3
    if re.search(r"\bonce\s+(?:a|per)\s+week\b", text):
        return 7

    cadence = re.search(
        r"\b(?:every|once every)\s+(\d+(?:\.\d+)?)"
        r"(?:\s*-\s*(\d+(?:\.\d+)?))?\s*(days?|weeks?|months?)\b",
        text,
    )
    if cadence:
        low = float(cadence.group(1))
        high = float(cadence.group(2) or low)
        unit = cadence.group(3)
        multiplier = 1 if unit.startswith("day") else 7 if unit.startswith("week") else 30.44
        return max(1, round(((low + high) / 2) * multiplier))

    if re.search(r"\bmonthly\b", text):
        return 30

    return None


CARE_SCHEDULES = load_schedules()


def find_plant(name: str) -> dict[str, str] | None:
    query = normalize_name(name)
    if not query:
        return None

    exact_matches = [
        row for row in CARE_SCHEDULES
        if query == normalize_name(row["Plant"])
    ]
    if exact_matches:
        return exact_matches[0]

    partial_matches = [
        row for row in CARE_SCHEDULES
        if query in normalize_name(row["Plant"])
        or normalize_name(row["Plant"]) in query
    ]
    if len(partial_matches) == 1:
        return partial_matches[0]
    return None


def parse_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise ValueError("Choose a valid date.")


def due_date(last_done: str | date, interval: int) -> date:
    return parse_date(last_done) + timedelta(days=interval)


def _due_label(last_done: str, interval: int | None, today: date) -> str:
    if interval is None:
        return "No calendar interval in dataset"
    next_date = due_date(last_done, interval)
    if next_date < today:
        days_overdue = (today - next_date).days
        return f"Overdue by {days_overdue} day{'s' if days_overdue != 1 else ''} · {next_date:%b %d, %Y}"
    if next_date == today:
        return f"Due today · {next_date:%b %d, %Y}"
    days_until = (next_date - today).days
    return f"Due in {days_until} day{'s' if days_until != 1 else ''} · {next_date:%b %d, %Y}"


def render_plants(plants: list[dict[str, str]] | None, today: date | None = None) -> str:
    today = today or date.today()
    if not plants:
        return (
            '<div class="empty-state">Add a plant to see its schedule and '
            'upcoming care dates.</div>'
        )

    cards = []
    for tracked in plants:
        schedule = next(
            row for row in CARE_SCHEDULES if row["Plant"] == tracked["plant"]
        )
        water_interval = interval_days(schedule[WATER_COLUMN])
        fertilizer_interval = interval_days(schedule[FERTILIZER_COLUMN])
        water_due = _due_label(tracked["last_watered"], water_interval, today)
        fertilizer_due = _due_label(
            tracked["last_fertilized"], fertilizer_interval, today
        )
        fertilizer_text = (
            "Not recommended"
            if fertilizer_interval is None
            and re.search(r"\bdo not\b|\bdon't\b|\bnever\b", schedule[FERTILIZER_COLUMN], re.I)
            else schedule[FERTILIZER_COLUMN]
        )
        cards.append(
            f"""
            <article class="plant-card">
              <h3>{html.escape(schedule["Plant"])}</h3>
              <p class="sunlight">{html.escape(schedule["Sunlight / where to keep it"])}</p>
              <div class="care-grid">
                <section class="care-item">
                  <h4>💧 Watering</h4>
                  <p>{html.escape(schedule[WATER_COLUMN])}</p>
                  <p class="due">{html.escape(water_due)}</p>
                  <small>Last watered: {html.escape(tracked["last_watered"])}</small>
                </section>
                <section class="care-item">
                  <h4>🌱 Fertilizing</h4>
                  <p>{html.escape(fertilizer_text)}</p>
                  <p class="due">{html.escape(fertilizer_due)}</p>
                  <small>Last fertilized: {html.escape(tracked["last_fertilized"])}</small>
                </section>
              </div>
              <p class="caveat">Calculated reminders are estimates from the dataset.
              Follow soil/season conditions and the care instructions above.</p>
            </article>
            """
        )
    return "\n".join(cards)


def add_or_update_plant(
    name: str,
    last_watered: Any,
    last_fertilized: Any,
    plants: list[dict[str, str]] | None,
) -> tuple[list[dict[str, str]], Any, str, str]:
    plants = list(plants or [])
    schedule = find_plant(name or "")
    if schedule is None:
        query = normalize_name(name or "")
        ambiguous_matches = [
            row["Plant"]
            for row in CARE_SCHEDULES
            if query
            and query in normalize_name(row["Plant"])
        ]
        if len(ambiguous_matches) > 1:
            choices = [item["plant"] for item in plants]
            detail = "That name matches more than one plant. Choose a specific name: " + "; ".join(
                ambiguous_matches
            )
            return plants, gr.update(choices=choices), render_plants(plants), detail

        suggestions = difflib.get_close_matches(
            normalize_name(name or ""),
            [normalize_name(row["Plant"]) for row in CARE_SCHEDULES],
            n=3,
            cutoff=0.35,
        )
        detail = (
            "I couldn't match that plant to the supplied dataset."
            if not suggestions
            else "I couldn't match that plant. Try one of: "
            + ", ".join(suggestions)
        )
        choices = [item["plant"] for item in plants]
        return plants, gr.update(choices=choices), render_plants(plants), detail

    try:
        water_date = parse_date(last_watered).isoformat()
        fertilizer_date = parse_date(last_fertilized).isoformat()
    except (TypeError, ValueError) as exc:
        choices = [item["plant"] for item in plants]
        return plants, gr.update(choices=choices), render_plants(plants), str(exc)

    record = {
        "plant": schedule["Plant"],
        "last_watered": water_date,
        "last_fertilized": fertilizer_date,
    }
    existing_index = next(
        (index for index, item in enumerate(plants) if item["plant"] == record["plant"]),
        None,
    )
    if existing_index is None:
        plants.append(record)
        message = f"Added {schedule['Plant']} to your reminders."
    else:
        plants[existing_index] = record
        message = f"Updated the last-care dates for {schedule['Plant']}."

    choices = [item["plant"] for item in plants]
    return (
        plants,
        gr.update(choices=choices, value=schedule["Plant"]),
        render_plants(plants),
        message,
    )


def load_saved_plants(
    plants: list[dict[str, str]] | None,
) -> tuple[Any, str]:
    plants = list(plants or [])
    choices = [item["plant"] for item in plants]
    return (
        gr.update(choices=choices, value=choices[0] if choices else None),
        render_plants(plants),
    )


def complete_task(
    selected_plant: str,
    task: str,
    plants: list[dict[str, str]] | None,
    completed_on: date | None = None,
) -> tuple[list[dict[str, str]], str, str]:
    plants = list(plants or [])
    tracked = next(
        (item for item in plants if item["plant"] == selected_plant),
        None,
    )
    if tracked is None:
        return plants, render_plants(plants), "Select a tracked plant first."

    schedule = next(row for row in CARE_SCHEDULES if row["Plant"] == selected_plant)
    column = WATER_COLUMN if task == "Watering" else FERTILIZER_COLUMN
    if task not in {"Watering", "Fertilizing"}:
        return plants, render_plants(plants), "Choose watering or fertilizing."
    if interval_days(schedule[column]) is None:
        return (
            plants,
            render_plants(plants),
            "This care instruction has no recurring calendar interval to complete.",
        )

    completed_date = (completed_on or date.today()).isoformat()
    date_field = "last_watered" if task == "Watering" else "last_fertilized"
    tracked[date_field] = completed_date
    return (
        plants,
        render_plants(plants),
        f"Marked {task.lower()} complete for {selected_plant} on {completed_date}.",
    )


theme = gr.themes.Soft(
    primary_hue="green",
    secondary_hue="emerald",
    neutral_hue="slate",
).set(
    body_background_fill="#0b1220",
    body_text_color="#e5e7eb",
    background_fill_primary="#111827",
    background_fill_secondary="#1f2937",
    border_color_primary="#334155",
    button_primary_background_fill="#16a34a",
    button_primary_background_fill_hover="#15803d",
    button_primary_text_color="#ffffff",
    input_background_fill="#0b1220",
    input_border_color="#334155",
    block_background_fill="#111827",
)

CSS = """
.plant-card {
  background: #111827;
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 1.25rem;
  margin: 1rem 0;
  color: #e5e7eb;
}
.plant-card h3, .care-item h4 { color: #d1fae5; }
.sunlight, .caveat, .care-item small { color: #9ca3af; }
.care-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }
.care-item { background: #0b1220; border: 1px solid #263449; border-radius: 12px; padding: 1rem; }
.due { color: #86efac; font-weight: 700; }
.caveat { margin-top: 1rem; font-size: 0.9rem; }
.empty-state { background: #111827; border: 1px dashed #475569; border-radius: 12px; padding: 1.25rem; color: #cbd5e1; }
"""

with gr.Blocks(title="LeafSense Plant Care Reminders") as demo:
    gr.Markdown(
        """
# 🌿 Plant Care Reminders
Enter a plant name from the supplied care dataset. Due dates are calculated
from the last time you watered or fertilized it.
"""
    )
    tracked_plants = gr.BrowserState(
        default_value=[],
        storage_key="leafsense_plant_care_tracker_v1",
    )
    with gr.Row():
        with gr.Column():
            plant_name = gr.Textbox(
                label="Plant name",
                placeholder="e.g. Monstera, Aloe Vera, Pothos",
            )
            last_watered = gr.DateTime(
                value=date.today().isoformat(),
                include_time=False,
                type="string",
                label="Date last watered",
            )
            last_fertilized = gr.DateTime(
                value=date.today().isoformat(),
                include_time=False,
                type="string",
                label="Date last fertilized",
            )
            add_button = gr.Button("Add / Update Plant", variant="primary")
        with gr.Column():
            plant_to_complete = gr.Dropdown(
                choices=[],
                label="Plant for completed task",
                info="Marking a task complete resets its next due date to today.",
            )
            task_to_complete = gr.Dropdown(
                choices=["Watering", "Fertilizing"],
                value="Watering",
                label="Care task",
            )
            complete_button = gr.Button("Mark Task Completed", variant="primary")

    feedback = gr.Markdown()
    dashboard = gr.HTML(render_plants([]))
    add_button.click(
        fn=add_or_update_plant,
        inputs=[plant_name, last_watered, last_fertilized, tracked_plants],
        outputs=[tracked_plants, plant_to_complete, dashboard, feedback],
    )
    demo.load(
        fn=load_saved_plants,
        inputs=[tracked_plants],
        outputs=[plant_to_complete, dashboard],
    )
    complete_button.click(
        fn=complete_task,
        inputs=[plant_to_complete, task_to_complete, tracked_plants],
        outputs=[tracked_plants, dashboard, feedback],
    )


if __name__ == "__main__":
    demo.launch(theme=theme, css=CSS)
