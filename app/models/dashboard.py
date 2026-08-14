import re
from datetime import datetime

from app.extensions import db


class Dashboard(db.Model):
    __tablename__ = "Dashboards"
    __table_args__ = (
        db.UniqueConstraint("owner_id", "name", name="uq_dashboards_owner_id_name"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False, index=True)
    is_default = db.Column(db.Boolean, nullable=False, default=False)
    notes = db.relationship("Note", back_populates="dashboard", cascade="all, delete-orphan")
    owner = db.relationship("User", back_populates="dashboards")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def slug(self):
        slug = re.sub(r"[^a-z0-9]+", "-", self.name.casefold()).strip("-")
        return slug or "dashboard"

    @property
    def formatted_updated_at(self):
        return self.updated_at.strftime("%Y-%m-%d %H:%M")

    @property
    def formatted_created_at(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "is_default": self.is_default,
            "created_at": self.formatted_created_at,
            "updated_at": self.formatted_updated_at,
        }

    def __repr__(self):
        return f"<Dashboard {self.id}>"
