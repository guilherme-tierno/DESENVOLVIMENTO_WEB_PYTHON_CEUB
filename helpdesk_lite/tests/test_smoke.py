def test_get_home_status_200(client):
    """Testa se a rota raiz retorna status code 200."""
    response = client.get('/')
    assert response.status_code == 200