import hashlib
from db import db

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)  # New column for image descriptions
    hash = db.Column(db.String(64), unique=True)  # New column for image content hash

    def __init__(self, img, name, mimetype, description=None):
        self.img = img
        self.name = name
        self.mimetype = mimetype
        self.description = description
        self.hash = self.compute_hash(img)

    @staticmethod
    def compute_hash(data):
        """Compute the SHA-256 hash of data."""
        hasher = hashlib.sha256()
        hasher.update(data)
        return hasher.hexdigest()
