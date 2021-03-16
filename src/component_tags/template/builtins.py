from . import Library
from .components import Slot

"""
Builtin tags 

* Slot: can be used inside any other component, therefore it can be pre-loaded inside django.
"""
register = Library()

register.tag('slot', Slot)
