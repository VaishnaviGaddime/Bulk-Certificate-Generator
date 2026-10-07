def test_create_job(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "organization": "AEREO",
            "event_date": "2026-10-15",
            "recipients": [
                {
                    "name": "Vaishnavi Gaddime",
                    "email": "vaishnavi@example.com"
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

    assert data["status"] == "COMPLETED"
    assert data["total_certificates"] == 2
    assert data["successful_certificates"] == 2
    assert data["failed_certificates"] == 0
    assert "job_id" in data