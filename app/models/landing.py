import secrets
from datetime import datetime, timezone
from app.extensions import db


def generate_slug():
    return secrets.token_urlsafe(8)  # 11 chars, URL-safe


class LandingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    public_slug = db.Column(db.String(16), unique=True, nullable=False, default=generate_slug)
    landing_type = db.Column(db.String(3), nullable=False, default='b2c')  # 'b2b' or 'b2c'
    sector = db.Column(db.String(20), nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    # B2B contact fields
    contact_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    linkedin = db.Column(db.String(200), nullable=True)
    website = db.Column(db.String(200), nullable=True)

    generated_prompt = db.Column(db.Text, nullable=True)
    generated_html = db.Column(db.Text, nullable=True)
    qr_code = db.Column(db.Text, nullable=True)  # base64 PNG
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('landing_requests', lazy=True))
    services = db.relationship('LandingService', backref='request', lazy=True,
                               order_by='LandingService.order')
    contacts = db.relationship('Contact', backref='request', lazy=True)
    availability = db.relationship('Availability', backref='request', lazy=True,
                                   order_by='Availability.day_of_week')
    appointments = db.relationship('Appointment', backref='request', lazy=True)

    @property
    def is_b2b(self):
        return self.landing_type == 'b2b'

    def __repr__(self):
        return f'<LandingRequest {self.id} - {self.landing_type}/{self.sector}>'
