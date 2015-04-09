import django
from django.core.exceptions import ImproperlyConfigured
from django.template.base import Template
from django.template import Node, Context, TemplateSyntaxError
from django.template.loader import get_template
from django.utils import six
from django.utils.itercompat import is_iterable
from tag_parser.parser import parse_token_kwargs, parse_as_var


__all__ = (
    'BaseNode', 'BaseInclusionNode'
)


class BaseNode(Node):
    """
    Base class for template tag nodes.

    Plain style:

    .. code-block:: python

        class MyTag(BaseNode):
            def render_tag(self, context, *args, **kwargs):
                return "Tag output"

        register.tag('my_tag', MyTag.parse)

    or classical style:

    .. code-block:: python

        @register.tag
        def my_tag(parser, token):
            return MyTag.parse(parser, token)

    or using the decorator:

    .. code-block:: python

        @template_tag(register, 'my_tag')
        class MyTag(BaseNode):
            def render_tag(self, context, *args, **kwargs):
                return "Tag output"
    """
    #: The names of the allowed keyword arguments in the template tag.
    allowed_kwargs = ()

    #: If you want that it this will also parse the text until the end tag,
    #: and store that in ``self.nodelist``.
    end_tag_name = None

    #: The minimum number of required positional arguments. Use ``None`` to disable the check.
    min_args = 0

    #: The maximum number of allowed positional arguments. Use ``None`` for infinite.
    max_args = 0

    #: Whether the parser should treat the arguments as filter expressions.
    compile_args = True

    #: Whether the parser should treat the keyword arguments as filter expressions.
    compile_kwargs = True


    def __init__(self, tag_name, *args, **kwargs):
        """
        The constructor receives the parsed arguments.
        The values are stored in :attr:`tagname`, :attr:`args`, :attr:`kwargs`.
        """
        if self.end_tag_name and 'nodelist' in kwargs:
            self.nodelist = kwargs.pop('nodelist')
        self.tag_name = tag_name  # May differ from cls.tag_name, and doesn't affect the 'cls' attribute at all.
        self.args = args
        self.kwargs = kwargs


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the tag, instantiate the class.
        """
        # There is no __init__(self, parser, token) method in this class design
        # to discourage the @register.tag decorator on the class because that prevents tag inheritance.
        tag_name, args, kwargs = parse_token_kwargs(
            parser, token,
            allowed_kwargs=cls.allowed_kwargs,
            compile_args=cls.compile_args,
            compile_kwargs=cls.compile_kwargs
        )
        cls.validate_args(tag_name, *args, **kwargs)
        if cls.end_tag_name:
            kwargs['nodelist'] = parser.parse((cls.end_tag_name,))
            parser.delete_first_token()

        return cls(tag_name, *args, **kwargs)


    def render(self, context):
        """
        The default Django render() method for the tag.

        This method resolves the filter expressions, and calls :func:`render_tag`.
        """
        # Resolve token kwargs
        tag_args = [expr.resolve(context) for expr in self.args] if self.compile_args else self.args
        tag_kwargs = dict([(name, expr.resolve(context)) for name, expr in six.iteritems(self.kwargs)]) if self.compile_kwargs else self.kwargs

        return self.render_tag(context, *tag_args, **tag_kwargs)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        """
        Render the tag, with all arguments resolved to their actual values.
        """
        raise NotImplementedError("{0}.render_tag() is not implemented!".format(self.__class__.__name__))


    @classmethod
    def validate_args(cls, tag_name, *args, **kwargs):
        """
        Validate the syntax of the template tag.
        """
        if cls.min_args is not None and len(args) < cls.min_args:
            if cls.min_args == 1:
                raise TemplateSyntaxError("'{0}' tag requires at least {1} argument".format(tag_name, cls.min_args))
            else:
                raise TemplateSyntaxError("'{0}' tag requires at least {1} arguments".format(tag_name, cls.min_args))

        if cls.max_args is not None and len(args) > cls.max_args:
            if cls.max_args == 0:
                if cls.allowed_kwargs:
                    raise TemplateSyntaxError("'{0}' tag only allows keywords arguments, for example {1}=\"...\".".format(tag_name, cls.allowed_kwargs[0]))
                else:
                    raise TemplateSyntaxError("'{0}' tag doesn't support any arguments".format(tag_name))
            elif cls.max_args == 1:
                raise TemplateSyntaxError("'{0}' tag only allows {1} argument.".format(tag_name, cls.max_args))
            else:
                raise TemplateSyntaxError("'{0}' tag only allows {1} arguments.".format(tag_name, cls.max_args))


    def get_request(self, context):
        """
        Fetch the request from the context.

        This enforces the use of a RequestProcessor, e.g.
        ::

            render_to_response("page.html", context, context_instance=RequestContext(request))
        """
        if 'request' not in context:
            # This error message is issued to help newcomers find solutions faster!
            raise ImproperlyConfigured(
                "The '{0}' tag requires a 'request' variable in the template context.\n" \
                "Make sure 'RequestContext' is used and 'TEMPLATE_CONTEXT_PROCESSORS' includes 'django.core.context_processors.request'.".format(self.tag_name)
            )

        return context['request']



class BaseInclusionNode(BaseNode):
    """
    Base class to render a template tag with a template.

    This class allows more flexibility then Django's default :func:`django.template.Library.inclusion_tag` decorator.

    It allows specify the template name via:

    * a static ``template_name`` property.
    * a ``get_template_name()`` method
    * a 'template' kwarg in the HTML.

    The :func:`get_context_data` function should be overwritten to provide the required context.
    """
    template_name = None
    allowed_kwargs = ('template',)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        data = self.get_context_data(context, *tag_args, **tag_kwargs)
        new_context = self.get_context(context, data)

        if django.VERSION >= (1,8):
            t = context.render_context.get(self)
            if t is None:
                file_name = self.get_template_name(*tag_args, **tag_kwargs)

                if isinstance(file_name, Template):
                    t = file_name
                elif isinstance(getattr(file_name, 'template', None), Template):
                    t = file_name.template
                elif not isinstance(file_name, six.string_types) and is_iterable(file_name):
                    t = context.template.engine.select_template(file_name)
                else:
                    t = context.template.engine.get_template(file_name)
                context.render_context[self] = t

            return t.render(new_context)
        else:
            # Get template nodes, and cache it.
            # Note that self.nodelist has a special meaning in the Node base class.
            if not getattr(self, 'nodelist', None):
                file_name = self.get_template_name(*tag_args, **tag_kwargs)
                tpl = get_template(file_name)
                self.nodelist = tpl.nodelist

            # Render the node
            return self.nodelist.render(new_context)


    def get_template_name(self, *tag_args, **tag_kwargs):
        """
        Get the template name, by default using the :attr:`template_name` attribute.
        """
        return tag_kwargs.get('template', self.template_name)


    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        """
        Return the context data for the included template.
        """
        raise NotImplementedError("{0}.get_context_data() is not implemented.".format(self.__class__.__name__))


    def get_context(self, parent_context, data):
        """
        Wrap the context data in a :class:`~django.template.Context` object.

        :param parent_context: The context of the parent template.
        :type parent_context: :class:`~django.template.Context`
        :param data: The result from :func:`get_context_data`
        :type data: dict
        :return: Context data.
        :rtype: :class:`~django.template.Context`
        """
        if django.VERSION >= (1,8):
            new_context = parent_context.new(data)
        else:
            settings = {
                'autoescape': parent_context.autoescape,
                'current_app': parent_context.current_app,
                'use_l10n': parent_context.use_l10n,
                'use_tz': parent_context.use_tz,
            }
            new_context = Context(data, **settings)

        # Pass CSRF token for same reasons as @register.inclusion_tag does.
        csrf_token = parent_context.get('csrf_token', None)
        if csrf_token is not None:
            new_context['csrf_token'] = csrf_token

        return new_context


class BaseAssignmentNode(BaseNode):
    """
    Base assignment node for an ``as var`` syntax.
    """
    def __init__(self, tag_name, as_var, *args, **kwargs):
        super(BaseAssignmentNode, self).__init__(tag_name, *args, **kwargs)
        self.as_var = as_var


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the "as var" syntax.
        """
        bits, as_var = parse_as_var(parser, token)
        tag_name, args, kwargs = parse_token_kwargs(parser, bits, cls.allowed_kwargs, compile_args=cls.compile_args, compile_kwargs=cls.compile_kwargs)

        # Pass through standard chain
        cls.validate_args(tag_name, *args)
        return cls(tag_name, as_var, *args, **kwargs)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        """
        Rendering of the tag. It either assigns the value as variable, or renders it.
        """
        if self.as_var:
            # Assign the value in the parent context
            context[self.as_var] = self.get_value(context, *tag_args, **tag_kwargs)

        return u''


    def get_value(self, context, *tag_args, **tag_kwargs):
        """
        Return the value for the tag.

        :param tag_args:
        :param tag_kwargs:
        """
        raise NotImplementedError("{0}.get_value() is not implemented'.".format(self.__class__.__name__))


class BaseAssignmentOrOutputNode(BaseAssignmentNode):
    """
    Base class to assign a value, or output it.
    This works like ``{% trans .. %}`` and ``{% url .. %}`` which both optionally
    have an ``as var`` syntax; ``{% trans .. as .. %}`` and ``{% url .. as .. %}``.
    """

    def render_tag(self, context, *tag_args, **tag_kwargs):
        if self.as_var:
            return super(BaseAssignmentOrOutputNode, self).render_tag(context, *tag_args, **tag_kwargs)
        else:
            return self.get_value(context, *tag_args, **tag_kwargs)


class BaseAssignmentOrInclusionNode(BaseInclusionNode, BaseAssignmentNode):
    """
    Base class to either assign a tag, or render it using a template.
    """
    context_value_name = 'value'


    @classmethod
    def parse(cls, parser, token):
        """
        Parse the "as var" syntax.
        """
        bits, as_var = parse_as_var(parser, token)
        tag_name, args, kwargs = parse_token_kwargs(parser, bits, ('template',) + cls.allowed_kwargs, compile_args=cls.compile_args, compile_kwargs=cls.compile_kwargs)

        # Pass through standard chain
        cls.validate_args(tag_name, *args)
        return cls(tag_name, as_var, *args, **kwargs)


    def render_tag(self, context, *tag_args, **tag_kwargs):
        """
        Rendering of the tag. It either assigns the value as variable, or renders it.
        """
        # Be very explicit about which base functionality is used:
        # Using super() for mixin support will not work nicely anyway here.
        if self.as_var:
            # Assign the value in the parent context
            return BaseAssignmentNode.render_tag(self, context, *tag_args, **tag_kwargs)
        else:
            # Render the output using the BaseInclusionNode features
            return BaseInclusionNode.render_tag(self, context, *tag_args, **tag_kwargs)


    def get_context_data(self, parent_context, *tag_args, **tag_kwargs):
        """
        Return the context data for the inclusion tag.

        Returns ``{'value': self.get_value(parent_context, *tag_args, **tag_kwargs)}`` by default.
        """
        if 'template' not in self.allowed_kwargs:
            # The overwritten get_value() doesn't have to take care of our customly inserted tag parameters,
            # It can safely assume passing **tag_kwargs to another function.
            tag_kwargs.pop('template', None)

        return {
            self.context_value_name: self.get_value(parent_context, *tag_args, **tag_kwargs)
        }
