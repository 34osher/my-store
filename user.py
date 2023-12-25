from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from bson.objectid import ObjectId

# MongoDB setup
client = MongoClient('mongodb://osher:123456@mongo:27017/')
db = client['mydatabase']
users_col = db['users']

class User:
    def __init__(self, email, password_hash=None, is_admin=False, _id=None):
        self.email = email
        self.password_hash = password_hash
        self.is_admin = is_admin
        self._id = _id

    @classmethod
    def find_by_email(cls, email):
        data = users_col.find_one({"email": email})
        if data:
            return cls(**data)

    @classmethod
    def find_by_id(cls, _id):
        data = users_col.find_one({"_id": ObjectId(_id)})
        if data:
            return cls(**data)

    def save_to_db(self):
        users_col.insert_one(self.json())

    def json(self):
        return {
            "email": self.email,
            "password_hash": self.password_hash,
            "is_admin": self.is_admin
        }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
