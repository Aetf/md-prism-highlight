"""
Prism Fenced Code Extension for Python Markdown
===============================================
This extension adds Fenced Code Blocks to Python-Markdown.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown import Extension
from markdown.preprocessors import Preprocessor
import re


class PrismConfig(object):
    """Config object that holds Prism options"""
    def __init__(self, presets=None):
        """Create a config object with presets dictionary"""
        super(PrismConfig, self).__init__()
        self.presets = presets
        self.update('preset=default')
        self.classes = []
        self.data = {}

    def _set(self, key, value):
        """Set key value"""
        if key == 'lineno':
            value = value == 'True'
            lineno_class = 'line-numbers'
            if value and lineno_class not in self.classes:
                self.classes.append(lineno_class)
            elif not value and lineno_class in self.classes:
                self.classes.remove(lineno_class)
        else:
            self.data[key] = value

    def update(self, inline):
        """Update the config with inline options string"""
        for pair in inline.strip().split(' '):
            key, value = pair.split('=')
            if key == 'preset':
                if value in self.presets:
                    for k, v in self.presets.items():
                        self._set(k, v)
            else:
                self._set(key, value)


    def pre_class(self):
        """Returns a list of classes that should be applied to pre element"""
        return self.classes

    def data_attr(self):
        """Returns a list of string in the format key=value
           that should be add to pre element as extra data attributes"""
        return ['%s="%s"' % (k, v) for k, v in self.data.items()]

class PrismFencedCodeExtension(Extension):
    """Markdown extension that provides fenced code block"""
    def __init__(self, config):
        super(PrismFencedCodeExtension, self).__init__()
        self.config = config

    def extendMarkdown(self, md, md_globals):
        """ Add PrismFencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        if 'fenced_code_block' in md.preprocessors:
            md.preprocessors['fenced_code_block'] = PrismFencedBlockPreprocessor(md, self.config)
        else:
            # fenced_code_block not loaded yet
            md.preprocessors.add('prism_fenced_code_block',
                                 PrismFencedBlockPreprocessor(md, self.config),
                                 ">normalize_whitespace")


class PrismFencedBlockPreprocessor(Preprocessor):
    FENCED_BLOCK_RE = re.compile(r'''
(?P<fence>^(?:~{3,}|`{3,}))[ ]*         # Opening ``` or ~~~
((?P<brace>\{?)(?P<lang>[a-zA-Z0-9_+-]+))?[ ]*  # Optional {, and lang
# Optional key=value pairs
(?P<pairs>([ ]+[^ \n]+=[^ \n]+)+)?[ ]*
(?P=brace)[ ]*\n                                # Optional closing }
(?P<code>.*?)(?<=\n)
(?P=fence)[ ]*$''', re.MULTILINE | re.DOTALL | re.VERBOSE)
    CODE_WRAP = '<pre class="%s" %s><code%s>%s</code></pre>'
    LANG_TAG = ' class="language-%s"'

    def __init__(self, md, config):
        super(PrismFencedBlockPreprocessor, self).__init__(md)
        self.config = config

    def run(self, lines):
        """ Match and store Fenced Code Blocks in the HtmlStash. """
        text = "\n".join(lines)
        while True:
            m = self.FENCED_BLOCK_RE.search(text)
            if m:
                lang = ''
                if m.group('lang'):
                    lang = self.LANG_TAG % m.group('lang')
                else:
                    lang = self.LANG_TAG % 'none'

                if m.group('pairs'):
                    self.config.update(m.group('pairs'))

                code = self.CODE_WRAP % (' '.join(self.config.pre_class()),
                                         ' '.join(self.config.data_attr()),
                                         lang,
                                         self._escape(m.group('code')))

                placeholder = self.markdown.htmlStash.store(code, safe=True)
                text = '%s\n%s\n%s' % (text[:m.start()],
                                       placeholder,
                                       text[m.end():])
            else:
                break
        return text.split("\n")

    def _escape(self, txt):
        """ basic html escaping """
        txt = txt.replace('&', '&amp;')
        txt = txt.replace('<', '&lt;')
        txt = txt.replace('>', '&gt;')
        txt = txt.replace('"', '&quot;')
        return txt
