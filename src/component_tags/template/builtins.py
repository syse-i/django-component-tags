from . import Library
from .components import Slot

register = Library()

register.tag('slot', Slot)
