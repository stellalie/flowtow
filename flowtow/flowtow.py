import cgi
import html
import os
from database import COMP249Db
from flowtow.template import render_plain, render_template
from interface import list_images, add_comment, list_images_for_user, list_only_images, list_comments, add_image
from users import user_from_cookie, check_login, generate_session, COOKIE_NAME, delete_session

db = COMP249Db()


def render_comment_list(comment_list):
    result = ""
    for comment in comment_list:
        result += render_plain('includes/comment_item.html', dict(comment=comment))
    return result


def render_image_list(listing):
    result = ""
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


def page_my_images(environ, start_response):
    logged_user = user_from_cookie(db, environ)
    if logged_user:
        template_mapping = dict(image_list_for_user=render_image_list(list_images_for_user(db, logged_user)))
        return render_page(environ, 'my_images.html', 'Flowtow - My Images', template_mapping)
    return page_404(start_response)


def page_index(environ):
    template_mapping = dict(image_list=render_image_list(list_only_images(db, 3)))
    return render_page(environ, 'index.html', 'Flowtow - Home', template_mapping)


def page_about(environ):
    return render_page(environ, 'about.html', 'FlowTow - About Us', {})


def page_404(start_response):
    """An application that always returns
    a 404 response"""
    page_404 = """<html>
    <h1>Page not Found</h1>
    <p>That page is unknown. Return to the <a href="/">Flowtow</a> home</p>
    </html>
    """
    headers = [('content-type', 'text/html')]
    start_response('404 Not Found', headers)
    return [page_404.encode(), ]


def action_comment(environ):
    form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    if 'image' in form and 'comment' in form:
        add_comment(db, form.getvalue('image'), html.escape(form.getvalue('comment')))


def action_upload(environ):
    form = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
    logged_user = user_from_cookie(db, environ)
    if logged_user and 'image' in form and form['image'].filename != '':
        file_data = form['image'].file.read()
        filename = form['image'].filename
        # write the content of the uploaded file to a local file
        target = os.path.join('static/images', filename)
        f = open(target, 'wb')
        f.write(file_data)
        f.close()
        add_image(db, filename, logged_user)


def flowtow_app(environ, start_response):
    headers = [('content-type', 'text/html')]

    # about page
    if environ['PATH_INFO'] == '/about':
        start_response("200 OK", headers)
        return page_about(environ)
    # action comment
    elif environ['PATH_INFO'] == '/comment':
        action_comment(environ)
        headers.append(('location', '/'))
        start_response("303 See Other", headers)
        return page_index(environ)
    # action upload
    elif environ['PATH_INFO'] == '/upload':
        action_upload(environ)
        start_response("200 OK", headers)
        return page_my_images(environ, start_response)
    # action login
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
                return page_index(environ)
        headers.append(('location', '/?login_failed'))
        start_response("303 See Other", headers)
        return page_index(environ)
    # action logout
    elif environ['PATH_INFO'] == '/logout':
        logged_user = user_from_cookie(db, environ)
        if logged_user:
            delete_session(db, logged_user)
        headers.append(('location', '/'))
        start_response("303 See Other", headers)
        return page_index(environ)
    # my images
    elif environ['PATH_INFO'] == '/my_images':
        start_response("200 OK", headers)
        return page_my_images(environ, start_response)
    # index page
    elif environ['PATH_INFO'] == '/':
        start_response("200 OK", headers)
        return page_index(environ)
    # 404
    else:
        return page_404(start_response)
