from app.db.models.job_card import JobCard


def test_job_card_estimate():
    job_card = JobCard(
        booking_id=1,
        technician_id=1,
        notes="Brake inspection required",
        estimate={
            "parts": 2500,
            "labour": 1000,
            "total": 3500,
        },
        status="PENDING",
    )

    assert job_card.estimate["parts"] == 2500
    assert job_card.estimate["labour"] == 1000
    assert job_card.estimate["total"] == 3500


def test_job_card_status():
    job_card = JobCard(
        booking_id=1,
        technician_id=1,
        notes="Inspection completed",
        estimate={
            "total": 5000,
        },
        status="PENDING",
    )

    assert job_card.status == "PENDING"

    job_card.status = "IN_PROGRESS"

    assert job_card.status == "IN_PROGRESS"