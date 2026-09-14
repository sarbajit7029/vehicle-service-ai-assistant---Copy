from app.services.vehicle_safety_guard import check_vehicle_safety


def test_safe_maintenance_question() -> None:
    result = check_vehicle_safety(
        "What is the recommended maintenance schedule?"
    )

    assert result.triggered is False
    assert result.category is None
    assert result.response is None


def test_brake_failure_question() -> None:
    result = check_vehicle_safety(
        "My brakes are not working."
    )

    assert result.triggered is True
    assert result.category == "brake_failure"
    assert result.response is not None


def test_fuel_leak_question() -> None:
    result = check_vehicle_safety(
        "There is a fuel leak from my vehicle."
    )

    assert result.triggered is True
    assert result.category == "fuel_leakage"
    assert result.response is not None


def test_electrical_fire_question() -> None:
    result = check_vehicle_safety(
        "There is an electrical fire in my car."
    )

    assert result.triggered is True
    assert result.category == "electrical_fire"
    assert result.response is not None


def test_normal_engine_question() -> None:
    result = check_vehicle_safety(
        "What does normal engine maintenance include?"
    )

    assert result.triggered is False
    assert result.category is None
    assert result.response is None