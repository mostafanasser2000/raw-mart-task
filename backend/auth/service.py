from datetime import datetime, timezone

from flask_jwt_extended import decode_token
from sqlalchemy.orm.exc import NoResultFound

from backend.extensions import db
from backend.models import TokenBlocklist, User


def add_token_to_database(encoded_token, identity_claim):
    decoded_token = decode_token(encoded_token)
    db_token = TokenBlocklist(
        jti=decoded_token["jti"],
        token_type=decoded_token["type"],
        user_id=decoded_token[identity_claim],
        expires=datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc),
        revoked=False,
    )
    db.session.add(db_token)
    db.session.commit()


def is_token_revoked(jwt_payload):
    try:
        token = TokenBlocklist.query.filter_by(jti=jwt_payload["jti"]).one()
        return token.revoked
    except NoResultFound:
        return True


def revoke_token(token_jti, user):
    try:
        token = TokenBlocklist.query.filter_by(jti=token_jti, user_id=user).one()
        token.revoked = True
        db.session.commit()
    except NoResultFound:
        raise ValueError(f"Token {token_jti} not found")


def create_user(name: str, email: str, password: str):
    email = email.lower()
    if User.query.filter_by(email=email).first():
        raise ValueError("User with this email already exists")
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def get_user(email: str):
    return User.query.filter_by(email=email.lower()).first()


def revoke_all_user_tokens(user_id: int):
    TokenBlocklist.query.filter_by(user_id=user_id, revoked=False).update(
        {"revoked": True}
    )
    db.session.commit()
