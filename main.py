'''
Created on Mar 30, 2014

@author: Steve Cassidy
'''
from flowtow.static import static_app, STATIC_URL_PREFIX
from flowtow.flowtow import flowtow_app


def application(environ, start_response):
    """Main WSGI Application for FlowTow"""

    if environ['PATH_INFO'].startswith(STATIC_URL_PREFIX):
        return static_app(environ, start_response)
    else:
        return flowtow_app(environ, start_response)


if __name__ == '__main__':
    from wsgiref import simple_server
    import database

    db = database.COMP249Db()
    db.create_tables()
    db.sample_data()

    server = simple_server.make_server('localhost', 8000, application)
    print("listening on http://localhost:8000/ ...")
    server.serve_forever()

