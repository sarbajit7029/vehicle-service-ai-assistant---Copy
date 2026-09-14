from app.schemas.vehicle import VehicleCreate


def test_vehicle_schema_creation():
    vehicle = VehicleCreate(
        customer_id=1,
        registration_no="WB00TEST01",
        make="Toyota",
        model="Innova",
        year=2022,
        details={},
    )

    assert vehicle.customer_id == 1
    assert vehicle.registration_no == "WB00TEST01"
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Innova"
    assert vehicle.year == 2022


def test_vehicle_requires_valid_registration():
    vehicle = VehicleCreate(
        customer_id=1,
        registration_no="WB00VALID01",
        make="Honda",
        model="City",
        year=2020,
        details={},
    )

    assert vehicle.registration_no == "WB00VALID01"


def test_vehicle_rejects_invalid_year():
    try:
        VehicleCreate(
            customer_id=1,
            registration_no="WB00YEAR01",
            make="Toyota",
            model="Innova",
            year=1700,
            details={},
        )
    except ValueError:
        assert True
    else:
        assert False, "Expected validation error for invalid year"