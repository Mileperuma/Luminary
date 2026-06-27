"""Tests for /api/preferences CRUD."""


def test_bulk_create_lists_and_owns_by_user(logged_in_client) -> None:
    client, headers = logged_in_client

    payload = {"preferences": [
        {"media_type": "book", "key": "genre", "value": "literary fiction", "weight": 0.8},
        {"media_type": "movie", "key": "tone", "value": "calm", "weight": 0.6},
    ]}
    res = client.post("/api/preferences", headers=headers, json=payload)
    assert res.status_code == 201
    body = res.json()
    assert len(body) == 2
    assert {p["value"] for p in body} == {"literary fiction", "calm"}

    listed = client.get("/api/preferences", headers=headers).json()
    assert len(listed) == 2


def test_patch_updates_value_and_weight(logged_in_client) -> None:
    client, headers = logged_in_client

    created = client.post(
        "/api/preferences",
        headers=headers,
        json={"preferences": [{"media_type": "book", "key": "genre", "value": "scifi", "weight": 0.5}]},
    ).json()
    pid = created[0]["id"]

    res = client.patch(
        f"/api/preferences/{pid}",
        headers=headers,
        json={"value": "literary scifi", "weight": 0.9},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["value"] == "literary scifi"
    assert body["weight"] == 0.9
    assert body["source"] == "explicit"


def test_delete_removes_row(logged_in_client) -> None:
    client, headers = logged_in_client

    created = client.post(
        "/api/preferences",
        headers=headers,
        json={"preferences": [{"media_type": "article", "key": "topic", "value": "design", "weight": 0.7}]},
    ).json()
    pid = created[0]["id"]

    delete_res = client.delete(f"/api/preferences/{pid}", headers=headers)
    assert delete_res.status_code == 204

    listed = client.get("/api/preferences", headers=headers).json()
    assert listed == []


def test_patch_with_invalid_weight_returns_422(logged_in_client) -> None:
    client, headers = logged_in_client
    created = client.post(
        "/api/preferences",
        headers=headers,
        json={"preferences": [{"media_type": "book", "key": "genre", "value": "scifi", "weight": 0.5}]},
    ).json()
    pid = created[0]["id"]

    res = client.patch(f"/api/preferences/{pid}", headers=headers, json={"weight": 5.0})
    assert res.status_code == 422


def test_patch_unknown_preference_returns_404(logged_in_client) -> None:
    client, headers = logged_in_client
    res = client.patch(
        "/api/preferences/00000000-0000-0000-0000-000000000000",
        headers=headers,
        json={"value": "x"},
    )
    assert res.status_code == 404
