from copy import copy

from django.template.base import Node, NodeList

__all__ = ['ComponentNode', 'BaseComponent']

from .attributes import ClassAttribute, ContextAttribute, Attribute, BaseAttribute
from .context import ComponentContext


class TemplateIsNull(Exception):
    pass


class BaseComponent(type):
    """Metaclass for all component nodes."""
    pass


class ComponentMeta:
    template_name = None


class ComponentNode(Node, metaclass=BaseComponent):
    """
    Components are used to mark up the start of an HTML element
    and they are usually enclosed in angle brackets.
    """

    TemplateIsNull = TemplateIsNull

    def __init__(self, tag_name: str, nodelist: NodeList, options: dict, slots: dict, *args,
                 isolated_context: bool = True, **kwargs):
        self._tag_name = tag_name
        self._nodelist = nodelist
        self._attrs = kwargs
        self._slots = slots
        self._options = options
        self._isolated_context = isolated_context
        self._meta = self.set_meta()

    def get_template_name(self, context):
        template_name = self._meta.template_name
        if not template_name:
            raise self.TemplateIsNull('Template is undefined')
        return context.template.engine.get_template(template_name)

    # TODO: understand _meta and implement inherit here
    def set_meta(self):
        class InheritMeta(getattr(self, 'Meta', object), ComponentMeta):
            pass
        return InheritMeta

    def get_context_data(self, context):
        return ComponentContext(self._nodelist, initial=context, isolated=self._isolated_context)

    def render(self, context):
        template = self.get_template_name(context)

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

        attrs = self._attrs.copy()

        # Do not use original context since we are updating values inside this function
        _context = self.get_context_data(copy(context))

        # Class attributes
        class_attrs = list(filter(lambda x: isinstance(x[1], BaseAttribute), vars(self.__class__).items()))

        while class_attrs:
            key, attr = class_attrs.pop()

            if not attr.name:
                attr.name = key

            try:
                value = attr.resolve(attrs.pop(key), context)
            except KeyError:
                value = attr.resolve_default()

            key = attr.name

            if isinstance(attr, Attribute):
                _context.add_attribute(key, value)
            elif isinstance(attr, ClassAttribute):
                _context.add_class(value)
            elif isinstance(attr, ContextAttribute):
                _context[key] = value
            else:
                raise AttributeError('Must be Attribute instance')

        # Attribute variables
        for name, value in attrs.items():
            _context.add_attribute(name, value)

        # Option variables
        for name, value in self._options.items():
            _context[name] = value.resolve(context)

        context = _context.make()  # Slots should only have access to parent context

        # Slot nodes
        for name, value in self._slots.items():
            _context[name] = value.render(context)

        return template.render(context)

