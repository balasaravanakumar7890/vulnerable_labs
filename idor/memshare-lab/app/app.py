import os
import time
import uuid
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, render_template, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretjwtkey')

db = SQLAlchemy(app)

# -- MODELS --
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    memories = db.relationship('Memory', backref='author', lazy=True)

class Memory(db.Model):
    __tablename__ = 'memories'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content_url = db.Column(db.String(255), nullable=False)
    privacy = db.Column(db.Integer, default=0) # 0: Friends/Private, 1: Everyone/Public

# -- AUTH MIDDLEWARE --
def get_current_user():
    token = request.cookies.get('token')
    if not token:
        return None
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return User.query.get(data['user_id'])
    except:
        return None

# -- FRONTEND ROUTES --
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

# -- API ROUTES --
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get('username')).first()
    if user and bcrypt.checkpw(data.get('password').encode('utf-8'), user.password_hash.encode('utf-8')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        resp = make_response(jsonify({"message": "Logged in successfully", "username": user.username}))
        resp.set_cookie('token', token, httponly=True)
        return resp
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/feed', methods=['GET'])
def get_feed():
    memories = Memory.query.filter_by(privacy=1).all()
    result = [{"memory_id": m.id, "content_url": m.content_url, "author": m.author.username} for m in memories]
    return jsonify(result), 200

@app.route('/api/memories/upload', methods=['POST'])
def upload_memory():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    content_url = data.get('content_url')
    if not content_url:
         return jsonify({"error": "Missing content_url"}), 400
         
    new_memory = Memory(user_id=user.id, content_url=content_url, privacy=0)
    db.session.add(new_memory)
    db.session.commit()
    return jsonify({"message": "Memory uploaded successfully (Private by default)", "memory_id": new_memory.id}), 201

@app.route('/api/profile/<username>', methods=['GET'])
def get_user_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    memories_data = []
    for mem in user.memories:
        mem_dict = {
            "memory_id": mem.id,
            "privacy": mem.privacy,
            # INTENTIONAL INFORMATION DISCLOSURE: 
            # We hide the content URL if private, but we LEAK the memory_id
            "content_url": mem.content_url if mem.privacy == 1 else None
        }
        memories_data.append(mem_dict)
    return jsonify({"username": user.username, "memories": memories_data}), 200

@app.route('/api/privacy/modify', methods=['POST'])
def modify_privacy():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    memory_id = data.get('memory_id')
    new_privacy = data.get('type')

    # THE VULNERABILITY: IDOR (Insecure Direct Object Reference)
    memory = Memory.query.filter_by(id=memory_id).first()
    
    if memory:
        memory.privacy = int(new_privacy)
        db.session.commit()
        return jsonify({"message": "Privacy updated successfully"}), 200
    
    return jsonify({"error": "Memory not found"}), 404

if __name__ == '__main__':
    time.sleep(2)
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
