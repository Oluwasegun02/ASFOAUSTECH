from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def url(view_name, *args, **kwargs):
    return reverse(view_name, args=args, kwargs=kwargs)


def environment(**options):
    # Django passes 'context_processors' and 'debug' into this function, 
    # but the Jinja2 Environment constructor does not accept them as arguments.
    options.pop('context_processors', None)
    options.pop('debug', None)
    
    env = Environment(**options)
    env.globals.update(
        {
            "static": static,
            "url": url,
        }
    )
    return env
