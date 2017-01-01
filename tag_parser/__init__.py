from .decorators import template_tag
from .parser import parse_token_kwargs, parse_as_var

__all__ = (
    'template_tag', 'parse_token_kwargs', 'parse_as_var',
)

# following PEP 440
__version__ = "3.1"
