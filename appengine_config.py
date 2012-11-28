import datetime 

from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
     app = SessionMiddleware(app, cookie_key="1miyg9r4n3achza5s9jkdwa9t3khwu97", lifetime=datetime.timedelta(days=31))
     return app