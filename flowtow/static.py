import os

MIME_TABLE = {
    '.txt': 'text/plain',
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
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
