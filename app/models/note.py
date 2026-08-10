from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class Note(db.Model):
    __tablename__ = "Notes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False, index=True)
    owner = db.relationship("User", back_populates="notes")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def formatted_updated_at(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M")

    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.formatted_created_at,
            "updated_at": self.formatted_updated_at,
        }

    def __repr__(self):
        return f"<Note {self.id}>"
