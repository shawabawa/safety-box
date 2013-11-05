import os
import sys
import unittest

import tornado
from tornado.testing import AsyncHTTPTestCase, LogTrapTestCase
import tornado.testing

sys.path.insert(0,os.path.abspath(__file__+"/../.."))
import lib.db
from lib import utils

def login_as(username, password):

  def wrapper(func):
    def inner_wrapper(self, *args, **kwargs):
      def handle(response):
        self.token = response.body.decode("utf-8")
        self.login_response = response
        self.stop()

      result = self.http_client.fetch(
        self.get_url("/login"), 
        handle, 
        method="POST",
        body="username={}&password={}".format(username, password))

      self.wait()
      ret = func(self, *args, **kwargs)

      return ret
    return inner_wrapper

  return wrapper


class BasicTest(AsyncHTTPTestCase, LogTrapTestCase):
  def get_app(self):
    from safety_box import safety_box
    return safety_box

  def setUp(self):
    super().setUp()

  def test_0_index(self):
    def handle(response):
      self.assertEqual(response.code, 200)
      self.stop()

    result = self.http_client.fetch(self.get_url("/"), handle)
    self.wait()

  def test_1_create(self):
    def handle(response):
      self.assertEqual(response.code, 200)
      self.stop()

    result = self.http_client.fetch(
      self.get_url("/create"), 
      handle, 
      method="POST",
      body="username=testuser&password=testpass&email=test@test.com")

    self.wait()

  @login_as("testuser", "testpass")
  def test_2_login(self):
     self.assertEqual(self.login_response.code, 200)

  @login_as("testuser", "testpass2")
  def test_2a_login_fail_wrong_pass(self):
     self.assertEqual(self.login_response.code, 401)

  @login_as("testuser2", "testpass2")
  def test_2b_login_fail_no_user(self):
     self.assertEqual(self.login_response.code, 401)

  @login_as("testuser", "testpass")
  def test_3_get_token(self):
    user = utils.get_user(self.token)
    self.assertNotEqual(user, None)
    self.assertEqual(user.username, "testuser")



if __name__ == "__main__":
  lib.db.init("testdb.sqlite")

  try:
    unittest.main(verbosity=2)
  finally:
    lib.db.conn.close()
    os.unlink("testdb.sqlite")
