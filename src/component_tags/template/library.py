from django.template.library import Library as BaseLibrary

from .wrappers import component_wrapper
from .nodes import BaseComponent

__all__ = ['Library']


class Library(BaseLibrary):
    """
    A custom class for registering template components, tags and filters.
    The filter, simple_tag, and inclusion_tag methods provide a convenient
    way to register callables/components as tags.

    Examples
    --------
    There is a lot of ways to register a component tag:

    .. code-block:: python

        register.tag('name', ComponentClass)

        @register.tag
        class ComponentClass:
            pass

        @register.tag()
        class ComponentClass:
            pass

        @register.tag('name')
        class ComponentClass:
            pass

        register.tag_function(ComponentClass)

        register.component('name', ComponentClass)

        @register.component
        class ComponentClass:
            pass

    Notes
    ----
    - Pycharm doesnt recognize @register.component, therefore the recommended way to register all components
    using Pycharm is with `register.tag('name', ComponentClass)`
    - Does not interfere with the current Django Library behavior, but it decorates the callable function
    with the component wrapper if this is a component tag.
    """

    def tag_function(self, func):
        if isinstance(func, BaseComponent):
            name = getattr(func, "_decorated_function", func).__name__.lower()
            name, func = component_wrapper(name, func)
            self.tags[name] = func
            return func
        return super().tag_function(func)

    def tag(self, name=None, compile_function=None):
        # @register.tag()
        if name is None and compile_function is None:
            return self.tag_function
        if name is not None and compile_function is None:
            # @register.tag
            if callable(name):
                if isinstance(name, BaseComponent):
                    component_name = name.__name__.lower()
                    name, func = component_wrapper(component_name, name)
                    self.tags[name] = func
                    return func
                return super().tag_function(name)
            # @register.tag('foobar') or @register.tag(name='foobar')
            else:
                tag_func = super().tag

                def dec(f):
                    if isinstance(f, BaseComponent):
                        return tag_func(*component_wrapper(name, f))
                    return tag_func(name, f)

                return dec
        # register.tag('foobar', foobar)
        elif name is not None and compile_function is not None:
            if isinstance(compile_function, BaseComponent):
                name, func = component_wrapper(name, compile_function)
                self.tags[name] = func
                return func
            self.tags[name] = compile_function
            return compile_function
        else:
            raise ValueError("Unsupported arguments to Library.tag: (%r, %r)" % (name, compile_function))

    def component(self, name=None, compile_function=None):
        return self.tag(name=name, compile_function=compile_function)
