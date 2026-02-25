from app.extensions import db


class Availability(db.Model):
    __tablename__ = 'availability'

    id = db.Column(db.Integer, primary_key=True)
    landing_request_id = db.Column(db.Integer, db.ForeignKey('landing_request.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Lunes … 6=Domingo
    start_time = db.Column(db.String(5), nullable=False, default='09:00')
    end_time = db.Column(db.String(5), nullable=False, default='18:00')
    slot_minutes = db.Column(db.Integer, default=60)

    def __repr__(self):
        return f'<Availability req={self.landing_request_id} day={self.day_of_week}>'
