import os
import urllib.parse as up
import psycopg2
from sqlalchemy import (
    inspect, func, Column, Float, ForeignKey, Integer, String, Boolean, JSON
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from creds import database_credentials

db = database_credentials()
Base = declarative_base()

# Create a class-based model for the "Note" database
class Note(Base):
    __tablename__ = "Notes"
    NoteId = Column(Integer, primary_key=True)
    IsList = Column(Boolean, unique=False, default=True)
    Title = Column(String)
    Content = Column(ARRAY(JSON))


# Create a new instance of sessionamaker, then point to our engine
Session = sessionmaker(db)
# Open an actual session by calling the subclass defined above
session = Session()


# Creating the database using the declative_base subclass
Base.metadata.create_all(db)

# Create records in our database
new_note = Note(
    Title = "First note",
    IsList = True,
    Content = [
        {
            "checked": False,
            "content": "Test test test"
        }
    ]
)


# Add each instance of our Note into the session
session.add(new_note)


# Commit our session to the database
session.commit()


# Query the database
notes = session.query(Note)

def get_notes():
    inspector = inspect(db.engine)
    if inspector.has_table("Notes") == True:
        results = []

        for note in notes:
            new = {
                "Id": note.NoteId,
                "List": note.IsList,
                "Title": note.Title,
                "Content": note.Content
            }
            results.append(new) 

        return results
    else:
        print('error')
        return None