"""
Decorators to write template tags
"""


def template_tag(library, name):
    """
    Decorator to register class tags

    :param library: The template tag library, typically instantiated as ``register = Library()``.
    :type library: :class:`~django.template.Library`
    :param name: The name of the template tag
    :type name: str

    Example:

    .. code-block:: python

        @template_tag(register, 'my_tag')
        class MyTag(BaseNode):
            pass
    """
    def _inner(cls):
        if hasattr(cls, 'parse'):
            compile_function = cls.parse
        else:
            # Hope that it's either a function, or cls with __init__(self, parser, token) method.
            compile_function = cls

        library.tag(name, compile_function)
        return cls  # Return the class body to keep it in the namespace of the module

    return _inner
