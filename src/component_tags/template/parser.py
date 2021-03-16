from django.template.exceptions import TemplateSyntaxError
from django.template.base import kwarg_re, FilterExpression, token_kwargs

from .components import Slot


def parse_component(nodelist, token, parser):
    """
    Load a component template and render it with the current context. You can pass
    additional context using keyword arguments.

    Example

    .. code-block::

        {% component %}{% endcomponent %}
        {% component with bar="BAZZ!" baz="BING!" %}{% endcomponent %}

    """
    bits = token.split_contents()

    # if len(bits) < 2:
    #     raise TemplateSyntaxError(
    #         "%r tag takes at least one argument: the name of the template to "
    #         "be included." % bits[0]
    #     )

    tag_name = bits.pop(0)
    args = []
    kwargs, options, slots = {}, {}, {}
    isolated_context = True

    while bits:
        bit = bits.pop(0)

        # if bit in options:
        #     raise TemplateSyntaxError('The %r option was specified more than once.' % bit)

        match = kwarg_re.match(bit)
        kwarg_format = match and match.group(1)

        if kwarg_format:
            key, value = match.groups()
            filter_expr = FilterExpression(value, parser)
            kwargs[key] = filter_expr
        else:
            filter_expr = FilterExpression(bit, parser)
            args.append(filter_expr)

        if bit == 'with':
            options = token_kwargs(bits, parser, support_legacy=False)
            if not options:
                raise TemplateSyntaxError('"with" in %r tag needs at least '
                                          'one keyword argument.' % tag_name)

    slot_nodes = list(filter(lambda x: isinstance(x[1], Slot), enumerate(nodelist)))

    while slot_nodes:
        pos, node = slot_nodes.pop()
        name = getattr(node, 'slot_name', pos)
        key = f'slot_{pos if name is None else name}'
        slots[key] = node
        del nodelist[pos]

    return tag_name, args, kwargs, options, slots, isolated_context
