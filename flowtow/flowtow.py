import cgi
from database import COMP249Db
from flowtow.template import render_plain, render_template
from interface import list_images, add_comment

db = COMP249Db()


def render_comment_list(comment_list):
    result = ""
    for comment in comment_list:
        result += render_plain('includes/comment_item.html', dict(comment=comment))
    return result


def render_image_list(n):
    result = ""
    for image in list_images(db, n):
        image_mapping = {
            'image': image[0],
            'date': image[1],
            'useremail': image[2],
            'comments': render_comment_list(image[3])
        }
        result += render_plain('includes/image_item.html', image_mapping)
    return result


def index():
    return render_template('index.html', dict(image_list=render_image_list(3)), 'Flowtow - Home')


def flowtow_app(environ, start_response):
    # routing
    headers = ('content-type', 'text/html')
    if environ['PATH_INFO'] == '/about':
        start_response("200 OK", [headers])
        return render_template('about.html', None, 'FlowTow - About Us')
    elif environ['PATH_INFO'] == '/comment':
        form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        if 'image' in form and 'comment' in form:
            add_comment(db, form.getvalue('image'), cgi.escape(form.getvalue('comment')))
        start_response("303 See Other", [headers, ('location', '/')])
        return index()
    else:
        start_response("200 OK", [headers])
        return index()