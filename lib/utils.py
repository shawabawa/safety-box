from passlib.utils import generate_password
from collections import namedtuple

from datetime import datetime, timedelta
import string
import math
import passlib.hash

from lib import db

def verify_hash(password, passhash, hash_scheme="sha256_crypt"):
  hasher = getattr(passlib.hash, hash_scheme, passlib.hash.sha256_crypt)
  return hasher.verify(password, passhash)

token_length = 64
def create_token(user_id, duration=None):
  if duration is None:
    duration = timedelta(minutes=5)

  token = generate_password(token_length)

  db.conn.execute("""
    INSERT INTO Sessions
      (token, user_id, duration, last_accessed)
    VALUES
      (?, ?, ?, ?)
    """, (token, user_id, duration.seconds, datetime.now())
  )
  db.conn.commit()

  return token

def get_user(token):
  User = namedtuple('User', ['user_id', 'username'])

  cursor = db.conn.execute("""
    SELECT
      u.id,
      u.username,
      s.duration,
      s.last_accessed
    FROM
      Sessions s
    JOIN 
      Users u ON s.user_id = u.id 
    WHERE
      s.token = ?
  """, (token,))

  r = cursor.fetchone()

  if not r:
    return None

  cursor = db.conn.execute("""
    UPDATE Sessions
    SET last_accessed = ?
    WHERE token = ?
  """, (datetime.now(), token))

  return User(r[0], r[1])