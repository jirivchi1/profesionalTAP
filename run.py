import click
from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()


@app.cli.command('make-admin')
@click.argument('email')
def make_admin(email):
    """Promote a user to admin. Usage: flask make-admin user@example.com"""
    user = User.query.filter_by(email=email).first()
    if not user:
        click.echo(f'Usuario no encontrado: {email}')
        return
    user.is_admin = True
    db.session.commit()
    click.echo(f'{email} ahora es administrador.')


if __name__ == '__main__':
    app.run(debug=True)
