from django.template import Library
from tag_parser.basetags import BaseNode

register = Library()


@register.tag('InvalidCompileTag')
class InvalidCompileTag(BaseNode):
    pass
