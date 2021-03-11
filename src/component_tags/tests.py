from django.template import Context
from django.template.base import Variable, VariableDoesNotExist
from django.test import TestCase

from .template.choices import AttributeChoices
from .template.attributes import BaseAttribute, Attribute


class AttributeTest(TestCase):

    def setUp(self):
        class CustomChoices(AttributeChoices):
            foo = 'bar2'

        self.choices = CustomChoices

    def test_is_instance(self):
        self.assertIsInstance(Attribute(), BaseAttribute)

    def test_choices(self):
        attr = Attribute(choices=self.choices)
        context = Context({'attr': 'foo'})
        self.assertEqual(attr.resolve(Variable('attr'), context), 'bar')

    def test_choice_not_found(self):
        attr = Attribute(choices=self.choices)
        context = Context({'attr': 'X'})
        self.assertRaises(Attribute.ChoiceDoesNotExist, lambda: attr.resolve(Variable('attr'), context))

    def test_choices_default(self):
        attr = Attribute(choices=self.choices, default=self.choices.foo)
        context = Context()

        try:
            value = attr.resolve(Variable('attr'), context)
        except VariableDoesNotExist:
            value = attr.resolve_default()
        self.assertEqual(value, 'bar')

    def test_choices_are_required(self):
        attr = Attribute(choices=self.choices, required=True, name='attr')
        context = Context()

        def test_func():
            try:
                attr.resolve(Variable('attr'), context)
            except VariableDoesNotExist:
                attr.resolve_default()
        self.assertRaises(Attribute.RequiredValue, test_func)

    def test_choices_are_required_and_value_is_none(self):
        attr = Attribute(choices=self.choices, required=True, name='attr')
        context = Context({'attr': None})

        def test_func():
            try:
                attr.resolve(Variable('attr'), context)
            except VariableDoesNotExist:
                attr.resolve_default()
        self.assertRaises(Attribute.RequiredValue, test_func)

    def test_with_no_context(self):
        attr = Attribute()
        self.assertEqual(attr.resolve('attr', None), 'attr')
