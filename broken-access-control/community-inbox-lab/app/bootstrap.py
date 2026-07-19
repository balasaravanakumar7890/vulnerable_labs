from datetime import datetime, timezone
import uuid

from app.app import EmailNotification, Message, User, create_app, db
from werkzeug.security import generate_password_hash


def seed_demo_data():
    if db.session.scalar(db.select(User.id).limit(1)):
        return

    users = [
        User(username="alice", email="alice@example.test", password_hash=generate_password_hash("DemoPass!23"), created_at=datetime.now(timezone.utc)),
        User(username="bruno", email="bruno@example.test", password_hash=generate_password_hash("DemoPass!23"), created_at=datetime.now(timezone.utc)),
        User(username="casey", email="casey@example.test", password_hash=generate_password_hash("DemoPass!23"), created_at=datetime.now(timezone.utc)),
    ]
    db.session.add_all(users)
    db.session.commit()
    message = Message(
        id=uuid.UUID("2c1139f1-c131-4db4-b2f1-ea5168064b4e"),
        sender_id=users[0].id,
        recipient_id=users[1].id,
        subject="Q3 partner renewal notes",
        body="The partner asked that the renewal figures remain limited to the account team until next week's review.",
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(message)
    db.session.add(EmailNotification(
        message_id=message.id,
        recipient_id=users[1].id,
        recipient_email=users[1].email,
        delivered_at=datetime.now(timezone.utc),
    ))
    db.session.commit()


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        seed_demo_data()
