from django.template.library import Library as BaseLibrary

from .wrappers import component_wrapper
from .nodes import BaseComponent

__all__ = ['Library']


class Library(BaseLibrary):

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
            # @register.tag('somename') or @register.tag(name='somename')
            else:
                tag_func = super().tag

                def dec(f):
                    if isinstance(f, BaseComponent):
                        return tag_func(*component_wrapper(name, f))
                    return tag_func(name, f)

                return dec
        # register.tag('somename', somefunc)
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
