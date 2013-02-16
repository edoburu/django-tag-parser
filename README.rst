django-tag-parser
=================

A micro-library to easily write custom Django template tags.

Features:

* Functions to parse tags, especially: "args", "kwargs", and "as varname" syntax.
* Real OOP classes to write custom inclusion tags.

Compared to the standard Django features:

* The ``BaseInclusionNode`` can dynamically determine the template to use, while the standard ``@register.inclusion_tag`` call can't.
* The ``BaseNode`` can parse dynamic arguments where the ``@register.simple_tag`` is forced to a flat argument syntax.


Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-tag-parser

Or the current folder can be installed::

    pip install .


Examples
========

In your template tags library::

    from django.template import Library
    from tag_parser import template_tag
    from tag_parser.basetags import BaseNode, BaseInclusionNode

    register = Library()


To create tags with keyword arguments::

    @template_tag(register, 'my_tag')
    class MyTagNode(BaseNode):
        """
        My custom template node, usage::

            {% my_tag "arg1" keyword1="bar" keyword2="foo" %}
        """
        max_args = 1
        allowed_kwargs = ('keyword1', 'keyword2',)

        def render_tag(self, context, *tag_args, **tag_kwargs):
            return "Tag Output"


To create inclusion nodes where the template_name can be overwritten::

    @template_tag(register, "my_include_tag")
    class MyIncludeTag(BaseInclusionNode):
        """
        My custom inclusion node, usage::

            {% my_include_tag "foo" template="custom/example.html" %}
        """
        template_name = "mytags/example.html"

        def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
            return {
                'foo': "bar"
            }


To create custom parsing::




Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)
