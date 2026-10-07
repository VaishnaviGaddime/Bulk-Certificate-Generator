def test_get_job_status(client):
    create_response = client.post(
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

    assert create_response.status_code == 200

    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["status"] == "COMPLETED"
    assert data["total_certificates"] == 2
    assert data["successful_certificates"] == 2
    assert data["failed_certificates"] == 0
    assert data["progress"] == "2/2"