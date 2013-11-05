import argparse
import tornado
import tornado.web

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("public/index.html")


from lib.handlers import Create, Login
safety_box = tornado.web.Application([
  ("/login", Login),
  ("/create", Create),
  # ("/auth", Auth),
  ("/", IndexHandler)
])

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument(
    '-p', 
    '--port', 
    metavar='port', 
    type=int,
    default=7999,
    help='listen on the specified port'
  )

  args = parser.parse_args()

  from lib import db
  db.init()

  safety_box.listen(args.port)
  print('Listening on port {port}'.format(port=args.port))
  iol = tornado.ioloop.IOLoop.instance()
  iol.start()