'''
Created on Mar 30, 2014

@author: Steve Cassidy
'''
import os

from mock import list_images
from templating import render


MIME_TABLE = {'.txt': 'text/plain',
              '.html': 'text/html',
              '.css': 'text/css',
              '.js': 'application/javascript',
}

STATIC_URL_PREFIX = '/static/'
STATIC_FILE_DIR = 'static/'


def content_type(path):
    """Return a guess at the mime type for this path
    based on the file extension"""

    name, ext = os.path.splitext(path)

    if ext in MIME_TABLE:
        return MIME_TABLE[ext]
    else:
        return "application/octet-stream"


def render_template(template_name, template_mapping, title):
    base_mapping = {
        'title': title,
        'navigation': render('includes/navigation.html', template_mapping)[0].decode(),
        'body': render(template_name, template_mapping)[0].decode(),
    }
    return render('base.html', base_mapping)


def flowtow_app(environ, start_response):
    start_response("200 OK", [('content-type', 'text/html')])
    mapping = {
        'content': '<p>Hello World!</p>',
    }
    # routing
    if environ['PATH_INFO'] == '/about':
        return render_template('about.html', mapping, 'FlowTow - About Us')
    else:
        return render_template('index.html', mapping, 'Flowtow - Home')


def static_app(environ, start_response):
    """Serve static files from the directory named
    in STATIC_FILES"""

    path = environ['PATH_INFO']
    # we want to remove '/static' from the start
    path = path.replace(STATIC_URL_PREFIX, STATIC_FILE_DIR)

    # normalise any .. elements in path
    path = os.path.normpath(path)

    if path.startswith(STATIC_FILE_DIR) and os.path.exists(path):
        h = open(path, 'rb')
        content = h.read()
        h.close()

        headers = [('content-type', content_type(path))]
        start_response('200 OK', headers)
        return [content]


def application(environ, start_response):
    """Main WSGI Application for FlowTow"""
    if environ['PATH_INFO'].startswith(STATIC_URL_PREFIX):
        return static_app(environ, start_response)
    else:
        return flowtow_app(environ, start_response)


if __name__ == '__main__':
    from wsgiref import simple_server

    server = simple_server.make_server('localhost', 8000, application)
    print("listening on http://localhost:8000/ ...")
    server.serve_forever()

