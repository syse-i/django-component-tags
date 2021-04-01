from django import template
from django.forms.widgets import Media
from django.template import Context

"""
Copyright (c) 2015 Jérôme Bon

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation 
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial 
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED 
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
DEALINGS IN THE SOFTWARE.

For more information about this: 

https://gitlab.com/Mojeer/django_components

"""


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
