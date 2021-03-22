from django.template import Context
from django.template.base import Variable
from django.test import TestCase

from .template.choices import AttributeChoices
from .template.attributes import Attribute
from .template.builtins import register
from .template.components import Slot


class ChoiceTestCase(TestCase):

    def test_format(self):
        class FooChoices(AttributeChoices):
            bar = 'bar'

        self.assertEqual(format(FooChoices.bar), 'bar')

    def test_format_repr(self):
        class FooChoices(AttributeChoices):
            bar = 1

        self.assertIsInstance(format(FooChoices.bar), str)


class AttributeTestCase(TestCase):

    def setUp(self):
        class CustomChoices(AttributeChoices):
            foo = 'bar'

        self.choices = CustomChoices

    def test_is_instance(self):
        self.assertIsInstance(Attribute(), Attribute)

    def test_choices(self):
        attr = Attribute(choices=self.choices)
        x = Variable('attr')
        c = Context({'attr': 'foo'})
        self.assertEqual(attr.resolve(x, c), 'bar')

    def test_choice_does_not_exist(self):
        attr = Attribute(choices=self.choices, required=True)
        x = Variable('attr')
        c = Context({'attr': 'ERROR'})
        self.assertRaises(Attribute.ChoiceDoesNotExist, lambda: attr.resolve(x, c))

        attr = Attribute(choices=self.choices, required=True)
        x = Variable('attr')
        c = Context({'attr': 'ERROR'})
        self.assertRaises(Attribute.ChoiceDoesNotExist, lambda: attr.get_choice('x', raise_exception=True))

    def test_choices_default(self):
        attr = Attribute(choices=self.choices, default=self.choices.foo)

        try:
            # Not placing the attr inside context on purpose
            x = Variable('attr')
            c = Context()
            value = attr.resolve(x, c)
        except Attribute.VariableDoesNotExist:
            value = attr.default

        self.assertEqual(value, 'bar')

    def test_variable_does_not_exist(self):
        attr = Attribute(choices=self.choices)

        def test_func():
            x = Variable('attr')
            c = Context()
            return attr.resolve(x, c)

        self.assertRaises(Attribute.VariableDoesNotExist, test_func)

    def test_choices_are_required_and_value_is_none(self):
        attr = Attribute(choices=self.choices, required=True)

        def test_func():
            try:
                x = Variable('attr')
                c = Context({'attr': None})
                return attr.resolve(x, c)
            except Attribute.VariableDoesNotExist:
                return attr.default

        self.assertRaises(Attribute.RequiredValue, test_func)

    def test_choices_are_not_enum_type(self):
        class Choices:
            bar = 1

        def test_with_class():
            return Attribute(choices=Choices)

        def test_with_list():
            return Attribute(choices=[{'foo': 'bar'}])

        self.assertRaises(Attribute.RequiredValue, test_with_class)
        self.assertRaises(Attribute.RequiredValue, test_with_list)

    def test_set_context_name(self):
        attr = Attribute(choices=self.choices)
        attr.set_context_name('foo')
        self.assertEqual(attr.context_name, 'foo')


class BuiltinsTestCase(TestCase):

    def setUp(self) -> None:
        self.BUILTIN_TAGS = [
            ('slot', Slot)
        ]

    def test_default_tags(self):
        for name, i in self.BUILTIN_TAGS:
            self.assertIn(name, register.tags)
            self.assertTrue(issubclass(register.tags[name].__wrapped__, Slot))


class ComponentTestCase(TestCase):
    pass


class ContextTestCase(TestCase):
    pass


class HelperTestCase(TestCase):
    pass


class LibraryTestCase(TestCase):
    pass


class NodeTestCase(TestCase):
    pass


class ParserTestCase(TestCase):
    pass


class WrapperTestCase(TestCase):
    pass
