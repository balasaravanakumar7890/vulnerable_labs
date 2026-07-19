import os
import secrets
import uuid
from datetime import datetime, timezone
from functools import wraps

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(254), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)


class Message(db.Model):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("sender_id <> recipient_id", name="messages_no_self_delivery"),
    )

    id = db.Column(db.Uuid, primary_key=True)
    sender_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    sender = db.relationship("User", foreign_keys=[sender_id])
    recipient = db.relationship("User", foreign_keys=[recipient_id])


class EmailNotification(db.Model):
    __tablename__ = "email_notifications"

    id = db.Column(db.BigInteger, primary_key=True)
    message_id = db.Column(db.Uuid, db.ForeignKey("messages.id"), nullable=False, unique=True)
    recipient_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    recipient_email = db.Column(db.String(254), nullable=False)
    delivered_at = db.Column(db.DateTime(timezone=True), nullable=False)


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login", next=request.full_path))
        return view(*args, **kwargs)

    return wrapped


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def require_csrf():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not secrets.compare_digest(submitted, expected):
        abort(400, "Invalid form token.")


def valid_message_key(value):
    try:
        return uuid.UUID(value)
    except (TypeError, ValueError, AttributeError):
        return None


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "local-development-key-change-before-sharing"),
        SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=3600,
        MAX_CONTENT_LENGTH=32 * 1024,
    )
    db.init_app(app)

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def template_context():
        return {"current_user": current_user(), "csrf_token": csrf_token}

    @app.get("/")
    def home():
        return redirect(url_for("inbox" if current_user() else "login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user():
            return redirect(url_for("inbox"))
        if request.method == "POST":
            require_csrf()
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")
            user = db.session.scalar(db.select(User).filter_by(username=username))
            if user is None or not check_password_hash(user.password_hash, password):
                flash("Invalid username or password.", "error")
                return render_template("login.html"), 401
            session.clear()
            session["user_id"] = user.id
            session["csrf_token"] = secrets.token_urlsafe(32)
            session.permanent = True
            destination = request.args.get("next", "")
            if not destination.startswith("/") or destination.startswith("//"):
                destination = url_for("inbox")
            return redirect(destination)
        return render_template("login.html")

    @app.post("/logout")
    @login_required
    def logout():
        require_csrf()
        session.clear()
        flash("You have signed out.", "success")
        return redirect(url_for("login"))

    @app.get("/network/members/profile/myaccount")
    @login_required
    def profile():
        return render_template("profile.html")

    @app.get("/network/members/profile/myaccount/inbox")
    @login_required
    def inbox():
        user = current_user()
        message_key = request.args.get("MailMessageKey")
        if message_key is not None:
            key = valid_message_key(message_key)
            if key is None:
                abort(404)
            message = db.session.get(Message, key)
            if message is None:
                abort(404)
            # Intentional lab flaw: this detail route verifies authentication but not message ownership.
            return render_template("message.html", message=message)

        messages = db.session.scalars(
            db.select(Message).where(Message.recipient_id == user.id).order_by(Message.created_at.desc())
        ).all()
        return render_template("inbox.html", messages=messages)

    @app.get("/network/members/profile/myaccount/sent")
    @login_required
    def sent():
        user = current_user()
        messages = db.session.scalars(
            db.select(Message).where(Message.sender_id == user.id).order_by(Message.created_at.desc())
        ).all()
        return render_template("sent.html", messages=messages)

    @app.route("/network/members/profile/myaccount/messages/compose", methods=["GET", "POST"])
    @login_required
    def compose():
        user = current_user()
        members = db.session.scalars(db.select(User).where(User.id != user.id).order_by(User.username)).all()
        if request.method == "POST":
            require_csrf()
            recipient_name = request.form.get("recipient", "").strip().lower()
            subject = request.form.get("subject", "").strip()
            body = request.form.get("body", "").strip()
            recipient = db.session.scalar(db.select(User).filter_by(username=recipient_name))
            if recipient is None or recipient.id == user.id:
                flash("Choose a valid community member.", "error")
            elif not 1 <= len(subject) <= 120 or not 1 <= len(body) <= 5000:
                flash("Subject and message are required and exceed the allowed length.", "error")
            else:
                message = Message(
                    id=uuid.uuid4(), sender_id=user.id, recipient_id=recipient.id,
                    subject=subject, body=body, created_at=datetime.now(timezone.utc)
                )
                db.session.add(message)
                db.session.flush()
                db.session.add(EmailNotification(
                    message_id=message.id, recipient_id=recipient.id,
                    recipient_email=recipient.email, delivered_at=datetime.now(timezone.utc)
                ))
                db.session.commit()
                flash("Message sent. A recipient notification has been recorded.", "success")
                return redirect(url_for("sent"))
        return render_template("compose.html", members=members)

    return app
