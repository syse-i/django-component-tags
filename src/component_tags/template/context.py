from typing import Optional, Union

from django.template import Context, RequestContext
from django.template.base import NodeList

from .helpers import format_attributes, format_value

__all__ = [
    'BaseContext',
    'Context',
    'TagContext',
    'ComponentContext'
]


class BaseContext:
    """
    Context wrapper which includes a couple of methods to create the same outcome.

    Attributes
    ----------
    initial: Union[Context, RequestContext, None]
        current template context
    dict_: dict
        extra values added to the context
    isolated: bool
        ensures that the context is isolated from the global context
    """

    default_class = Context

    def __init__(self, initial: Union[Context, RequestContext, None], dict_: dict, isolated: bool = True):
        if initial is None:
            self._wrap = self.default_class(dict_)
        elif isinstance(initial, (Context, RequestContext)):
            self._wrap = initial
        else:
            raise Exception('Cannot define initial')

        if isolated:
            self._wrap = self.new(dict_)
        else:
            self.update(dict_)

    def __copy__(self):
        return self._wrap.__copy__()

    def __repr__(self):
        return self._wrap.__repr__()

    def __iter__(self):
        return self._wrap.__iter__()

    def __setitem__(self, key, value):
        self._wrap.__setitem__(key, self.resolve(value))

    def __getitem__(self, key):
        """
        Get a variable's value, starting at the current context and going upward
        """
        return self._wrap.__getitem__(key)

    def __delitem__(self, key):
        """
        Delete a variable from the current context
        """
        self._wrap.__delitem__(key)

    def __contains__(self, key):
        return self._wrap.__contains__(key)

    def __eq__(self, other):
        """
        Compare two contexts by comparing theirs 'dicts' attributes.
        """
        return self._wrap.__eq__(other)

    def clean(self):
        """
        Return the wrapped context
        """
        return self._wrap

    def flatten(self) -> dict:
        """
        Return self.dicts as one dictionary.
        """
        return self.make().flatten()

    def push(self, *args, **kwargs):
        return self._wrap.push(*args, **kwargs)

    def pop(self):
        return self._wrap.pop()

    def set_upward(self, key, value):
        """
        Set a variable in one of the higher contexts if it exists there,
        otherwise in the current context.
        """
        self._wrap.set_upward(key, self.resolve(value))

    def get(self, key, otherwise=None):
        return self._wrap.get(key, otherwise)

    def setdefault(self, key, default=None):
        return self._wrap.setdefault(key, default)

    def new(self, values=None):
        """
        Return a new context with the same properties, but with only the
        values given in 'values' stored.
        """
        return self._wrap.new(values)

    def update(self, *args, **kwargs):
        return self._wrap.update(*args, **kwargs)

    def make(self):
        """
        Used to exec any function before compile the component tag.
        """
        return self.clean()

    def resolve(self, value):
        """
        Resolve the Variable/FilterExpression using the wrapped context
        """
        return format_value(value, self._wrap)


class TagContext(BaseContext):
    """
    Context used inside a tag function, if there is no need to create a component tag this is the way to
    recreate the same context.

    Attributes
    ----------
    attributes: Optional[dict]
        html attributes stored inside the context, and can be used as: {{ attributes }}
    initial: Optional[RequestContext]
        current template context
    isolated: bool
        ensures that the context is isolated from the global context
    **kwargs: dict
        extra values added to the context
    """

    default_class = RequestContext

    def __init__(self, attributes: Optional[dict] = None, initial: Optional[RequestContext] = None,
                 isolated: bool = False, **kwargs):
        super().__init__(initial, kwargs, isolated=isolated)
        self._attributes = {} if attributes is None else attributes

    @property
    def _attributes(self):
        return self['attributes']

    @_attributes.setter
    def _attributes(self, values: dict):
        if not isinstance(values, dict):
            raise Exception('Set attrs as a dict')
        self['attributes'] = values

    def add_class(self, *value):
        """
        Add a html "class" attribute inside the context.
        There can be used multiple times to store multiple classes in different scenarios.

        TODO: class as list to perform:
            - context.class.append
            - context.class = <var:list> | <var:string>
            - context.class.remove(<index:string>)
            - context.class.reset() === list()
        """

        values = [self.resolve(v) for v in value]

        try:
            self._attributes['class'].extend(values)
        except AttributeError:  # cannot extend
            classes = self._attributes['class']
            self._attributes['class'] = [classes] + values
        except KeyError:  # class not defined
            self._attributes['class'] = values

    def add_attribute(self, name: str, value):
        """
        Add a html attribute inside the context.
        There can be used multiple times to store multiple key/values in different scenarios.

        TODO: attribute as dict to perform:
          - context.attributes[<index:string>] = <value:string>
          - context.attributes = <var:dict>
          - del context.attributes[<index:string>]
          - context.attributes.reset() === dict()
        """
        value = self.resolve(value)

        # is this a class attribute?
        if name in 'class':
            return self.add_class(value)

        self._attributes[name] = value

    def make(self):
        """
        Collection of actions executed before render the component:
        - Format attributes as strings
        """
        context = super().make()
        context['attributes'] = format_attributes(self._attributes, context)
        return context


class ComponentContext(TagContext):
    """
    Context used inside component tags.

    Attributes
    ----------
    nodelist: NodeList
        nodelist passed to the component context
    initial: Optional[RequestContext]
        current template context
    attributes: Optional[dict]
        html attributes stored inside the context, and can be used as: {{ attributes }}
    isolated: bool
        ensures that the context is isolated from the global context
    **kwargs: dict
        extra values added to the context
    """
    def __init__(self, nodelist: NodeList, initial: RequestContext, attributes: Optional[dict] = None,
                 isolated: bool = True, **kwargs):
        super().__init__(attributes, initial=initial, isolated=isolated, **kwargs)
        self._nodelist = nodelist

        # TODO: get rid of this implementation
        # Make sure that request is part of the context
        if 'request' not in self and getattr(self._wrap, 'request', False):
            self['request'] = self._wrap.request

    def make(self):
        """
        Collection of actions executed before render the component:
        - Format attributes as strings
        - Render the current nodelist and store it inside the current context
        """
        context = super().make()
        context['nodelist'] = self._nodelist.render(context)
        return context
