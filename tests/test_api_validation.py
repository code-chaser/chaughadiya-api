def test_chaughadiya_requires_date(client):
    response = client.get(
        "/api/get-chaughadiya",
        query_string={"latitude": "10.0", "longitude": "20.0"},
    )
    assert response.status_code == 400
    assert "date" in response.get_json()["error"]


def test_muhurat_requires_timestamp(client):
    response = client.get(
        "/api/get-muhurat",
        query_string={"latitude": "10.0", "longitude": "20.0"},
    )
    assert response.status_code == 400
    assert "timestamp" in response.get_json()["error"]


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"

