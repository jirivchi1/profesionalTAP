from datetime import datetime, timezone
from app.extensions import db


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True)
    landing_request_id = db.Column(db.Integer, db.ForeignKey('landing_request.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('landing_service.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(5), nullable=False)   # "09:00"
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending / confirmed / cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    service = db.relationship('LandingService', backref='appointments', lazy=True)

    def __repr__(self):
        return f'<Appointment {self.id} {self.name} {self.date} {self.time}>'
