import sqlite3

global conn
conn = None

def init(db_name="db.sqlite"):
  global conn
  conn = sqlite3.connect(db_name)
  conn.execute("""
    CREATE TABLE IF NOT EXISTS Users
    (
      id          INTEGER PRIMARY KEY,
      username    TEXT NOT NULL UNIQUE, 
      email       TEXT NOT NULL UNIQUE, 
      hash_scheme TEXT NOT NULL, 
      passhash    TEXT NOT NULL,
      create_date DATE DEFAULT CURRENT_TIMESTAMP,
      last_login  DATE
    );
  """)

  conn.execute("""
    CREATE TABLE IF NOT EXISTS Sessions
    (
      token         TEXT PRIMARY KEY,
      user_id       INTEGER,
      duration      INTEGER,
      last_accessed DATE,
      short_hash TEXT,
      short_salt TEXT,
      short_key  TEXT,
      FOREIGN KEY(user_id) REFERENCES Users(id)
    );
  """)

  conn.execute("""
    CREATE TABLE IF NOT EXISTS Secrets
    (
      id        INTEGER PRIMARY KEY,
      user_id   INT,
      expires   DATE,
      enc_secret TEXT,
      salt       TEXT,
      FOREIGN KEY(user_id) REFERENCES Users(id)
    );
  """)

  conn.commit()