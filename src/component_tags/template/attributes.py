from enum import Enum
from typing import Optional, Union

from django.template.base import Variable, FilterExpression, VariableDoesNotExist

__all__ = ['Attribute']


class ChoiceDoesNotExist(Exception):
    """
    Raised when the specified choice is not a choice's member
    """
    pass


class RequiredValue(Exception):
    """
    Raised when a variable value is required
    """
    pass


class Attribute:
    """
    Template Components have attributes; these are additional values that configure the elements or adjust their
    behavior in various ways to meet the criteria the users want.

    Attributes
    ----------
    name : str
        name used to identify it inside the context
    choices: AttributeChoices
        choices are used to specify the attribute correct value from a list of available options
    default: Any
        default attribute value
    required: bool
        set if the attribute value is required
    as_class: bool
        set the attribute as "class type" inside the template
    as_context: bool
        set the attribute as "context type" inside the template

    Examples
    --------
    **Attribute as class**

    Considering the following definition:

    .. code-block:: python

        # templatetags/custom_tags.py

        @register.component
        class Button(template.Component):
            class ColorChoices(template.AttributeChoices):
                primary = 'btn-primary'
                secondary = 'btn-secondary'

            color = template.Attribute(choices=ColorChoices, default=ColorChoices.primary, as_class=True)

            class Meta:
                template_name = 'components/button.html'

    And the following template

    .. code-block:: 

        # templates/components/button.html

        <button {{ attributes }}></button>

    Output

    .. code-block::

        # Setting a value
        {% button color="secondary" %}{% endbutton %}

        # output:
        <button class="btn-secondary"></button>

        # Without setting a value
        {% button %}{% endbutton %}

        # output:
        <button class="btn-primary"></button>

    **Attribute as context**

    Considering the following definition:

    .. code-block:: python

        class Button(template.Component):
            href = template.Attribute(default="#", as_context=True)

    You can use this attribute inside the component context as follows:

    .. code-block::

        # Setting a value
        {% button href="/some-url" %}
            {{ href }} # output: "/some-url"
        {% endbutton %}

        # Without setting a value
        {% button %}
            {{ href }} # output: "#"
        {% endbutton %}
    """

    ChoiceDoesNotExist = ChoiceDoesNotExist
    VariableDoesNotExist = VariableDoesNotExist
    RequiredValue = RequiredValue

    def __init__(self, choices=None, default=None, required: bool = False, context_name: str = None,
                 as_class: bool = False, as_context: bool = False):
        self.context_name = context_name

        try:
            if choices and not issubclass(choices, Enum):
                raise RequiredValue("choices must be Enum's subclass")
        except TypeError:
            raise RequiredValue("choices must be Enum's subclass")

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
        """
        Sets the default value and checks if can be applied.
        """
        self._default = self.check_value(value) if value is not None else value

    def get_member_choices(self):
        """
        Get the member choices as list
        """
        return [key for key, value in self.choices.__members__.items()]

    def get_choice(self, key: Union[Enum, str], raise_exception: bool = False):
        """
        Get the member choice value using the Enum format
        """
        if not raise_exception:
            raise_exception = self.required

        try:
            # noinspection PyCallingNonCallable,PyArgumentList
            return format(key if isinstance(key, self.choices) else self.choices[key])
        except (KeyError, ValueError):
            if raise_exception:
                raise ChoiceDoesNotExist(f'{key} is not an available choice, choices are: {self.get_member_choices()}')

    def check_value(self, value, raise_exception: bool = False):
        """
        Verify if the current value is valid based on different criteria
        """
        if self.required and value is None:
            raise RequiredValue(f'{self.context_name} should be different than null')
        return self.get_choice(value, raise_exception) if self.choices else value

    def set_context_name(self, value: str):
        """
        The name of the attribute used as context name.

        Sometimes declaring the names it is not enough to get the result needed, specially when you want to
        work with javascript.
        
        Examples
        --------
        
        **As a class instance:**

        .. code-block:: python
            
            class Button(template.Component):
                href = template.Attribute(default="#", as_context=True)

        Output:

        .. code-block::

                # base.html

                # Setting a value
                {% button href="foo-bar/" %}{% button %}

                # Output:
                <button href="foo-bar/"></button>

                # Without setting a value
                {% button %}{% button %}

                # Output:
                <button href="#"></button>
                
        **As parameter:**

        .. code-block:: python
        
                class Button(template.Component):
                    href = template.Attribute(default="#", name="data-href")

        Output:

        .. code-block::

                # base.html

                # Setting a value
                {% button href="foo-bar/" %}{% button %}

                # Output:
                <button data-href="foo-bar/"></button>

                # Without setting a value
                {% button %}{% button %}

                # Output:
                <button data-href="#"></button>

        """
        self.context_name = value

    def resolve(self, value: Union[Variable, FilterExpression, str], context, raise_exception: bool = True):
        """
        Resolves the template variable/expression specified as an argument, then checks if the value can be used.
        """
        try:
            return self.check_value(value.resolve(context), raise_exception=raise_exception)
        except VariableDoesNotExist as ex:
            raise self.VariableDoesNotExist(ex)
