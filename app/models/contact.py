from datetime import datetime, timezone
from app.extensions import db


class Contact(db.Model):
    __tablename__ = 'contact'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('landing_request.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('landing_service.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    service = db.relationship('LandingService', backref='contacts', lazy=True)

    def __repr__(self):
        return f'<Contact {self.id} - {self.name}>'
