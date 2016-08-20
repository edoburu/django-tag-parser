from django.template import Library
from tag_parser.basetags import BaseNode

register = Library()


@register.tag('BaseNoArgsTag')
class BaseNoArgsTag(BaseNode):
    pass



@register.tag('BaseAnyArgsTag')
class BaseAnyArgsTag(BaseNode):
    allowed_kwargs = None  # disable check


@register.tag('BaseArgsTag')
class BaseArgsTag(BaseNode):
    min_args = 1
    max_args = 3
    allowed_kwargs = ('kw1', 'kw2')

    def render_tag(self, context, *tag_args, **tag_kwargs):
        return '{{args: {0} kwargs: {1}]}}'.format(
            ' '.join(tag_args),
            ' '.join('{0}={1}'.format(k,v) for k,v in sorted(tag_kwargs.items()))
        )

