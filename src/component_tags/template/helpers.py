from django.utils.safestring import SafeText, SafeString

__all__ = [
    'format_value',
    'format_classes',
    'format_attributes',
]


def format_value(value, context=None):
    try:
        return value.resolve(context)
    except AttributeError:
        return value


def format_classes(classes, context=None):
    if isinstance(classes, SafeString):
        return classes

    elements = []

    if not classes:
        return None

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
    if isinstance(properties, SafeString):
        return properties

    elements = []
    for (key, value) in properties.items():
        is_class = key == 'class'
        if is_class:
            value = format_classes(value, context)
            if value is not None:
                elements.append('{}="{}"'.format(key, value))
        else:
            value = format_value(value, context)
            if value is not None:
                elements.append('{}="{}"'.format(key, value))

    return SafeText(" ".join(elements))
