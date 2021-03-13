from enum import Enum
from typing import Optional, Union

from django.template.base import Variable, FilterExpression, VariableDoesNotExist

__all__ = ['Attribute', 'BaseAttribute']


class InvalidChoice(Exception):
    pass


class ChoiceDoesNotExist(Exception):
    pass


class RequiredValue(Exception):
    pass


class BaseAttribute(type):
    pass


class Attribute(metaclass=BaseAttribute):
    """
    Attributes contain additional pieces of information.
    Attributes take the form of an opening tag and additional info is placed inside.
    """

    ChoiceDoesNotExist = ChoiceDoesNotExist
    VariableDoesNotExist = VariableDoesNotExist
    RequiredValue = RequiredValue
    InvalidChoice = InvalidChoice

    def __init__(self, choices=None, default=None, required: bool = False, name: str = None,
                 as_class: bool = False, as_context: bool = False):
        self.name = name

        if choices and not issubclass(choices, Enum):
            raise RequiredValue('choices must be a subclass of Enum')

        self.choices = choices
        self.required = required
        self.default = default
        self.as_class = as_class
        self.as_context = as_context

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, value: Optional[Enum]):
        self._default = self.check_value(value) if value is not None else value

    def get_member_choices(self):
        return [key for key, value in self.choices.__members__.items()]

    def get_choice(self, key: Enum, raise_exception: bool = False):
        if not raise_exception:
            raise_exception = self.required

        try:
            # noinspection PyCallingNonCallable,PyArgumentList
            return format(key if isinstance(key, self.choices) else self.choices[key])
        except KeyError:
            if raise_exception:
                raise ChoiceDoesNotExist(f'{key} is not an available choice, choices are: {self.get_member_choices()}')
        except ValueError:
            if raise_exception:
                raise self.InvalidChoice(f'{key} is not a valid choice, choices are: {self.get_member_choices()}')

    def check_value(self, value, raise_exception: bool = False):
        if self.required and value is None:
            raise RequiredValue(f'{self.name} should be different than null')
        return self.get_choice(value, raise_exception) if self.choices else value

    def set_name(self, value: str):
        self.name = value

    def resolve(self, value: Union[Variable, FilterExpression, str], context, raise_exception: bool = True):
        try:
            return self.check_value(value.resolve(context), raise_exception=raise_exception)
        except VariableDoesNotExist as ex:
            raise self.VariableDoesNotExist(ex)
