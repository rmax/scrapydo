import pprint
import uuid
import six

try:
    import pygments
except ImportError:
    pygments = None
else:
    import pygments.lexers
    import pygments.formatters

from IPython.display import HTML


def highlight(code, lexer='html', formatter='html', output_wrapper=None):
    """Highlights given code using pygments."""
    if not pygments:
        raise TypeError("pygments module required")
    if not isinstance(code, six.string_types):
        code = pprint.pformat(code)
    if isinstance(lexer, six.string_types):
        lexer = pygments.lexers.get_lexer_by_name(lexer)
    if isinstance(formatter, six.string_types):
        formatter = pygments.formatters.get_formatter_by_name(formatter)
        if formatter.name.lower() == 'html':
            formatter.full = True
            formatter.cssclass = "pygments-%s" % uuid.uuid4()
            if output_wrapper is None:
                output_wrapper = HTML
    return output_wrapper(pygments.highlight(code, lexer, formatter))
