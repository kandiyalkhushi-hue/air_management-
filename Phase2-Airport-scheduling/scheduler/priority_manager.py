# scheduler/priority_manager.py


# Lower number = higher priority
SITUATION_PRIORITY = {
    "MEDICAL": 1,
    "EMERGENCY": 2,
    "LOW_FUEL": 3,
    "WEATHER": 4,
    "VIP": 5,
    "NORMAL": 6
}


def get_priority(situation):
    """
    Convert flight situation into scheduling priority.

    Lower number means higher priority.
    """

    situation = situation.upper().strip()

    if situation not in SITUATION_PRIORITY:
        raise ValueError(
            f"Invalid flight situation: {situation}"
        )

    return SITUATION_PRIORITY[situation]


def get_situation_name(priority):
    """
    Convert priority number back to situation.
    """

    for situation, value in SITUATION_PRIORITY.items():

        if value == priority:
            return situation

    return "NORMAL"