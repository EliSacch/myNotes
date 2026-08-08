from datetime import datetime

from sqlalchemy.dialects.postgresql import ARRAY

from app.extensions import db


class Note(db.Model):
    __tablename__ = "Notes"

    NoteId = db.Column(db.Integer, primary_key=True)
    IsList = db.Column(db.Boolean, default=True)
    Title = db.Column(db.String(50))
    Content = db.Column(ARRAY(db.JSON))
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "Id": self.NoteId,
            "List": self.IsList,
            "Title": self.Title,
            "Content": self.Content,
        }
