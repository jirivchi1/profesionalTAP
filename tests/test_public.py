"""Tests para las rutas públicas (blueprint public)."""


def test_home_ok(client):
    res = client.get('/')
    assert res.status_code == 200


def test_about_ok(client):
    res = client.get('/about')
    assert res.status_code == 200


def test_contacto_ok(client):
    res = client.get('/contacto')
    assert res.status_code == 200


def test_profesionales_ok(client):
    res = client.get('/profesionales')
    assert res.status_code == 200


def test_profesional_inexistente_404(client):
    res = client.get('/profesionales/99999')
    assert res.status_code == 404


def test_ruta_inexistente_404(client):
    res = client.get('/esta-ruta-no-existe')
    assert res.status_code == 404
