from inspect import getmembers
from copy import copy

from django.forms.widgets import Media
from django.template.base import Node, NodeList

from .media import add_media
from .attributes import Attribute
from .context import ComponentContext


__all__ = ['ComponentNode', 'BaseComponent', 'Meta', 'Media']


class TemplateIsNull(Exception):
    pass


class Meta(Media):
    """
    Meta definition of component tags, currently only used to declare template information
    """
    def __init__(self, meta=None, css=None, js=None):
        super().__init__(meta, css, js)
        self.template_name = getattr(meta, 'template_name', None)


def meta_property(cls):
    """
    Get the media property of the superclass, if it exists
    """
    def _meta(self):

        sup_cls = super(cls, self)
        try:
            # noinspection PyUnresolvedReferences
            base = sup_cls.meta
        except AttributeError:
            base = Meta()

        # Get the media definition for this class
        definition = getattr(cls, 'Meta', None)

        if definition:
            extend = getattr(definition, 'extend', True)
            if extend:
                if extend is True:
                    m = base
                else:
                    m = Meta()
                    for medium in extend:
                        m = m + base[medium]
                extended = m + Meta(definition)
            else:
                extended = Meta(definition)

            template_name = getattr(definition, 'template_name', None)
            if template_name:
                setattr(extended, 'template_name', template_name)
            return extended
        return base
    return property(_meta)


class BaseComponent(type):
    """Metaclass for all component nodes."""

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)

        if 'meta' not in attrs:
            new_class.meta = meta_property(new_class)

        return new_class


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

    def get_template_name(self):
        return getattr(self.meta, 'template_name', None)

    def get_template(self, context):
        template_name = self.get_template_name()

        if not template_name:
            raise self.TemplateIsNull(f'[{self.tag_name.title()}] component does not have a template assigned.')

        return context.template.engine.get_template(template_name)

    def get_context_data(self, context):
        return ComponentContext(self.nodelist, initial=context, isolated=self.isolated_context)

    def render(self, context):
        add_media(context, self.meta)
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
        class_attrs = getmembers(self, lambda a: isinstance(a, Attribute))

        while class_attrs:
            key, attr = class_attrs.pop()

            if not attr.context_name:
                attr.set_context_name(key)

            try:
                value = attr.resolve(attrs.pop(key), context)
            except KeyError:
                value = attr.default

            key = attr.context_name

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
