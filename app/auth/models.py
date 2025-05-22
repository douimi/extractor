import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager

class User(UserMixin):
    def __init__(self, username, password_hash, role):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.role = role

    @staticmethod
    def get(username):
        try:
            with open('app/auth/users.json', 'r') as f:
                users = json.load(f)
                if username in users:
                    user_data = users[username]
                    return User(
                        username=username,
                        password_hash=user_data['password'],
                        role=user_data['role']
                    )
        except FileNotFoundError:
            return None
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def create_password_hash(password):
        return generate_password_hash(password) 