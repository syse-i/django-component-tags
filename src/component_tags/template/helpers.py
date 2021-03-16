from typing import Optional, Union

from django.template import Context, RequestContext
from django.utils.safestring import SafeText, SafeString

__all__ = [
    'format_value',
    'format_classes',
    'format_attributes',
]


def format_value(value, context=None):
    """
    Resole the Variable/FilterExpression value else nothing happens
    """
    try:
        return value.resolve(context)
    except AttributeError:
        return value


def format_classes(classes: Optional[list], context=Union[Context, RequestContext]) -> Optional[SafeText]:
    """
    Join all classes as a string
    """
    # Is format_classes already called before?
    if isinstance(classes, SafeString):
        return classes

    # Do not print anything if there are no html classes
    if not classes:
        return None

    elements = []
    for value in classes:
        value = format_value(value, context)
        if value is not None:
            elements.append(value)

    return SafeText(" ".join(elements))


# TODO: remove this function
# def format_options(options, context=None) -> SafeText:
#     elements = []
#     for (key, value) in options.items():
#         value = format_value(value, context)
#         if value is not None:
#             elements.append("{}: {}".format(key, value))
#     return SafeText("; ".join(elements).lower())


def format_attributes(properties, context=None) -> SafeText:
    """
    Join all attributes as a string
    """
    # Is format_attributes already called before?
    if isinstance(properties, SafeString):
        return properties

    elements = []
    for (key, value) in properties.items():
        # Is this a class attribute
        if key == 'class':
            value = format_classes(value, context)
        else:
            value = format_value(value, context)
        if value is not None:
            elements.append(f'{key}="{value}"')

    return SafeText(" ".join(elements))
