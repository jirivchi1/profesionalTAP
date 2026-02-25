"""Tests para el blueprint landing: crear perfil QR, vistas públicas y contactos."""
from tests.conftest import make_user, make_landing, login

FORM_BASE = {
    'sector': 'abogatap',
    'contact_name': 'Ana García',
    'phone': '600123456',
    'email': 'ana@test.com',
    'service_1_title': 'Derecho civil',
    'service_1_description': 'Asesoría en contratos',
}


# ---------------------------------------------------------------------------
# /comenzar — crear perfil
# ---------------------------------------------------------------------------

def test_crear_get(client):
    res = client.get('/comenzar')
    assert res.status_code == 200


def test_crear_sin_servicios_falla(client):
    data = {k: v for k, v in FORM_BASE.items()
            if not k.startswith('service')}
    res = client.post('/comenzar', data=data, follow_redirects=True)
    assert res.status_code == 200
    # El error aparece en el campo service_1_title del template
    assert 'al menos un servicio'.encode('utf-8') in res.data
    # No redirigió a /resultado — el form se re-renderizó
    assert b'Crear mi perfil y QR' in res.data


def test_crear_ok_redirige_a_resultado(client, db):
    res = client.post('/comenzar', data=FORM_BASE)
    assert res.status_code == 302
    assert '/resultado/' in res.headers['Location']


def test_crear_ok_guarda_en_bd(client, db):
    from app.models.landing import LandingRequest
    client.post('/comenzar', data=FORM_BASE)
    req = LandingRequest.query.first()
    assert req is not None
    assert req.contact_name == 'Ana García'
    assert req.sector == 'abogatap'


def test_crear_ok_genera_qr(client, db):
    from app.models.landing import LandingRequest
    client.post('/comenzar', data=FORM_BASE)
    req = LandingRequest.query.first()
    assert req.qr_code is not None
    assert len(req.qr_code) > 100  # base64 PNG no está vacío


def test_crear_ok_genera_prompt(client, db):
    from app.models.landing import LandingRequest
    client.post('/comenzar', data=FORM_BASE)
    req = LandingRequest.query.first()
    assert req.generated_prompt is not None
    assert 'Ana García' in req.generated_prompt


def test_crear_guarda_servicio(client, db):
    from app.models.landing_service import LandingService
    client.post('/comenzar', data=FORM_BASE)
    svc = LandingService.query.first()
    assert svc is not None
    assert svc.title == 'Derecho civil'


def test_crear_autenticado_asocia_usuario(client, db):
    from app.models.landing import LandingRequest
    user = make_user(db)
    login(client, user.email, 'password123')
    client.post('/comenzar', data=FORM_BASE)
    req = LandingRequest.query.first()
    assert req.user_id == user.id


# ---------------------------------------------------------------------------
# /resultado/<slug>
# ---------------------------------------------------------------------------

def test_resultado_ok(client, db):
    req = make_landing(db)
    res = client.get(f'/resultado/{req.public_slug}')
    assert res.status_code == 200


def test_resultado_slug_inexistente_404(client):
    res = client.get('/resultado/slug-que-no-existe')
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# /mis-landings
# ---------------------------------------------------------------------------

def test_mis_landings_requiere_login(client):
    res = client.get('/mis-landings')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_mis_landings_ok(client, db):
    user = make_user(db)
    login(client, user.email, 'password123')
    res = client.get('/mis-landings')
    assert res.status_code == 200


def test_mis_landings_solo_muestra_los_propios(client, db):
    user = make_user(db)
    otro = make_user(db, email='otro@test.com')
    make_landing(db, user=user, business_name='Mi negocio')
    make_landing(db, user=otro, business_name='Negocio ajeno')

    login(client, user.email, 'password123')
    res = client.get('/mis-landings')
    assert b'Mi negocio' in res.data
    assert b'Negocio ajeno' not in res.data


# ---------------------------------------------------------------------------
# /mis-landings/<id> — detalle
# ---------------------------------------------------------------------------

def test_detail_requiere_login(client, db):
    req = make_landing(db)
    res = client.get(f'/mis-landings/{req.id}')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']


def test_detail_ok(client, db):
    user = make_user(db)
    req = make_landing(db, user=user)
    login(client, user.email, 'password123')
    res = client.get(f'/mis-landings/{req.id}')
    assert res.status_code == 200
    assert req.business_name.encode() in res.data


def test_detail_otro_usuario_404(client, db):
    user = make_user(db)
    otro = make_user(db, email='otro@test.com')
    req = make_landing(db, user=otro)
    login(client, user.email, 'password123')
    res = client.get(f'/mis-landings/{req.id}')
    assert res.status_code == 404


def test_detail_sin_usuario_asignado_404(client, db):
    """Un LandingRequest anónimo no debe ser visible desde el detalle de usuario."""
    user = make_user(db)
    req = make_landing(db, user=None)
    login(client, user.email, 'password123')
    res = client.get(f'/mis-landings/{req.id}')
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# /p/<slug> — vista pública del QR
# ---------------------------------------------------------------------------

def test_public_view_ok(client, db):
    req = make_landing(db)
    res = client.get(f'/p/{req.public_slug}')
    assert res.status_code == 200


def test_public_view_slug_inexistente_404(client):
    res = client.get('/p/slug-inventado')
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# /p/<slug>/contactar — captura de lead
# ---------------------------------------------------------------------------

def test_contact_ok(client, db):
    req = make_landing(db)
    res = client.post(f'/p/{req.public_slug}/contactar', data={
        'service_id': '0',
        'name': 'María López',
        'email': 'maria@test.com',
        'phone': '611222333',
        'message': 'Me interesa el servicio',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Gracias' in res.data


def test_contact_guarda_en_bd(client, db):
    from app.models.contact import Contact
    req = make_landing(db)
    client.post(f'/p/{req.public_slug}/contactar', data={
        'service_id': '0',
        'name': 'Pedro Ruiz',
    }, follow_redirects=True)
    contact = Contact.query.filter_by(request_id=req.id).first()
    assert contact is not None
    assert contact.name == 'Pedro Ruiz'


def test_contact_sin_nombre_no_guarda(client, db):
    from app.models.contact import Contact
    req = make_landing(db)
    res = client.post(f'/p/{req.public_slug}/contactar', data={
        'service_id': '0',
        'name': '',
    }, follow_redirects=True)
    assert res.status_code == 200
    assert Contact.query.count() == 0
    assert b'nombre' in res.data.lower()
