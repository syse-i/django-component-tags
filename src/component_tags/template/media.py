from django import template
from django.forms.widgets import Media
from django.template import Context

MEDIA_CONTEXT_KEY = "__django_component__media"


def media_tag(media_type):
    def media(parser, token):
        nodelist = parser.parse()
        return MediaNode(media_type, nodelist)

    return media


def ensure_media_context(root_context: dict):
    if MEDIA_CONTEXT_KEY not in root_context:
        root_context[MEDIA_CONTEXT_KEY] = Media()


def add_media(context: Context, media):
    root_context = context.dicts[0]
    ensure_media_context(root_context)
    root_context[MEDIA_CONTEXT_KEY] += media


class MediaNode(template.Node):
    def __init__(self, media_type, nodelist):
        self.media_type = media_type
        self.nodelist = nodelist

    def render(self, context):
        rendered = self.nodelist.render(context)
        return self.render_media(context) + rendered

    def render_media(self, context):
        tags = []
        if MEDIA_CONTEXT_KEY in context:
            media = context[MEDIA_CONTEXT_KEY]
            if self.media_type == "css":
                tags = media.render_css()
            elif self.media_type == "js":
                tags = media.render_js()
        return "".join(tags)
