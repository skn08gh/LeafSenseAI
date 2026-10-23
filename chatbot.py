from plant_data import PLANTS


# ============================================================
# PLANT ALIASES
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

    "tulip": "tulip"
}


# ============================================================
# DETECT PLANT
# ============================================================

def detect_plant(text):
    """
    Detect the plant name mentioned in a message.
    Longer aliases are checked first so specific names
    are matched before shorter ones.
    """

    text = str(text).lower().strip()

    for alias, plant in sorted(
        ALIASES.items(),
        key=lambda x: len(x[0]),
        reverse=True
    ):
        if alias in text:
            return plant

    return None


# ============================================================
# CREATE RESPONSE
# ============================================================

def make_reply(message, plant):

    text = str(message).lower().strip()

    if plant not in PLANTS:
        return (
            "I couldn't find that plant in my database. 🌱 "
            "Please choose one of the available plants."
        )

    p = PLANTS[plant]

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    # Check complete words instead of searching for "hi"
    # inside words such as "this".
    words = set(
        text.replace(",", " ")
            .replace(".", " ")
            .replace("!", " ")
            .replace("?", " ")
            .split()
    )

    if words.intersection({"hello", "hi", "hey"}):
        return (
            f"Hey! 🌱 How is your {p['display']} doing today?"
        )

    # --------------------------------------------------------
    # WATERING
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "water",
            "watering",
            "thirsty",
            "dry soil"
        ]
    ):
        return (
            f"For your {p['display']}, {p['water']} "
            f"{p['notes']} "
            "I wouldn't use a fixed weekly schedule without "
            "checking how quickly your soil dries."
        )

    # --------------------------------------------------------
    # LIGHT
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "light",
            "sun",
            "sunlight",
            "window",
            "bright"
        ]
    ):
        return (
            f"Your {p['display']} does best with {p['light']} "
            "If you tell me your window direction and how far "
            "the plant is from it, I can help judge whether "
            "its current spot works."
        )

    # --------------------------------------------------------
    # YELLOW / BROWN / LEAVES
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "yellow",
            "yellowing",
            "brown",
            "crispy",
            "leaf",
            "leaves"
        ]
    ):
        return (
            f"Let's diagnose the leaves on your {p['display']} "
            "instead of guessing. "
            f"First check the soil: {p['water']} "
            f"Its light preference is {p['light']} "
            "Tell me whether the soil is wet or dry and "
            "whether the affected leaves are old or new."
        )

    # --------------------------------------------------------
    # DROOPING
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "droop",
            "drooping",
            "wilt",
            "wilting"
        ]
    ):
        return (
            f"Let's check the soil before watering your "
            f"{p['display']}. "
            "Very dry soil can indicate thirst, while wet "
            "soil plus drooping can point toward a drainage "
            "or root issue. "
            "Tell me which one you're seeing."
        )

    # --------------------------------------------------------
    # PESTS
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "pest",
            "pests",
            "bug",
            "bugs",
            "aphid",
            "aphids",
            "mite",
            "mites",
            "mealy",
            "mealybug",
            "insect",
            "insects",
            "web",
            "webbing"
        ]
    ):
        return (
            f"Let's identify the pest on your {p['display']} "
            "before choosing a treatment. "
            "Are you seeing tiny moving insects, cottony white "
            "spots, sticky residue, or fine webbing? "
            "Also tell me whether they're on the leaves, "
            "stems, or soil."
        )

    # --------------------------------------------------------
    # GROWTH
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "grow",
            "growth",
            "new leaf",
            "new leaves",
            "not growing",
            "slow growth",
            "slow"
        ]
    ):
        return (
            f"For your {p['display']}, slow growth can involve "
            "light, watering, temperature, nutrition, "
            "or its natural growth rate. "
            "How long has it been in its current spot, "
            "and has it produced any new growth?"
        )

    # --------------------------------------------------------
    # REPOTTING / SOIL
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "repot",
            "repotting",
            "pot",
            "potting",
            "root",
            "roots",
            "soil"
        ]
    ):
        return (
            f"For your {p['display']}, the growing medium "
            f"should be {p['soil']} "
            "Before repotting, check whether roots are tightly "
            "circling the pot, drainage is poor, or the soil "
            "stays wet unusually long."
        )

    # --------------------------------------------------------
    # FERTILIZER / FEEDING
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "fertilizer",
            "fertiliser",
            "fertilize",
            "fertilise",
            "feed",
            "feeding",
            "plant food",
            "nutrients",
            "nutrition"
        ]
    ):
        return (
            f"For your {p['display']}, feeding should be based "
            "on the plant's growth and condition rather than "
            "using fertilizer automatically. 🌱 "
            "If it is actively growing, a suitable balanced "
            "houseplant fertilizer can generally be used "
            "according to its label directions. "
            "Avoid fertilizing a severely stressed or recently "
            "repotted plant until it has settled."
        )

    # --------------------------------------------------------
    # CARE ROUTINE
    # --------------------------------------------------------

    if any(
        x in text
        for x in [
            "routine",
            "schedule",
            "care plan",
            "personalized",
            "personalised",
            "checklist"
        ]
    ):
        return (
            f"Here's a starting care plan for your "
            f"{p['display']} 🌱\n\n"
            f"• Light: {p['light']}\n"
            f"• Water: {p['water']}\n"
            f"• Humidity: {p['humidity']}\n"
            f"• Soil: {p['soil']}\n"
            f"• Note: {p['notes']}\n\n"
            "Tell me where you keep it, your pot size, whether "
            "it has drainage, and your current watering routine "
            "and I'll personalize it further."
        )

    # --------------------------------------------------------
    # DEFAULT RESPONSE
    # --------------------------------------------------------

    return (
        f"Got it — we're talking about your {p['display']}. 🌱\n\n"
        "I can help with:\n"
        "• 💧 Watering\n"
        "• ☀️ Light\n"
        "• 🍂 Yellow or brown leaves\n"
        "• 🥀 Drooping\n"
        "• 🐛 Pests\n"
        "• 📈 Growth\n"
        "• 🪴 Soil and repotting\n"
        "• 🌿 Fertilizer and feeding\n"
        "• 📋 Personalized care routine\n\n"
        "What are you noticing right now?"
    )


# ============================================================
# MAIN CHAT FUNCTION
# ============================================================

def chat(message, selected_plant=None):

    message = str(message).strip()

    # Use the selected plant first.
    # If none is selected, try detecting one from the message.
    plant = selected_plant or detect_plant(message)

    if not plant or plant not in PLANTS:
        return {
            "reply": (
                "🌱 I'd love to help!\n\n"
                "Please choose your plant from the dropdown above "
                "so I can give you personalized advice."
            ),
            "plant": None
        }

    return {
        "reply": make_reply(message, plant),
        "plant": plant
    }

