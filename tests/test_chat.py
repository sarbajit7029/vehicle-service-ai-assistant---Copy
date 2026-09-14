def test_chat_endpoint_exists(client):
    response = client.post(
        "/api/v1/chat",
        json={
            "question": "How often should I service my vehicle?"
        },
    )

    assert response.status_code != 404