"""Fixtures compartidas para toda la suite de tests."""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.landing import LandingRequest
from app.models.landing_service import LandingService
from app.models.contact import Contact


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SERVER_NAME = 'localhost'


@pytest.fixture
def app():
    """App Flask con BD en memoria. Se resetea entre tests."""
    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Cliente HTTP que simula el navegador."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Acceso directo a la BD de test."""
    return _db


# ---------------------------------------------------------------------------
# Helpers reutilizables
# ---------------------------------------------------------------------------

def make_user(db, email='user@test.com', password='password123', is_admin=False):
    """Crea y persiste un usuario. Devuelve la instancia."""
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        is_admin=is_admin,
    )
    db.session.add(user)
    db.session.commit()
    return user


def make_admin(db, email='admin@test.com', password='adminpass'):
    return make_user(db, email=email, password=password, is_admin=True)


def login(client, email, password):
    """Inicia sesión mediante POST y devuelve la respuesta final."""
    return client.post(
        '/login',
        data={'email': email, 'password': password},
        follow_redirects=True,
    )


def make_landing(db, user=None, sector='abogatap', business_name='Despacho Test'):
    """Crea un LandingRequest con un servicio. Devuelve la instancia."""
    req = LandingRequest(
        user_id=user.id if user else None,
        landing_type='b2b',
        sector=sector,
        business_name=business_name,
        description='',
        location='',
        contact_name='Nombre Prueba',
        phone='600000000',
        email='contacto@test.com',
    )
    db.session.add(req)
    db.session.flush()

    svc = LandingService(
        request_id=req.id,
        title='Consulta legal',
        description='Asesoría en derecho civil',
        order=0,
    )
    db.session.add(svc)
    db.session.commit()
    return req
