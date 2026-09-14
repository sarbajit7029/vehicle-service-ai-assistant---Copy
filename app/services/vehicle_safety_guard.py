from dataclasses import dataclass


@dataclass(frozen=True)
class SafetyCheckResult:
    triggered: bool
    category: str | None
    response: str | None


# Critical vehicle-safety patterns.
# These are intentionally conservative because a false negative
# can be more dangerous than a false positive.
SAFETY_PATTERNS: dict[str, tuple[str, ...]] = {
   "brake_failure": (
    "brake failure",
    "brakes failed",
    "brake failed",
    "brakes are not working",
    "brake is not working",
    "brakes not working",
    "brake not working",
    "no brakes",
    "lost my brakes",
    "braking failure",
    "brake pedal went to the floor",
    "brake pedal is on the floor",
    "brake pedal on the floor",
    "brake pedal feels soft",
    "brake pedal is soft",
    "brake pedal has no pressure",
    "brake pedal has no resistance",
    "brakes have no pressure",
    "cannot stop properly",
    "can't stop properly",
    "cannot stop",
    "can't stop",
    "vehicle cannot stop",
    "car cannot stop",
),
    "steering_failure": (
        "steering failure",
        "steering failed",
        "steering is not working",
        "steering not working",
        "lost steering",
        "cannot steer",
        "can't steer",
    ),
    "tyre_failure": (
        "tyre failure",
        "tire failure",
        "tyre burst",
        "tire burst",
        "tyre blowout",
        "tire blowout",
        "tyre exploded",
        "tire exploded",
    ),
    "fuel_leakage": (
        "fuel leak",
        "fuel leakage",
        "petrol leak",
        "petrol leakage",
        "diesel leak",
        "diesel leakage",
        "fuel is leaking",
        "petrol is leaking",
        "diesel is leaking",
    ),
    "electrical_fire": (
    "electrical fire",
    "electrical system fire",
    "electrical wiring fire",
    "electrical wiring is on fire",
    "wiring fire",
    "wiring is on fire",
    "electrical wiring and there is a fire",
    "electrical wiring and there is fire",
    "smoke from electrical wiring",
    "smoke is coming from the electrical wiring",
    "smoke coming from electrical wiring",
    "car wiring is burning",
    "vehicle wiring is burning",
),
    "smoke": (
        "smoke from engine",
        "smoke from car",
        "smoke from vehicle",
        "car is smoking",
        "vehicle is smoking",
        "engine is smoking",
        "heavy smoke",
        "thick smoke",
    ),
    "severe_overheating": (
        "engine overheating",
        "engine is overheating",
        "severe overheating",
        "vehicle is overheating",
        "car is overheating",
        "temperature is extremely high",
        "temperature gauge is in the red",
        "temperature gauge in the red",
    ),
    "dangerous_fluid_leakage": (
        "oil leak",
        "oil leakage",
        "brake fluid leak",
        "brake fluid leakage",
        "coolant leak",
        "coolant leakage",
        "coolant is leaking",
        "fluid is leaking",
        "fluid leakage",
        "major fluid leak",
        "large fluid leak",
    ),
}


def _normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def check_vehicle_safety(question: str) -> SafetyCheckResult:
    """
    Check whether a user question describes a potentially
    dangerous vehicle condition.

    This service does not diagnose the vehicle and does not
    provide repair instructions.
    """

    normalized = _normalize_text(question)

    if not normalized:
        return SafetyCheckResult(
            triggered=False,
            category=None,
            response=None,
        )

    for category, patterns in SAFETY_PATTERNS.items():
        if any(pattern in normalized for pattern in patterns):
            return SafetyCheckResult(
                triggered=True,
                category=category,
                response=build_safety_response(category),
            )

    return SafetyCheckResult(
        triggered=False,
        category=None,
        response=None,
    )


def build_safety_response(category: str) -> str:
    """
    Return a conservative response for a critical vehicle condition.
    """

    return (
        "This sounds like a potentially dangerous vehicle safety issue. "
        "For your safety, stop using the vehicle and move to a safe "
        "location if it is safe to do so. Do not continue driving if "
        "the vehicle may be unsafe. Contact a qualified technician, "
        "vehicle service centre, or appropriate roadside assistance "
        "for professional help. I cannot provide step-by-step repair "
        "instructions for a potentially dangerous condition."
    )