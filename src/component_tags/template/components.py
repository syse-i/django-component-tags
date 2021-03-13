from django.template.base import Variable, NodeList

from .nodes import ComponentNode

__all__ = ['Slot']


class Slot(ComponentNode):

    def __init__(self, tag_name: str, nodelist: NodeList, options: dict, slots: dict, name: str, *args,
                 isolated_context: bool = True, **kwargs):
        # Make sure slot has the parent context
        super().__init__(tag_name, nodelist, options, slots, *args, isolated_context=False, **kwargs)
        # TODO:
        #  there should be a better way to get the variable value
        #  but name should be declared inside this constructor
        self.slot_name = getattr(name, 'var', None)

    class Meta:
        template_name = 'component_tags/slot.html'
