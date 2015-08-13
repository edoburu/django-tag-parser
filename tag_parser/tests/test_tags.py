from django.template.base import add_to_builtins, Template, Token, TOKEN_TEXT, Parser
from django.test import SimpleTestCase
from tag_parser.basetags import BaseNode


class TagParserTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        # Make it easier to run tests without needing to change INSTALLED_APPS
        add_to_builtins("tag_parser.tests.templatetags.tag_parser_test_tags")

    def test_invalid_register(self):
        """
        Detect when ``@register.tag`` was used directly on the class.
        It should fail, and tell developers how to handle tags.
        """
        self.assertRaisesRegexp(TypeError, 'use @template_tag', lambda: Template('{% InvalidCompileTag %}'))

    def test_repr(self):
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

        node = ArgsTest1.parse(parser=Parser([]), token=Token(TOKEN_TEXT, 'ArgsTest  1  2  kw=foo|default:"1" '))
        self.assertEqual(repr(node), '<ArgsTest1: {% ArgsTest 1 2 kw=foo|default:"1" %}>')

        node = ArgsTest2.parse(parser=Parser([]), token=Token(TOKEN_TEXT, 'ArgsTest  1  2  kw=foo|default:"1" '))
        self.assertEqual(repr(node), '<ArgsTest2: {% ArgsTest 1 2 kw=foo|default:"1" %}>')
