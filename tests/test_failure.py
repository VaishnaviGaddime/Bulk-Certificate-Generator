def test_certificate_failure_is_isolated(client, monkeypatch):
    from app.routers import jobs

    original_generate = jobs.generate_certificate

    def mock_generate_certificate(
        certificate_id,
        recipient_name,
        event_name,
        organization,
        event_date
    ):
        if recipient_name == "Fail Test":
            raise Exception("Simulated certificate generation failure")

        return original_generate(
            certificate_id,
            recipient_name,
            event_name,
            organization,
            event_date
        )

    monkeypatch.setattr(
        jobs,
        "generate_certificate",
        mock_generate_certificate
    )

    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "organization": "AEREO",
            "event_date": "2026-10-15",
            "recipients": [
                {
                    "name": "Fail Test",
                    "email": "fail@example.com"
                },
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@example.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "PARTIAL_FAILURE"
    assert data["total_certificates"] == 2
    assert data["successful_certificates"] == 1
    assert data["failed_certificates"] == 1