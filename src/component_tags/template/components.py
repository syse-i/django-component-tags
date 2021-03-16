from django.template.base import Variable, NodeList

from .nodes import ComponentNode

__all__ = ['Slot']


class Slot(ComponentNode):
    """
    Can be used inside any other component to create dynamic blocks inside components.

    Attributes
    ----------
    name: str
        name used to identify the slot inside the component tag

    Examples
    --------

        .. code-block::

            # tags/button.html
            <span>{{ slot_foo }}</span>
            <button {{ attributes }}>
                {{ nodelist }}
            </button>

            # base.html
            {% button type="button" %}
                {% slot 'foo' %}Slot 1{% endslot %}
                Button 1
            {% endbutton %}

            # Output:
            <span>Slot 1</span>
            <button type="button"></button>
    """

    def __init__(self, *args, **kwargs):
        tag_name, nodelist, options, slots, name = args
        kwargs['isolated_context'] = True  # Make sure slot has the parent context
        super().__init__(tag_name, nodelist, options, slots, **kwargs)

        # TODO:
        #  there should be a better way to get the variable value
        #  but name should be declared inside this constructor
        self.slot_name = getattr(name, 'var', None)

    class Meta:
        template_name = 'component_tags/slot.html'
