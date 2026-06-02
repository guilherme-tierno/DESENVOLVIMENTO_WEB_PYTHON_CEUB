"""Smoke tests — só verificam que a app sobe."""


def test_soma_dois_numeros_positivos():
    """Sanity check do próprio pytest (AAA básico)."""
    a, b = 2, 3
    resultado = a + b
    assert resultado == 5


def test_home_responde_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"MicroTask" in response.data


def test_sobre_responde_200(client):
    response = client.get("/sobre")
    assert response.status_code == 200


def test_pagina_inexistente_retorna_404(client):
    response = client.get("/rota-que-nao-existe-na-vida")
    assert response.status_code == 404
