"""Tests para el blueprint auth: registro, login y logout."""
from tests.conftest import make_user, login


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------

def test_registro_get(client):
    res = client.get('/registro')
    assert res.status_code == 200


def test_registro_ok(client, db):
    res = client.post('/registro', data={
        'email': 'nuevo@test.com',
        'password': 'password123',
        'password2': 'password123',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Bienvenido' in res.data


def test_registro_email_duplicado(client, db):
    make_user(db, email='existe@test.com')
    res = client.post('/registro', data={
        'email': 'existe@test.com',
        'password': 'password123',
        'password2': 'password123',
    }, follow_redirects=True)
    assert res.status_code == 200
    # La validación debe rechazarlo — el form se re-renderiza (no flash de bienvenida)
    assert b'Bienvenido' not in res.data


def test_registro_passwords_no_coinciden(client, db):
    res = client.post('/registro', data={
        'email': 'otro@test.com',
        'password': 'password123',
        'password2': 'diferente456',
    }, follow_redirects=True)
    assert res.status_code == 200
    # No debe haber redirigido al home
    assert b'Bienvenido' not in res.data


def test_registro_redirige_si_autenticado(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/registro')
    assert res.status_code == 302


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_get(client):
    res = client.get('/login')
    assert res.status_code == 200


def test_login_ok(client, db):
    make_user(db, email='user@test.com', password='password123')
    res = login(client, 'user@test.com', 'password123')
    assert res.status_code == 200
    assert b'correctamente' in res.data


def test_login_password_incorrecta(client, db):
    make_user(db, email='user@test.com', password='password123')
    res = login(client, 'user@test.com', 'incorrecta')
    assert res.status_code == 200
    assert b'incorrectos' in res.data


def test_login_email_inexistente(client, db):
    res = login(client, 'noexiste@test.com', 'cualquier')
    assert res.status_code == 200
    assert b'incorrectos' in res.data


def test_login_redirige_si_autenticado(client, db):
    make_user(db)
    login(client, 'user@test.com', 'password123')
    res = client.get('/login')
    assert res.status_code == 302


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def test_logout_ok(client, db):
    make_user(db)
    login(client, 'user@test.com', 'password123')
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b'cerrada' in res.data


def test_logout_sin_sesion_ok(client):
    # Logout sin estar autenticado no debe explotar
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
