import json
from datetime import datetime

from app.extensions import db


class Note(db.Model):
    __tablename__ = "Notes"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    content_json = db.Column(db.Text, default='[]')
    owner_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False, index=True)
    owner = db.relationship("User", back_populates="notes")
    dashboard_id = db.Column(db.Integer, db.ForeignKey("Dashboards.id"), nullable=False, index=True)
    dashboard = db.relationship("Dashboard", back_populates="notes")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def formatted_updated_at(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M")

    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    @property
    def content_blocks(self):
        try:
            blocks = json.loads(self.content_json or "[]")
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
        if not isinstance(blocks, list):
            return []
        return blocks

    @property
    def content_text(self):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else ""
            for block in self.content_blocks
        )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content_json": self.content_json,
            "content_blocks": self.content_blocks,
            "content_text": self.content_text,
            "created_at": self.formatted_created_at,
            "updated_at": self.formatted_updated_at,
        }

    def __repr__(self):
        return f"<Note {self.id}>"
