# -*- coding: utf-8 -*-
"""
Markdown Prism Highlight Extension For Pelican
==============================================
Extends Pelican's Markdown module and use Prism
code highlighting
"""

import sys
from pelican import signals

try:
    from .markdown_prism_fenced_code import PrismConfig, PrismFencedCodeExtension
except ImportError as e:
    PrismFencedCodeExtension = None
    print("\nMarkdown is not installed - Prism Highlight Markdown Extension disabled\n")


def init(pelicanobj):
    """Loads settings and instantiates the Python Markdown extension"""

    if not PrismFencedCodeExtension:
        return

    # Process settings
    config = process_settings(pelicanobj)

    # Configure Markdown Extension
    apply_markdown_extension(pelicanobj, config)


def process_settings(pelicanobj):
    """Handle user specified settings (see README for more details)"""

    # Default settings
    settings = {
        "default": {
            "lineno": True,
            "max-height": "30em",
        }
    }

    # Get the user specified settings
    try:
        user_settings = pelicanobj.settings['PRISM_PRESETS']
        settings.update(user_settings)
    except:
        pass

    return PrismConfig(settings)


def apply_markdown_extension(pelicanobj, config):
    """Instantiates the customized Markdown extension and disable conflict ones"""

    # Instantiate Markdown extension and append it to the current extensions
    try:
        pelicanobj.settings['MD_EXTENSIONS'].append(PrismFencedCodeExtension(config))
    except:
        sys.excepthook(*sys.exc_info())
        sys.stderr.write("\nError - md-prism-highlight failed to load\n")
        sys.stderr.flush()

def register():
    """Plugin registration"""
    signals.readers_init.connect(init)
