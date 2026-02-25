"""Business logic for LandingRequest creation and management."""
import io
import os
import base64

import qrcode

_SECTORS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sectors')


def generate_qr(url: str) -> str:
    """Generate a QR code for *url* and return it as a base64-encoded PNG string."""
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def build_prompt(req, services: list) -> str:
    """Build the AI generation prompt for *req* using the sector's prompt.txt template.

    *services* is the list of LandingService objects (or any object with .title / .description)
    that were saved alongside the request — passed explicitly to avoid relying on lazy-loaded
    SQLAlchemy relationships before the session is committed.

    Returns an empty string if the sector template is not found.
    """
    prompt_path = os.path.join(_SECTORS_DIR, req.sector, 'prompt.txt')
    try:
        with open(prompt_path, encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        return ''

    # Build description from saved services when available
    if services:
        lines = [
            f"- {s.title}: {s.description or 'Sin descripción'}"
            for s in services
        ]
        descripcion = 'Servicios ofrecidos:\n' + '\n'.join(lines)
    else:
        descripcion = req.description or ''

    ubicacion = req.location or req.website or ''

    return template.format(
        nombre=req.business_name or req.contact_name or '',
        descripcion=descripcion,
        ubicacion=ubicacion,
    )
