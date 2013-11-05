import tornado.web
import passlib.hash

from lib import db

from lib.utils import (
  get_user,
  create_token,
  verify_hash,
  generate_password
)

class Create(tornado.web.RequestHandler):
  SUPPORTED_METHODS = ('POST')

  def post(self):
    username    = self.get_argument("username"   , default=None, strip=False)
    email       = self.get_argument("email"      , default=None, strip=False)
    password    = self.get_argument("password"   , default=None, strip=False)

    cursor = db.conn.execute("""
      INSERT INTO Users
        (username, email, hash_scheme, passhash)
      VALUES
        (?, ?, ?, ?)
      """, (username, email, "sha256_crypt", passlib.hash.sha256_crypt.encrypt(password))
    )
    db.conn.commit()

    # TODO potential race condition if tornado is multithreaded
    token = create_token(cursor.lastrowid)
    self.write(token)


class CreateShortKey(tornado.web.RequestHandler):
  SUPPORTED_METHODS = ('POST')

  def post(self):
    token = self.get_argument("token", default=None, strip=False)

    cursor = db.conn.execute("""
      INSERT INTO Users
        (username, email, hash_scheme, passhash)
      VALUES
        (?, ?, ?, ?)
      """, (username, email, "sha256_crypt", passlib.hash.sha256_crypt.encrypt(password))
    )
    db.conn.commit()

    # TODO potential race condition if tornado is multithreaded
    token = create_token(cursor.lastrowid)
    self.write(token)

global FAIL_PASSHASH
# Create a hash to verify against if non existant user
FAIL_PASSHASH = passlib.hash.sha256_crypt.encrypt(generate_password(64))

class Login(tornado.web.RequestHandler):
  SUPPORTED_METHODS = ('POST')

  def post(self):
    global FAIL_PASSHASH
    username = self.get_argument("username", default=None, strip=False)
    password = self.get_argument("password", default=None, strip=False)

    cursor = db.conn.execute("""
      SELECT 
        id,
        hash_scheme, 
        passhash 
      FROM 
        Users 
      WHERE 
        username=?
    """, (username,))

    r = cursor.fetchone()
    if not r:
      # To simplify code path
      user_id, hash_scheme, passhash = (0, "sha256_crypt", FAIL_PASSHASH)
    else:
      user_id, hash_scheme, passhash = r

    if verify_hash(password, passhash, hash_scheme):
      token = create_token(user_id)
      self.write(token)
    else:
      self.set_status(401)
