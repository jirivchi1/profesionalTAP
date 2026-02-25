"""Tests unitarios para app/services/landing_service.py.

Estos tests no necesitan HTTP ni BD — prueban la lógica pura.
"""
import base64

import pytest

from app.services.landing_service import generate_qr, build_prompt


# ---------------------------------------------------------------------------
# generate_qr
# ---------------------------------------------------------------------------

def test_generate_qr_devuelve_string(app):
    with app.app_context():
        result = generate_qr('https://ejemplo.com/p/abc123')
    assert isinstance(result, str)


def test_generate_qr_es_base64_valido(app):
    with app.app_context():
        result = generate_qr('https://ejemplo.com')
    # Si no lanza excepción, es base64 válido
    decoded = base64.b64decode(result)
    # Los PNG empiezan con la firma \x89PNG
    assert decoded[:4] == b'\x89PNG'


def test_generate_qr_no_vacio(app):
    with app.app_context():
        result = generate_qr('https://ejemplo.com')
    assert len(result) > 100


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------

class _FakeLandingRequest:
    """Doble de LandingRequest para tests unitarios sin BD."""
    def __init__(self, sector, business_name='Negocio Test',
                 contact_name=None, description='', location='', website=''):
        self.sector = sector
        self.business_name = business_name
        self.contact_name = contact_name
        self.description = description
        self.location = location
        self.website = website


class _FakeService:
    def __init__(self, title, description=None):
        self.title = title
        self.description = description


def test_build_prompt_contiene_nombre_negocio(app):
    req = _FakeLandingRequest(sector='abogatap', business_name='Despacho Pérez')
    services = [_FakeService('Derecho penal', 'Defensa criminal')]
    with app.app_context():
        prompt = build_prompt(req, services)
    assert 'Despacho Pérez' in prompt


def test_build_prompt_contiene_servicio(app):
    req = _FakeLandingRequest(sector='abogatap')
    services = [_FakeService('Herencias', 'Gestión de herencias')]
    with app.app_context():
        prompt = build_prompt(req, services)
    assert 'Herencias' in prompt


def test_build_prompt_sin_servicios_no_falla(app):
    req = _FakeLandingRequest(sector='segurotap', business_name='Seguros SA')
    with app.app_context():
        prompt = build_prompt(req, [])
    assert isinstance(prompt, str)
    assert 'Seguros SA' in prompt


def test_build_prompt_sector_inexistente_devuelve_vacio(app):
    req = _FakeLandingRequest(sector='sectorfantasma')
    with app.app_context():
        prompt = build_prompt(req, [])
    assert prompt == ''


def test_build_prompt_todos_los_sectores(app):
    """Todos los sectores activos tienen su prompt.txt."""
    sectores = ['abogatap', 'segurotap', 'inmotap', 'consultortap']
    for sector in sectores:
        req = _FakeLandingRequest(sector=sector, business_name=f'Negocio {sector}')
        services = [_FakeService('Servicio principal')]
        with app.app_context():
            prompt = build_prompt(req, services)
        assert len(prompt) > 0, f'Prompt vacío para sector: {sector}'


def test_build_prompt_usa_website_como_ubicacion(app):
    req = _FakeLandingRequest(
        sector='inmotap',
        business_name='Inmobiliaria Central',
        location='',
        website='https://inmobiliaria.es',
    )
    with app.app_context():
        prompt = build_prompt(req, [])
    assert 'https://inmobiliaria.es' in prompt


def test_build_prompt_usa_location_si_disponible(app):
    req = _FakeLandingRequest(
        sector='consultortap',
        business_name='Consultores SA',
        location='Madrid, España',
        website='https://consultores.es',
    )
    with app.app_context():
        prompt = build_prompt(req, [])
    # location tiene prioridad sobre website
    assert 'Madrid' in prompt
