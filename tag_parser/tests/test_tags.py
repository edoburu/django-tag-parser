from django.template import Context, TemplateSyntaxError
from django.template.base import Template, Token, TOKEN_TEXT, Parser, FilterExpression
from django.test import SimpleTestCase
from tag_parser.basetags import BaseNode
from tag_parser.tests.templatetags import tag_parser_test_tags as test_tags


try:
    from django.template.base import add_to_builtins  # Django 1.8-
except ImportError:
    add_to_builtins = None


class TagParserTests(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super(TagParserTests, cls).setUpClass()
        if add_to_builtins is not None:
            # Django 1.8 and below.
            # Make it easier to run tests without needing to change INSTALLED_APPS
            add_to_builtins("tag_parser.tests.templatetags.tag_parser_test_tags")

    def test_base_no_args(self):
        """
        Detect when ``@register.tag`` was used directly on the class.
        It should fail, and tell developers how to handle tags.
        """
        tag = Template('{% BaseNoArgsTag %}').nodelist[0]
        self.assertIsInstance(tag, test_tags.BaseNoArgsTag)

    def test_base_any_args(self):
        """
        Detect when ``@register.tag`` was used directly on the class.
        It should fail, and tell developers how to handle tags.
        """
        t = Template('{% BaseAnyArgsTag foo=1 bar=1 %}')
        tag = t.nodelist[0]
        self.assertIsInstance(tag, test_tags.BaseAnyArgsTag)
        self.assertIsInstance(tag.kwargs['foo'], FilterExpression)
        self.assertIsInstance(tag.kwargs['bar'], FilterExpression)

    def test_base_arguments(self):
        """
        Test whether compiled template arguments come across properly
        """
        t = Template('{% BaseArgsTag arg1 arg2 kw1=key1 kw2=key2 %}')
        tag = t.nodelist[0]

        # See if the tags are parsed correctly:
        self.assertIsInstance(tag, test_tags.BaseArgsTag)
        self.assertEqual(tag.tag_name, 'BaseArgsTag')
        self.assertEqual(len(tag.args), 2)
        self.assertEqual(sorted(tag.kwargs.keys()), ['kw1', 'kw2'])
        self.assertIsInstance(tag.args[0], FilterExpression)
        self.assertIsInstance(tag.args[1], FilterExpression)
        self.assertIsInstance(tag.kwargs['kw1'], FilterExpression)
        self.assertIsInstance(tag.kwargs['kw2'], FilterExpression)

        text = t.render(Context({'arg1': 'AA1', 'arg2': 'AA2', 'key1': 'KEY1', 'key2': 'KEY2'}))
        self.assertEqual(text, '{args: AA1 AA2 kwargs: kw1=KEY1 kw2=KEY2]}')

    def test_invalid_kwargs(self):
        with self.assertRaises(TemplateSyntaxError):
            Template('{% BaseArgsTag invalid_kwarg=1 %}')

    def test_base_repr(self):
        """
        Test whether repr shows some meaningful output (both with compile and non-compile)
        """
        class ArgsTest1(BaseNode):
            max_args = 2
            allowed_kwargs = ('kw',)

        class ArgsTest2(BaseNode):
            max_args = 2
            allowed_kwargs = ('kw',)
            compile_kwargs = False

        node = ArgsTest1.parse(parser=_get_parser(), token=Token(TOKEN_TEXT, 'ArgsTest  1  2  kw=foo|default:"1" '))
        self.assertEqual(repr(node), '<ArgsTest1: {% ArgsTest 1 2 kw=foo|default:"1" %}>')

        node = ArgsTest2.parse(parser=_get_parser(), token=Token(TOKEN_TEXT, 'ArgsTest  1  2  kw=foo|default:"1" '))
        self.assertEqual(repr(node), '<ArgsTest2: {% ArgsTest 1 2 kw=foo|default:"1" %}>')

    def test_inclusion_tag_list(self):
        """
        Test whether the inclusion tag can handle lists as template choices.
        """
        tag = Template('{% BaseInclusionTag FOOBAR|default:"123" %}')
        self.assertEqual(tag.render(Context({'FOOBAR': '456'})).strip(), '456')


def _get_parser():
    import django
    parser = Parser([])
    if django.VERSION >= (1, 9):
        import django.template.defaultfilters
        parser.add_library(django.template.defaultfilters.register)
    return parser
