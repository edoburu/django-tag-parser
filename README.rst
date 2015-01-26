django-tag-parser
=================

A micro-library to easily write custom Django template tags.

Features:

* Functions to parse tags, especially: "args", "kwargs", and "as varname" syntax.
* Real OOP classes to write custom inclusion tags.

Functions:

* ``parse_token_kwargs``: split a token into the tag name, args and kwargs.
* ``parse_as_var``: extract the "as varname" from a token.

Decorators:

* ``@template_tag``: register a class with a ``parse(parser, token)`` method as template tag.

Base classes (in ``tag_parser.basetags``):

* ``BaseNode``: A template ``Node`` object which features some basic parsing abilities.
* ``BaseInclusionNode``: a ``Node`` that has ``inclusion_tag`` like behaviour, but allows to override the ``template_name`` dynamically.
* ``BaseAssignmentOrInclusionNode``: a class that allows a ``{% get_items template="..." %}`` and ``{% get_items as var %}`` syntax.

The base classes allows to implement ``@register.simple_tag``, ``@register.inclusion_tag`` and ``@register.assignment_tag`` like functionalities,
while still leaving room to extend the parsing, rendering or syntax validation.
For example, not all arguments need to be seen as template variables, filters or literal keywords.


Installation
============

First install the module, preferably in a virtual environment. It can be installed from PyPI::

    pip install django-tag-parser

Or the current folder can be installed::

    pip install .


Examples
========

At the top of your template tags library, always include the standard
Django ``register`` variable and our ``template_tag`` decorator::

    from django.template import Library
    from tag_parser import template_tag

    register = Library()

Arguments and keyword arguments
-------------------------------

To parse a syntax like::

    {% my_tag "arg1" keyword1="bar" keyword2="foo" %}

use::

    from django.template import Library
    from tag_parser import template_tag
    from tag_parser.basetags import BaseNode

    register = Library()


    @template_tag(register, 'my_tag')
    class MyTagNode(BaseNode):
        max_args = 1
        allowed_kwargs = ('keyword1', 'keyword2',)

        def render_tag(self, context, *tag_args, **tag_kwargs):
            return "Tag Output"

Inclusion tags
--------------

To create an inclusion tag with overwritable template_name::

    {% my_include_tag "foo" template="custom/example.html" %}

use::


    from django.template import Library
    from tag_parser import template_tag
    from tag_parser.basetags import BaseInclusionNode

    register = Library()


    @template_tag(register, "my_include_tag")
    class MyIncludeTag(BaseInclusionNode):
        template_name = "mytags/default.html"
        max_args = 1

        def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
            (foo,) = *tag_args
            return {
                'foo': foo
            }

The ``get_template_name()`` method can be overwritten too to support dynamic resolving of template names.
By default it checks the ``template`` tag_kwarg, and ``template_name`` attribute.
Note the template nodes are cached afterwards, it's not possible to return random templates at each call.


Assignment tags
---------------

To create assignment tags that can either render itself, or return context data::

    {% get_tags template="custom/example.html" %}
    {% get_tags as popular_tags %}

use::

    from django.template import Library
    from tag_parser import template_tag
    from tag_parser.basetags import BaseAssignmentOrInclusionNode

    register = Library()


    @template_tag(register, 'get_tags')
    class GetPopularTagsNode(BaseAssignmentOrInclusionNode):
        template_name = "myblog/templatetags/popular_tags.html"
        context_value_name = 'tags'
        allowed_kwargs = (
            'order', 'orderby', 'limit',
        )

        def get_value(self, context, *tag_args, **tag_kwargs):
            return query_tags(**tag_kwargs)   # Something that reads the tags.


Block tags
----------

To have a "begin .. end" block, define ``end_tag_name`` in the class::

    {% my_tag keyword1=foo %}
        Tag contents, possibly other tags.
    {% end_my_tag %}

use::

    from django.template import Library
    from tag_parser import template_tag
    from tag_parser.basetags import BaseAssignmentOrInclusionNode

    register = Library()


    @template_tag(register, 'my_tag')
    class MyTagNode(BaseNode):
        max_args = 1
        allowed_kwargs = ('keyword1', 'keyword2',)
        end_tag_name = 'end_my_tag'

        def render_tag(self, context, *tag_args, **tag_kwargs):
            # Render contents inside
            return self.nodelist.render(context)


Custom parsing
--------------

With the standard ``Node`` class from Django, it's easier to implement custom syntax.
For example, to parse::

    {% getfirstof val1 val2 as val3 %}

use::

    from django.template import Library, Node, TemplateSyntaxError
    from tag_parser import template_tag, parse_token_kwargs, parse_as_var

    register = Library()


    @template_tag(register, 'getfirstof')
    class GetFirstOfNode(Node):
        def __init__(self, options, as_var):
            self.options = options    # list of FilterExpression nodes.
            self.as_var = as_var

        @classmethod
        def parse(cls, parser, token):
            bits, as_var = parse_as_var(parser, token)
            tag_name, options, _ = parse_token_kwargs(parser, bits, allowed_kwargs=())

            if as_var is None or not choices:
                raise TemplateSyntaxError("Expected syntax: {{% {0} val1 val2 as val %}}".format(tag_name))

            return cls(options, as_var)

        def render(self, context):
            value = None
            for filterexpr in self.options:
                # The ignore_failures argument prevents that the value becomes TEMPLATE_STRING_IF_INVALID.
                value = filterexpr.resolve(context, ignore_failures=True)
                if value is not None:
                    break

            context[self.as_var] = value
            return ''



Contributing
------------

This module is designed to be generic. In case there is anything you didn't like about it,
or think it's not flexible enough, please let us know. We'd love to improve it!

If you have any other valuable contribution, suggestion or idea,
please let us know as well because we will look into it.
Pull requests are welcome too. :-)
