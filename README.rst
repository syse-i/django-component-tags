=======================
Django - Component Tags
=======================

Create advanced HTML components using Django Tags.


Description
===========

The goal of this project is to use
`Django Template Tags <https://docs.djangoproject.com/en/3.1/ref/templates/builtins/>`_ and create a new way of
writing **reusable html components** compatible with the current template infrastructure. This new way should
fit the Django standards of creating classes, like ``Models`` and ``Forms``, also it should require as little boilerplate
code and be simple to write.

Some features:

* Class based template tags.
* Template tag argument parser.
* Declarative component attributes.
* Extendable components.
* Slot components.

.. note::

    **django-component-tags** implements a simple content distribution API inspired by the
    `Web Components spec draft <https://github.com/WICG/webcomponents/blob/gh-pages/proposals/Slots-Proposal.md>`_,
    using the ``{% slot %}`` component inside another component to serve as distribution outlets for content.

Requirements
============

Requires Django 2.2 or newer, and is tested against Python 3.7 and PyPy.


Quick Start
===========

First, install the library:

.. code-block::

    pip3 install django-component-tags

Add it to ``INSTALLED_APPS``.

.. code-block::

    INSTALLED_APPS = [
        ...
        'component_tags',
        ...
    ]

Assuming that we already have an `application <https://docs.djangoproject.com/en/3.1/intro/tutorial01/>`_
called **foo**, lets create a new component tag:

.. code-block:: python

    # foo/templatetags/foo_tags.py
    from component_tags import template

    register = template.Library()

    @register.tag
    class Link(template.Component):
        href = template.Attribute(default='#')

        class Meta:
            template_name = 'tags/link.html'



.. note::

    **django-component-tags** extends the default django template library, because it wraps component classes with a parser
    function and extracts template tag arguments, everything else is left in the same way.

    Please check out `the repository <https://github.com/syse-i/django-component-tags/blob/main/src/component_tags/template/library.py>`_
    if you want to know more about this process.

Next step, creating the component template:

.. code-block::

    # foo/templates/foo/tags/link.html

    <a {{ attributes }}>
        {{ nodelist }}
    </a>

Here we defined a couple of variables that we can use inside a component template:

* **attributes**: component template/class attributes (formatted).
* **nodelist**: the content created between ``{% link %}`` and ``{% endlink %}`` will be rendered here.

Finally, we can use it as follows:

.. code-block::

    # foo/templates/foo/index.html
    {% load foo_tags %}

    {% link %}
        Link 1
    {% endlink %}

Output:

.. code-block::

    # foo/templates/foo/index.html

    <a href="#">
        Link 1
    </a>

This is the simplest way to start, there is a lot of different settings that you can combine to create complex
html components.


Examples
========

Adding css classes
------------------

Lets create a html component using the `bootstrap framework <https://getbootstrap.com>`_

.. code-block:: python

    # foo/templatetags/foo_tags.py
    from component_tags import template

    register = template.Library()

    @register.tag
    class Link(template.Component):
        class ColorChoices(template.AttributeChoices):
            primary = 'btn btn-primary'
            secondary = 'btn btn-secondary'
            success = 'btn btn-success'
            danger = 'btn btn-danger'
            warning = 'btn btn-warning'
            info = 'btn btn-info'

        color = template.Attribute(choices=TypeChoices, default=TypeChoices.submit, as_class=True)
        href = template.Attribute(default='#')

        class Meta:
            template_name = 'tags/link.html'

Rendering the component:

.. code-block::

    # foo/templates/foo/index.html
    {% load foo_tags %}

    {% link color="primary" class="foo-bar" %}
        Link 1
    {% endlink %}

Also we added the ``class`` argument to the component tag, so even if the components strictly have class attributes,
you will always have a flexible way to customize your components any time in different scenarios.

Output:

.. code-block::

    # foo/templates/foo/index.html

    <a class="btn btn-primary foo-bar" href="#">
        Link 1
    </a>

Note that it was merged with all attribute classes previously declared.


Using slot components
---------------------

Lets make another html component using the `bootstrap framework <https://getbootstrap.com>`_,
this one is going to be a ``Card`` component.

.. code-block:: python

    # foo/templatetags/foo_tags.py
    from component_tags import template

    register = template.Library()

    @register.tag
    class Card(template.Component):
        title = template.Attribute(as_context=True)

        class Meta:
            template_name = 'tags/card.html'

Create the component template:

.. code-block::

    # foo/templates/foo/tags/card.html

    <div class="card" style="width: 18rem;">
      <img src="..." class="card-img-top" alt="...">
      <div class="card-body">
        <h5 class="card-title">{{ title }}</h5>
        <div class="card-text">
            {{ nodelist }}
        </div>
        {% if slot_footer %}
            <div class="card-footer">
                {{ slot_footer }}
            </div>
        {% endif %}
      </div>
    </div>

Rendering the component:

.. code-block::

    # foo/templates/foo/index.html
    {% load foo_tags %}

    {% card title='foo' %}
        Some quick example text to build on the card title and make up the bulk of the card's content.
        {% slot 'footer' %}
            <a href="#" class="btn btn-primary">Go somewhere</a>
        {% endslot %}
    {% endcard %}

Output:

.. code-block::

    # foo/templates/foo/index.html

    <div class="card" style="width: 18rem;">
        <img src="..." class="card-img-top" alt="...">
        <div class="card-body">
            <h5 class="card-title">foo</h5>
            <div class="card-text">
                Some quick example text to build on the card title and make up the bulk of the card's content.
            </div>
            <div class="card-footer">
                <a href="#" class="btn btn-primary">Go somewhere</a>
            </div>
        </div>
    </div>


Adding extra context
--------------------

By default, all components used isolated context to work with. If you want to pass global context to the component tag
it is required to use the ``with`` argument.

.. code-block:: python

    # foo/views.py
    def foo(request, object_id=None):
        return render(request, 'foo/index.html', {
            'object_id': object_id
        })

.. code-block::

    # foo/templates/foo/index.html
    {% load foo_tags %}

    {% link color="primary" with id=object_id %}
        Link {{ id }}
    {% endlink %}

Assuming that the request of the page will be something like ``http://localhost:8000/foo/1/``, the output will be:

.. code-block::

    # foo/templates/foo/index.html

    <a class="btn btn-primary" href="#">
        Link 1
    </a>

.. note::

    ``Slot`` components doesn't need to specify global context, they always use the parent context as default.

.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.0rc2. For details and usage
information on PyScaffold see https://pyscaffold.org/.
