def test_create_job_with_empty_recipients(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "organization": "AEREO",
            "event_date": "2026-10-15",
            "recipients": []
        }
    )

    assert response.status_code == 422


def test_create_job_with_invalid_email(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Python Workshop",
            "organization": "AEREO",
            "event_date": "2026-10-15",
            "recipients": [
                {
                    "name": "Vaishnavi Gaddime",
                    "email": "invalid-email"
                }
            ]
        }
    )

    assert response.status_code == 422