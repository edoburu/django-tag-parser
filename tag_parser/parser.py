from django.template import TemplateSyntaxError
from django.template.base import Token
import re

__all__ = (
    'parse_as_var', 'parse_token_kwargs'
)


kwarg_re = re.compile('^(?P<name>\w+)=')


def parse_as_var(parser, token):
    """
    Parse the remainder of the token, to find a "as varname" statement.

    :param parser: The "parser" object that ``@register.tag`` provides.
    :type parser: :class:`~django.template.Parser`
    :param token: The "token" object that ``@register.tag`` provides.
    :type token: :class:`~django.template.Token` or splitted bits
    """
    if isinstance(token, Token):
        bits = token.split_contents()
    else:
        bits = token

    as_var = None
    if len(bits) > 2 and bits[-2] == 'as':
        bits = bits[:]
        as_var = bits.pop()
        bits.pop()  # as keyword

    return bits, as_var


def parse_token_kwargs(parser, token, allowed_kwargs=None, compile_args=True, compile_kwargs=True):
    """
    Allow the template tag arguments to be like a normal Python function, with *args and **kwargs.

    :param parser: The "parser" object that ``@register.tag`` provides.
    :type parser: :class:`~django.template.Parser`
    :param token: The "token" object that ``@register.tag`` provides.
    :type token: :class:`~django.template.Token` or splitted bits
    :param compile_args: Whether the arguments should be compiled using :func:`parser.compile_filter <django.template.Parser.compile_filter>`.
    :param compile_kwargs: Whether the keyword arguments should be compiled using :func:`parser.compile_filter <django.template.Parser.compile_filter>`.
    :param allowed_kwargs: A list of allowed keyword arguments. A value of ``None`` disables the check.
    :type allowed_kwargs: tuple
    :return: The tag name, arguments and keyword arguments.
    :rtype: tuple(tag_name, args, kwargs)
    """
    if isinstance(token, Token):
        bits = token.split_contents()
    else:
        bits = token

    expect_kwarg = False
    args = []
    kwargs = {}
    prev_bit = None

    tag_name = bits[0]

    for bit in bits[1::]:
        kwarg_match = kwarg_re.match(bit)
        if kwarg_match:
            # Keyword argument
            expect_kwarg = True
            (name, expr) = bit.split('=', 2)
            kwargs[name] = parser.compile_filter(expr) if compile_kwargs else expr
        else:
            # Still at positioned arguments.
            if expect_kwarg:
                raise TemplateSyntaxError("{0} tag may not have a non-keyword argument ({1}) after a keyword argument ({2}).".format(bits[0], bit, prev_bit))
            args.append(parser.compile_filter(bit) if compile_args else bit)

        prev_bit = bit

    # Validate the allowed arguments, to make things easier for template developers
    if allowed_kwargs is not None and kwargs:
        if not allowed_kwargs:
            raise TemplateSyntaxError("The option %s=... cannot be used in '%s'.\nNo keyword arguments are allowed.")

        for name in kwargs:
            if name not in allowed_kwargs:
                raise TemplateSyntaxError("The option %s=... cannot be used in '%s'.\nPossible options are: %s." % (name, bits[0], ", ".join(allowed_kwargs)))

    return tag_name, args, kwargs
