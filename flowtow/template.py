from templating import render


def render_plain(template_name, template_mapping):
    return render(template_name, template_mapping)[0].decode()


def render_template(template_name, template_mapping, title):
    base_mapping = {
        'title': title,
        'navigation': render_plain('includes/navigation.html', template_mapping),
        'body': render_plain(template_name, template_mapping),
    }
    return render('base.html', base_mapping)