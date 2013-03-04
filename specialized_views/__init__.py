from django.template.response import TemplateResponse
from functools import wraps


def parse_accept_header(accept):
    result = []
    for media_range in accept.split(","):
        parts = media_range.split(";")
        media_type = parts.pop(0).strip()
        media_params = []
        typ, subtyp = media_type.split('/')
        q = 1.0
        for part in parts:
            (key, value) = part.lstrip().split("=", 1)
            key = key.strip()
            value = value.strip()
            if key == "q":
                q = float(value)
            else:
                media_params.append((key, value))
        result.append((media_type, dict(media_params), q))
    result.sort(lambda x, y: -cmp(x[2], y[2]))
    return result


def find_best_type(accept_header, mime_handlers):
    accepted = parse_accept_header(accept_header)
    for mime_type, params, q in accepted:
        if mime_type in mime_handlers:
            return mime_handlers[mime_type], params


def render_to_response(request, response, **kwargs):
    template = response.pop('template')
    return TemplateResponse(request, template, response)


def view(fun):
    @wraps(fun)
    def wrapped(request, **kwargs):
        response = fun(request, **kwargs)
        spec, params = find_best_type(request.META['HTTP_ACCEPT'],
                                      wrapped.mime_handlers)
        if spec:
            kwargs = dict(kwargs, media_params=params)
            return spec(request, response, **kwargs)
        if request.is_ajax() and wrapped.ajax_handler:
            return wrapped.ajax_handler(request, response, **kwargs)
        return wrapped.default_handler(request, response)

    def default(fun):
        wrapped.default_handler = fun
        return fun

    def for_ajax(fun):
        wrapped.ajax_handler = fun
        return fun

    def for_mime(mime_type):
        def decorator(fun):
            wrapped.mime_handlers[mime_type] = fun
            return fun
        return decorator

    wrapped.ajax_handler = None
    wrapped.mime_handlers = {}
    wrapped.default_handler = render_to_response
    wrapped.default = default
    wrapped.for_ajax = for_ajax
    wrapped.for_mime = for_mime
    return wrapped
