from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def url(view_name, *args, **kwargs):
    return reverse(view_name, args=args, kwargs=kwargs)


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": url,
        }
    )
    return env
