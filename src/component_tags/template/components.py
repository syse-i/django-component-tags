from django.template.base import NodeList

from .nodes import ComponentNode

__all__ = ['Slot']


class Slot(ComponentNode):

    def __init__(self, tag_name: str, nodelist: NodeList, options: dict, slots: dict, name: str, *args,
                 isolated_context=True, **kwargs):
        super().__init__(tag_name, nodelist, options, slots, *args, isolated_context=isolated_context, **kwargs)
        # TODO: there should be a better way to perform this action but name should be declared inside this constructor
        self._name = getattr(name, 'var', None)
        self._isolated_context = False  # Make sure slot has the parent context

    class Meta:
        template_name = 'component_tags/slot.html'
