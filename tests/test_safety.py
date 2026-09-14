from app.services.vehicle_safety_guard import check_vehicle_safety


def test_brake_failure():
    result = check_vehicle_safety(
        "My brakes are not working and I cannot stop properly."
    )

    assert result.triggered is True
    assert result.category == "brake_failure"
    assert result.response is not None


def test_fuel_leak():
    result = check_vehicle_safety(
        "There is fuel leaking from my vehicle and there is a strong fuel smell."
    )

    assert result.triggered is True
    assert result.category == "fuel_leakage"
    assert result.response is not None


def test_electrical_fire():
    result = check_vehicle_safety(
        "Smoke is coming from the electrical wiring and there is a fire."
    )

    assert result.triggered is True
    assert result.category == "electrical_fire"
    assert result.response is not None


def test_normal_question():
    result = check_vehicle_safety(
        "How often should I change my engine oil?"
    )

    assert result.triggered is False
    assert result.category is None
    assert result.response is None