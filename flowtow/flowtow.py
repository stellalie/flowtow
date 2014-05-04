import cgi
from database import COMP249Db
from flowtow.template import render_plain, render_template
from interface import list_images, add_comment, list_images_for_user, list_only_images, list_comments
from users import user_from_cookie, check_login, generate_session, COOKIE_NAME, delete_session

db = COMP249Db()


def render_comment_list(comment_list):
    result = ""
    for comment in comment_list:
        result += render_plain('includes/comment_item.html', dict(comment=comment))
    return result


def render_image_list(n, useremail=None):
    result = ""
    listing = list_images_for_user(db, useremail) if useremail else list_only_images(db, n)
    for image in listing:
        image_mapping = {
            'image': image[0],
            'date': image[1],
            'useremail': image[2],
            'comments': render_comment_list(list_comments(db, image[0]))
        }
        result += render_plain('includes/image_item.html', image_mapping)
    return result


def render_page(environ, template_name, page_title, template_mapping=()):
    logged_user = user_from_cookie(db, environ)
    if logged_user:
        template_mapping['useremail'] = logged_user
        template_mapping['account_area'] = render_plain('includes/account_details.html', template_mapping)
    else:
        template_mapping['login_error'] = ''
        if 'QUERY_STRING' in environ and environ['QUERY_STRING'].startswith('login_failed'):
            template_mapping['login_error'] = 'Login Failed, please try again'
        template_mapping['account_area'] = render_plain('includes/login_form.html', template_mapping)
    return render_template(template_name, template_mapping, page_title)


def index(environ):
    if 'QUERY_STRING' in environ and environ['QUERY_STRING'].startswith('useremail'):
        useremail = environ['QUERY_STRING'].split('=')[1]
        template_mapping = dict(image_list=render_image_list(3, useremail))
    else:
        template_mapping = dict(image_list=render_image_list(3))
    return render_page(environ, 'index.html', 'Flowtow - Home', template_mapping)


def about(environ):
    return render_page(environ, 'about.html', 'FlowTow - About Us', {})


def page_404(start_response):
    """An application that always returns
    a 404 response"""
    page_404 = """<html>
    <h1>Page not Found</h1>

    <p>That page is unknown. Return to the <a href="/">home page</a></p>
    </html>
    """
    headers = [('content-type', 'text/html')]
    start_response('404 Not Found', headers)
    return [page_404.encode(), ]


def flowtow_app(environ, start_response):
    # routing
    headers = [('content-type', 'text/html')]
    if environ['PATH_INFO'] == '/about':
        start_response("200 OK", headers)
        return about(environ)
    elif environ['PATH_INFO'] == '/comment':
        form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        if 'image' in form and 'comment' in form:
            add_comment(db, form.getvalue('image'), cgi.escape(form.getvalue('comment')))
        headers.append(('location', '/'))
        start_response("303 See Other", headers)
        return index(environ)
    elif environ['PATH_INFO'] == '/login':
        form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        if 'email' in form and 'password' in form:
            useremail = form.getvalue('email')
            can_login = check_login(db, useremail, form.getvalue('password'))
            if can_login:
                cookie = generate_session(db, useremail)
                headers.append(('Set-Cookie', cookie[COOKIE_NAME].OutputString()))
                headers.append(('location', '/'))
                start_response("303 See Other", headers)
                return index(environ)
        headers.append(('location', '/?login_failed'))
        start_response("303 See Other", headers)
        return index(environ)
    elif environ['PATH_INFO'] == '/logout':
        logged_user = user_from_cookie(db, environ)
        if logged_user:
            delete_session(db, logged_user)
        headers.append(('location', '/'))
        start_response("303 See Other", headers)
        return index(environ)
    elif environ['PATH_INFO'] == '/':
        start_response("200 OK", headers)
        return index(environ)
    else:
        return page_404(start_response)
