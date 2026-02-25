"""Tests para el blueprint admin: control de acceso y vistas."""
from tests.conftest import make_user, make_admin, make_landing, login


# ---------------------------------------------------------------------------
# Control de acceso
# ---------------------------------------------------------------------------

def test_admin_sin_login_redirige(client):
    res = client.get('/admin/')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_admin_usuario_normal_403(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/admin/')
    assert res.status_code == 403


def test_admin_ok(client, db):
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/')
    assert res.status_code == 200


def test_pedidos_sin_login_redirige(client):
    res = client.get('/admin/pedidos')
    assert res.status_code == 302


def test_pedidos_usuario_normal_403(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/admin/pedidos')
    assert res.status_code == 403


def test_pedidos_ok(client, db):
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos')
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# Seguridad: LandingRequest sin usuario no debe crashear el admin
# ---------------------------------------------------------------------------

def test_admin_index_con_landing_anonimo(client, db):
    """Regresión: req.user era None y crashaba con AttributeError."""
    make_landing(db, user=None)
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/')
    assert res.status_code == 200
    assert '—'.encode('utf-8') in res.data  # muestra guion en lugar de email


def test_pedidos_con_landing_anonimo(client, db):
    """Regresión: mismo bug en la tabla de pedidos."""
    make_landing(db, user=None)
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos')
    assert res.status_code == 200
    assert '\u2014'.encode('utf-8') in res.data


# ---------------------------------------------------------------------------
# Filtros
# ---------------------------------------------------------------------------

def test_pedidos_filtro_tipo(client, db):
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos?tipo=b2b')
    assert res.status_code == 200


def test_pedidos_filtro_sector_valido(client, db):
    make_landing(db, sector='abogatap')
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos?sector=abogatap')
    assert res.status_code == 200
    assert b'ABOGATAP' in res.data


def test_pedidos_filtro_saludtap_sin_resultados(client, db):
    """saludtap fue eliminado — filtrar por él no debe romper nada."""
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos?sector=saludtap')
    assert res.status_code == 200
    assert b'No hay pedidos' in res.data


def test_pedidos_paginacion(client, db):
    admin = make_admin(db)
    login(client, admin.email, 'adminpass')
    res = client.get('/admin/pedidos?page=1')
    assert res.status_code == 200
