async def test_index(client):
    resp = await client.get('/')
    assert resp.status == 200

    text = await resp.text()
    assert 'Greatness' in text
