from .parser import parse_component
from functools import wraps

__all__ = ['component_wrapper']


def component_wrapper(name, component_node):
    """
    Component wrapper to parse all component args
    """
    @wraps(component_node)
    def func(parser, token):
        nodelist = parser.parse(('end%s' % name,))
        parser.delete_first_token()
        tag_name, args, kwargs, options, slots, isolated_context = parse_component(nodelist, token, parser)
        return component_node(tag_name, nodelist, options, slots, *args, isolated_context=isolated_context, **kwargs)
    return name, func
