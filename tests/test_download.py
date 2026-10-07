def test_download_certificate(client):
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
                }
            ]
        }
    )

    assert create_response.status_code == 200

    job_id = create_response.json()["job_id"]

    certificates_response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificate_id = certificates_response.json()["certificates"][0]["id"]

    response = client.get(
        f"/api/jobs/certificates/{certificate_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")