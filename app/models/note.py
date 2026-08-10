from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class Note(db.Model):
    __tablename__ = "Notes"

    id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(50))
    Content = db.Column(db.Text)
    OwnerId = db.Column(db.Integer, db.ForeignKey("Users.id"))
    Owner = db.relationship("User", back_populates="notes")
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def formatted_created_at(self):
        return self.CreatedAt.strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "Id": self.id,
            "Title": self.Title,
            "Content": self.Content,
            "CreatedAt": self.formatted_created_at,
        }

    def __repr__(self):
        return f"<Note {self.id}>"
