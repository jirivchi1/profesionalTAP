"""Tests para el blueprint dashboard: índice, mensaje y CRUD de perfil/servicio."""
from tests.conftest import make_user, make_landing, login
from app.models.contact import Contact


# ---------------------------------------------------------------------------
# /dashboard
# ---------------------------------------------------------------------------

def test_dashboard_requiere_login(client):
    res = client.get('/dashboard')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_dashboard_ok(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/dashboard')
    assert res.status_code == 200


def test_dashboard_muestra_landings_del_usuario(client, db):
    user = make_user(db)
    # make_landing fija contact_name='Nombre Prueba'; el template muestra contact_name or business_name
    make_landing(db, user=user)
    login(client, user.email, 'password123')
    res = client.get('/dashboard')
    assert b'Nombre Prueba' in res.data


# ---------------------------------------------------------------------------
# /dashboard/mensaje/<contact_id>
# ---------------------------------------------------------------------------

def _crear_contacto(db, user):
    req = make_landing(db, user=user)
    contact = Contact(
        request_id=req.id,
        name='Carlos Visitante',
        email='carlos@test.com',
    )
    db.session.add(contact)
    db.session.commit()
    return contact


def test_mensaje_ok(client, db):
    user = make_user(db)
    contact = _crear_contacto(db, user)
    login(client, user.email, 'password123')
    res = client.get(f'/dashboard/mensaje/{contact.id}')
    assert res.status_code == 200
    data = res.get_json()
    assert 'message' in data
    assert 'Carlos Visitante' in data['message']


def test_mensaje_otro_usuario_403(client, db):
    user = make_user(db)
    otro = make_user(db, email='otro@test.com')
    contact = _crear_contacto(db, otro)
    login(client, user.email, 'password123')
    res = client.get(f'/dashboard/mensaje/{contact.id}')
    assert res.status_code == 403


def test_mensaje_contacto_inexistente_403(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/dashboard/mensaje/99999')
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# Perfil profesional
# ---------------------------------------------------------------------------

def test_crear_perfil_get(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/perfil/crear')
    assert res.status_code == 200


def test_crear_perfil_ok(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.post('/perfil/crear', data={
        'name': 'Ana Abogada',
        'specialty': 'Derecho civil',
        'phone': '600111222',
        'bio': 'Abogada con 10 años de experiencia.',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'creado' in res.data


def test_crear_perfil_redirige_si_ya_existe(client, db):
    from app.models.professional import Professional
    user = make_user(db)
    prof = Professional(user_id=user.id, name='Ya existe')
    db.session.add(prof)
    db.session.commit()
    login(client, user.email, 'password123')
    res = client.get('/perfil/crear')
    assert res.status_code == 302


def test_editar_perfil_sin_perfil_redirige(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/perfil/editar')
    assert res.status_code == 302


# ---------------------------------------------------------------------------
# Servicios del perfil legacy
# ---------------------------------------------------------------------------

def _crear_perfil(db, user):
    from app.models.professional import Professional
    prof = Professional(user_id=user.id, name='Prof Test')
    db.session.add(prof)
    db.session.commit()
    return prof


def test_crear_servicio_ok(client, db):
    user = make_user(db)
    _crear_perfil(db, user)
    login(client, user.email, 'password123')
    res = client.post('/servicios/crear', data={
        'title': 'Consultoría fiscal',
        'description': 'Asesoría fiscal para empresas',
        'price': '150',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'creado' in res.data


def test_eliminar_servicio_otro_usuario_403(client, db):
    from app.models.service import Service
    user = make_user(db)
    otro = make_user(db, email='otro@test.com')
    prof_otro = _crear_perfil(db, otro)
    svc = Service(professional_id=prof_otro.id, title='Servicio ajeno')
    db.session.add(svc)
    db.session.commit()

    _crear_perfil(db, user)
    login(client, user.email, 'password123')
    res = client.post(f'/servicios/{svc.id}/eliminar')
    assert res.status_code == 403
