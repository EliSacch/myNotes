import os
import urllib.parse as up
import psycopg2
from sqlalchemy import (
    func, Column, Float, ForeignKey, Integer, String
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from creds import database_credentials

db = database_credentials()
Base = declarative_base()

# Create a class-based model for the "Note" database
class Note(Base):
    __tablename__ = "Note"
    NoteId = Column(Integer, primary_key=True)
    Title = Column(String)
    Content = Column(ARRAY(String),nullable=False)


# Create a new instance of sessionamaker, then point to our engine
Session = sessionmaker(db)
# Open an actual session by calling the subclass defined above
session = Session()


# Creating the database using the declative_base subclass
Base.metadata.create_all(db)

# Create records in our database
new_note = Note(
    Title = "First note",
    Content = ["Text note random"]
)


# Add each instance of our Note into the session
session.add(new_note)


# Commit our session to the database
session.commit()


# Query the database
notes = session.query(Note)
for note in notes:
    print(
        note.NoteId,
        note.Title + " | ",
        note.Content
    )
