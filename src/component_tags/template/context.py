from typing import Optional

from django.template import Context, RequestContext
from django.template.base import NodeList

from .helpers import format_attributes, format_value

__all__ = [
    'BaseContext',
    'TagContext',
    'ComponentContext'
]


class BaseContext:

    def __init__(self, initial: Optional[Context], dict_: dict, isolated: bool = True):
        if initial is None:
            self._wrap = Context(dict_)
        elif isinstance(initial, Context):
            self._wrap = initial
        else:
            raise Exception('context is not a Context instance')

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
        return self._wrap

    def flatten(self) -> dict:
        """
        Return self.dicts as one dictionary.
        """
        return self._wrap.flatten()

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

    def resolve(self, value):
        return format_value(value, self._wrap)

    def update(self, *args, **kwargs):
        return self._wrap.update(*args, **kwargs)


class TagContext(BaseContext):

    def __init__(self, attributes: Optional[dict] = None, initial: Optional[RequestContext] = None,
                 isolated: bool = False, **kwargs):
        super().__init__(initial, kwargs, isolated=isolated)
        self._attributes = attributes if attributes else {}

    @property
    def _attributes(self):
        return self['attributes']

    @_attributes.setter
    def _attributes(self, values: dict):
        if not isinstance(values, dict):
            raise Exception('Set attrs as a dict')
        self['attributes'] = values

    # TODO: class as list to perform:
    #  - context.class.append
    #  - context.class = <var:list> | <var:string>
    #  - context.class.remove(<index:string>)
    #  - context.class.reset() === list()

    def add_class(self, *value):
        values = [self.resolve(v) for v in value]

        try:
            self._attributes['class'].extend(values)
        except AttributeError:  # cannot extend
            classes = self._attributes['class']
            self._attributes['class'] = [classes] + values
        except KeyError:  # class not defined
            self._attributes['class'] = values

    # TODO: attribute as dict to perform:
    #  - context.attributes[<index:string>] = <value:string>
    #  - context.attributes = <var:dict>
    #  - del context.attributes[<index:string>]
    #  - context.attributes.reset() === dict()

    def add_attribute(self, name: str, value):
        value = self.resolve(value)

        # want to add a class attribute?
        if name in 'class':
            return self.add_class(value)

        self._attributes[name] = value

    def make(self):
        context = self._wrap
        context['attributes'] = format_attributes(self._attributes, context)
        return context

    def flatten(self) -> dict:
        """
        Return self.dicts as one dictionary.
        """
        return self.make().flatten()


class ComponentContext(TagContext):

    def __init__(self, nodelist: NodeList, initial: RequestContext, attributes: Optional[dict] = None,
                 isolated: bool = True, **kwargs):
        super().__init__(attributes, initial=initial, isolated=isolated, **kwargs)
        self._nodelist = nodelist

        if 'request' not in self and getattr(self._wrap, 'request', False):
            self['request'] = self._wrap.request

    def make(self):
        context = super().make()
        context['nodelist'] = self._nodelist.render(context)
        return context
