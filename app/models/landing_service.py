from app.extensions import db


class LandingService(db.Model):
    __tablename__ = 'landing_service'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('landing_request.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<LandingService {self.id} - {self.title}>'
