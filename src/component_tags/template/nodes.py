from copy import copy

from django.template.base import Node, NodeList

__all__ = ['ComponentNode', 'BaseComponent']

from .attributes import Attribute
from .context import ComponentContext


class TemplateIsNull(Exception):
    pass


class BaseComponent(type):
    """Metaclass for all component nodes."""
    pass


class ComponentNode(Node, metaclass=BaseComponent):
    """
    Components are used to mark up the start of an HTML element
    and they are usually enclosed in angle brackets.
    """

    TemplateIsNull = TemplateIsNull

    def __init__(self, tag_name: str, nodelist: NodeList, options: dict, slots: dict, *args,
                 isolated_context: bool = True, **kwargs):
        self.tag_name = tag_name
        self.nodelist = nodelist
        self.attrs = kwargs
        self.slots = slots
        self.options = options
        self.isolated_context = isolated_context
        # TODO: understand metaclass
        self._meta = getattr(self, 'Meta', object)

    def get_template_name(self):
        return getattr(self._meta, 'template_name', None)

    def get_template(self, context):
        template_name = self.get_template_name()

        if not template_name:
            raise self.TemplateIsNull('Template is undefined')

        return context.template.engine.get_template(template_name)

    def get_context_data(self, context):
        return ComponentContext(self.nodelist, initial=context, isolated=self.isolated_context)

    def render(self, context):
        template = self.get_template(context)

        # Does this quack like a Template?
        if not callable(getattr(template, 'render', None)):
            # If not, try the cache and select_template().
            template_name = template or ()
            if isinstance(template_name, str):
                template_name = (template_name,)
            else:
                template_name = tuple(template_name)
            cache = context.render_context.dicts[0].setdefault(self, {})
            template = cache.get(template_name)

            if template is None:
                template = context.template.engine.select_template(template_name)
                cache[template_name] = template

        # Use the base.Template of a backends.django.Template.
        elif hasattr(template, 'template'):
            template = template.template

        attrs = self.attrs.copy()

        # Do not use original context since we are updating values inside this function
        _context = self.get_context_data(copy(context))

        # Class attributes
        class_attrs = list(filter(lambda x: isinstance(x[1], Attribute), vars(self.__class__).items()))

        while class_attrs:
            key, attr = class_attrs.pop()

            if not attr.name:
                attr.set_name(key)

            try:
                value = attr.resolve(attrs.pop(key), context)
            except KeyError:
                value = attr.default

            key = attr.name

            if attr.as_context:
                _context[key] = value
            elif attr.as_class:
                _context.add_class(value)
            else:
                _context.add_attribute(key, value)

        # Attribute variables
        for name, value in attrs.items():
            _context.add_attribute(name, value)

        # Option variables
        for name, value in self.options.items():
            _context[name] = value.resolve(context)

        context = _context.make()  # Slots should only have access to parent context

        # Slot nodes
        for name, value in self.slots.items():
            _context[name] = value.render(context)

        return template.render(context)
