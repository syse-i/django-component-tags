from . import Library
from .components import Slot
from .media import media_tag

"""
Builtin tags 

* Slot: can be used inside any other component, therefore it can be pre-loaded inside django.
* components_css: import css scripts from rendered components 
* components_js: import js scripts from rendered components 
"""
register = Library()

register.tag('slot', Slot)
register.tag("components_css", media_tag("css"))
register.tag("components_js", media_tag("js"))
