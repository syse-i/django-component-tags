from typing import Optional

__all__ = [
    'BaseAttribute',
    'Attribute',
    'ClassAttribute',
    'ContextAttribute',
]


class ChoiceDoesNotExist(Exception):
    pass


class RequiredValue(Exception):
    pass


class BaseAttribute:
    """
    Attributes contain additional pieces of information.
    Attributes take the form of an opening tag and additional info is placed inside.
    """

    ChoiceDoesNotExist = ChoiceDoesNotExist
    RequiredValue = RequiredValue

    def __init__(self, choices=None, default=None, required=None, name: Optional[str] = None):
        self.choices = choices
        self.default = default
        self.required = default is not None
        self.name = name

        if required is not None:
            self.required = bool(required)

    @property
    def default(self):
        try:
            return self._default.value
        except AttributeError:
            return self._default

    @default.setter
    def default(self, value):
        self._default = value

    def resolve_default(self):
        if self.required and self.default is None:
            raise RequiredValue(f'{self.name} should be different than null')
        return self.default

    def resolve(self, value, context):
        try:
            _value = value.resolve(context)
        except AttributeError:
            _value = value
        if self.required and _value is None:
            raise RequiredValue(f'{self.name} should be different than null')
        if self.choices:
            try:
                return self.choices[_value].value
            except KeyError:
                values = [key for key, value in self.choices.__members__.items()]
                raise ChoiceDoesNotExist(f'{_value} is not an available choice, choices are: {values}')
        return _value


class Attribute(BaseAttribute):
    pass


class ClassAttribute(BaseAttribute):
    pass


class ContextAttribute(BaseAttribute):
    pass
