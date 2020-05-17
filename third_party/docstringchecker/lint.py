# -*- coding: utf-8 -*-
# Copyright (c) 2013 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This module is not automatically loaded by the `cros` helper.  The filename
# would need a "cros_" prefix to make that happen.  It lives here so that it
# is alongside the cros_lint.py file.
#
# For msg namespaces, the 9xxx should generally be reserved for our own use.

"""Additional lint modules loaded by pylint.

This is loaded by pylint directly via its pylintrc file:
  load-plugins=chromite.cli.cros.lint

Then pylint will import the register function and call it.  So we can have
as many/few checkers as we want in this one module.
"""

from __future__ import print_function

import collections
import tokenize
import os
import re
import sys

import pylint.checkers
from pylint.config import ConfigurationMixIn
import pylint.interfaces

from chromite.utils import memoize


_THIRD_PARTY = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '..', '..', 'third_party')
_PYLINT_QUOTES = os.path.join(_THIRD_PARTY, 'pylint-quotes')
sys.path.insert(0, _PYLINT_QUOTES)
# pylint: disable=unused-import,wrong-import-position
from pylint_quotes.checker import StringQuoteChecker


# pylint: disable=too-few-public-methods


class DocStringSectionDetails(object):
  """Object to hold details about a docstring section.

  e.g. This holds the Args: or Returns: data.
  """

  def __init__(self, name=None, header=None, lines=None, lineno=None):
    """Initialize.

    Args:
      name: The name of this section, e.g. "Args".
      header: The raw header of this section, e.g. "  Args:".
      lines: The raw lines making up the section.
      lineno: The first line of the section in the overall docstring.
        This counts from one and includes the section header line.
    """
    self.name = name
    self.header = header
    self.lines = [] if lines is None else lines
    self.lineno = lineno

  def __str__(self):
    """A human readable string for this object."""
    return 'DocStringSectionDetails(%r, %r)' % (self.name, self.lineno)

  def __repr__(self):
    """A string to quickly identify this object."""
    return 'DocStringSectionDetails(%r, %r, %r, %r)' % (
        self.name, self.header, self.lines, self.lineno,
    )

  def __eq__(self, other):
    """Test whether two DocStringSectionDetails objects are equivalent"""
    return (
        self.name == other.name and
        self.header == other.header and
        self.lines == other.lines and
        self.lineno == other.lineno
    )


def _PylintrcConfig(config_file, section, opts):
  """Read specific pylintrc settings.

  This is a bit hacky.  The pylint framework doesn't allow us to access options
  outside of a Checker's own namespace (self.name), and multiple linters may not
  have the same name/options values (since they get globally registered).  So we
  have to re-read the registered config file and pull out the value we want.

  The other option would be to force people to duplicate settings in the config
  files and that's worse.  e.g.
  [format]
  indent-string = '  '
  [doc_string_checker]
  indent-string = '  '

  Args:
    config_file: Path to the pylintrc file to read.
    section: The section to read.
    opts: The specific settings to return.

  Returns:
    A pylint configuration object.  Use option_value('...') to read.
  """
  class ConfigReader(ConfigurationMixIn):
    """Dynamic config file reader."""
    name = section
    options = opts

  cfg = ConfigReader(config_file=config_file)
  cfg.read_config_file()
  cfg.load_config_file()
  return cfg


class DocStringChecker(pylint.checkers.BaseChecker):
  """PyLint AST based checker to verify PEP 257 compliance

  See our style guide for more info:
  https://dev.chromium.org/chromium-os/python-style-guidelines#TOC-Describing-arguments-in-docstrings
  """

  # TODO: See about merging with the pep257 project:
  # https://github.com/GreenSteam/pep257

  __implements__ = pylint.interfaces.IAstroidChecker

  # pylint: disable=class-missing-docstring,multiple-statements
  class _MessageCP001(object): pass
  class _MessageCP002(object): pass
  class _MessageCP003(object): pass
  class _MessageCP004(object): pass
  class _MessageCP005(object): pass
  class _MessageCP006(object): pass
  class _MessageCP007(object): pass
  class _MessageCP008(object): pass
  class _MessageCP009(object): pass
  class _MessageCP010(object): pass
  class _MessageCP011(object): pass
  class _MessageCP012(object): pass
  class _MessageCP013(object): pass
  class _MessageCP014(object): pass
  class _MessageCP015(object): pass
  class _MessageCP016(object): pass
  class _MessageCP017(object): pass
  class _MessageCP018(object): pass
  # pylint: enable=class-missing-docstring,multiple-statements

  # All the sections we recognize (and in this order).
  VALID_FUNC_SECTIONS = ('Examples', 'Args', 'Returns', 'Yields', 'Raises')
  VALID_CLASS_SECTIONS = ('Examples', 'Attributes')
  ALL_VALID_SECTIONS = set(VALID_FUNC_SECTIONS + VALID_CLASS_SECTIONS)

  # This is the section name in the pylintrc file.
  name = 'doc_string_checker'
  # Any pylintrc config options we accept.
  options = ()
  priority = -1
  MSG_ARGS = 'offset:%(offset)i: {%(line)s}'
  msgs = {
      'C9001': ('Modules should have docstrings (even a one liner)',
                ('module-missing-docstring'), _MessageCP001),
      'C9002': ('Classes should have docstrings (even a one liner)',
                ('class-missing-docstring'), _MessageCP002),
      'C9003': ('Trailing whitespace in docstring: ' + MSG_ARGS,
                ('docstring-trailing-whitespace'), _MessageCP003),
      'C9004': ('Leading whitespace in docstring (excess or missing)'
                ': ' + MSG_ARGS,
                ('docstring-leading-whitespace'), _MessageCP004),
      'C9005': ('Closing triple quotes should not be cuddled',
                ('docstring-cuddled-quotes'), _MessageCP005),
      'C9006': ('Section names should be preceded by one blank line'
                ': ' + MSG_ARGS,
                ('docstring-section-newline'), _MessageCP006),
      'C9007': ('Section names should be "%(section)s": ' + MSG_ARGS,
                ('docstring-section-name'), _MessageCP007),
      'C9008': ('Sections should be in the order: %(sections)s',
                ('docstring-section-order'), _MessageCP008),
      'C9009': ('First line should be a short summary',
                ('docstring-first-line'), _MessageCP009),
      'C9010': ('Not all args mentioned in doc string: |%(arg)s|',
                ('docstring-missing-args'), _MessageCP010),
      'C9011': ('Variable args/keywords are named *args/**kwargs, not %(arg)s',
                ('docstring-misnamed-args'), _MessageCP011),
      'C9012': ('Incorrectly formatted Args section: %(arg)s',
                ('docstring-arg-spacing'), _MessageCP012),
      'C9013': ('Too many blank lines in a row: ' + MSG_ARGS,
                ('docstring-too-many-newlines'), _MessageCP013),
      'C9014': ('Second line should be blank',
                ('docstring-second-line-blank'), _MessageCP014),
      'C9015': ('Section indentation should be %(want_indent)s spaces, not '
                '%(curr_indent)s spaces: ' + MSG_ARGS,
                ('docstring-section-indent'), _MessageCP015),
      'C9016': ('Closing triple quotes should be indented with %(want_indent)s '
                'spaces, not %(curr_indent)s',
                ('docstring-trailing-quotes'), _MessageCP016),
      'C9017': ('Section %(section)s shows up more than once; previous at '
                '%(line_old)i',
                ('docstring-duplicate-section'), _MessageCP017),
      'C9018': ('Docstrings must start with exactly three quotes',
                ('docstring-extra-quotes'), _MessageCP018),
  }

  def __init__(self, *args, **kwargs):
    pylint.checkers.BaseChecker.__init__(self, *args, **kwargs)

    if self.linter is None:
      # Unit tests don't set this up.
      self._indent_string = '  '
    else:
      cfg = _PylintrcConfig(self.linter.config_file, 'format',
                            (('indent-string', {'default': '    ',
                                                'type': 'string'}),))
      self._indent_string = cfg.option_value('indent-string')
    self._indent_len = len(self._indent_string)

  def visit_functiondef(self, node):
    """Verify function docstrings"""
    if node.doc:
      lines = node.doc.split('\n')
      self._check_common(node, lines)
      sections = self._parse_docstring_sections(node, lines)
      self._check_section_lines(node, lines, sections, self.VALID_FUNC_SECTIONS)
      self._check_all_args_in_doc(node, lines, sections)
      self._check_func_signature(node)
    else:
      # This is what C0111 already does for us, so ignore.
      pass

  def visit_module(self, node):
    """Verify module docstrings"""
    if node.doc:
      self._check_common(node)
    else:
      # Ignore stub __init__.py files.
      if os.path.basename(node.file) == '__init__.py':
        return
      self.add_message('C9001', node=node)

  def visit_classdef(self, node):
    """Verify class docstrings"""
    if node.doc:
      lines = node.doc.split('\n')
      self._check_common(node, lines)
      sections = self._parse_docstring_sections(node, lines)
      self._check_section_lines(node, lines, sections,
                                self.VALID_CLASS_SECTIONS)
    else:
      self.add_message('C9002', node=node, line=node.fromlineno)

  def _docstring_indent(self, node):
    """How much a |node|'s docstring should be indented"""
    if node.display_type() == 'Module':
      return 0
    else:
      return node.col_offset + self._indent_len

  def _check_common(self, node, lines=None):
    """Common checks we enforce on all docstrings"""
    if lines is None:
      lines = node.doc.split('\n')

    funcs = (
        self._check_first_line,
        self._check_second_line_blank,
        self._check_whitespace,
        self._check_last_line,
    )
    for f in funcs:
      f(node, lines)

  def _check_first_line(self, node, lines):
    """Make sure first line is a short summary by itself"""
    if lines[0] == '':
      self.add_message('C9009', node=node, line=node.fromlineno)

    # We only check the first line for extra quotes because the grammar halts
    # when it sees the next set of triple quotes (which means extra trailing
    # quotes are not part of the docstring).
    if lines[0].startswith('"'):
      self.add_message('C9018', node=node, line=node.fromlineno)

  def _check_second_line_blank(self, node, lines):
    """Make sure the second line is blank"""
    if len(lines) > 1 and lines[1] != '':
      self.add_message('C9014', node=node, line=node.fromlineno)

  def _check_whitespace(self, node, lines):
    """Verify whitespace is sane"""
    # Make sure first line doesn't have leading whitespace.
    if lines[0].lstrip() != lines[0]:
      margs = {'offset': 0, 'line': lines[0]}
      self.add_message('C9004', node=node, line=node.fromlineno, args=margs)

    # Verify no trailing whitespace.
    # We skip the last line since it's supposed to be pure whitespace.
    #
    # Also check for multiple blank lines in a row.
    last_blank = False
    for i, l in enumerate(lines[:-1]):
      margs = {'offset': i, 'line': l}

      if l.rstrip() != l:
        self.add_message('C9003', node=node, line=node.fromlineno, args=margs)

      curr_blank = l == ''
      if last_blank and curr_blank:
        self.add_message('C9013', node=node, line=node.fromlineno, args=margs)
      last_blank = curr_blank

    # Now specially handle the last line.
    l = lines[-1]
    if l.strip() != '' and l.rstrip() != l:
      margs = {'offset': len(lines), 'line': l}
      self.add_message('C9003', node=node, line=node.fromlineno, args=margs)

  def _check_last_line(self, node, lines):
    """Make sure last line is all by itself"""
    if len(lines) > 1:
      indent = self._docstring_indent(node)

      if lines[-1].strip() != '':
        self.add_message('C9005', node=node, line=node.fromlineno)
      elif lines[-1] != ' ' * indent:
        # The -1 line holds the """ itself and that should be indented.
        margs = {
            'offset': len(lines) - 1,
            'line': lines[-1],
            'want_indent': indent,
            'curr_indent': len(lines[-1]),
        }
        self.add_message('C9016', node=node, line=node.fromlineno, args=margs)

      # The last line should not be blank.
      if lines[-2] == '':
        margs = {'offset': len(lines) - 2, 'line': lines[-2]}
        self.add_message('C9003', node=node, line=node.fromlineno, args=margs)

  @memoize.MemoizedSingleCall
  def _invalid_sections_map(self):
    """Get a mapping from common invalid section names to the valid name."""
    invalid_sections_sets = {
        # Handle common misnamings.
        'Examples': {'example', 'exaple', 'exaples', 'usage', 'example usage'},
        'Attributes': {
            'attr', 'attrs', 'attribute',
            'prop', 'props', 'properties',
            'member', 'members',
        },
        'Args': {'arg', 'argument', 'arguments'},
        'Returns': {
            'ret', 'rets', 'return', 'retrun', 'retruns', 'result', 'results',
        },
        'Yields': {'yield', 'yeild', 'yeilds'},
        'Raises': {'raise', 'riase', 'riases', 'throw', 'throws'},
    }

    invalid_sections_map = {}
    for key, value in invalid_sections_sets.items():
      invalid_sections_map.update((v, key) for v in value)
    return invalid_sections_map

  def _parse_docstring_sections(self, node, lines):
    """Find all the sections and return them

    Args:
      node: The python object we're checking.
      lines: Parsed docstring lines.

    Returns:
      An ordered dict of sections and their (start, end) line numbers.
      The start line does not include the section header itself.
      {'Args': [start_line_number, end_line_number], ...}
    """
    sections = collections.OrderedDict()
    invalid_sections_map = self._invalid_sections_map()
    indent_len = self._docstring_indent(node)

    in_args_section = False
    last_section = None
    for lineno, line in enumerate(lines[1:], start=2):
      line_indent_len = len(line) - len(line.lstrip(' '))
      margs = {
          'offset': lineno,
          'line': line,
      }
      l = line.strip()

      # Catch semi-common javadoc style.
      if l.startswith('@param'):
        margs['section'] = 'Args'
        self.add_message('C9007', node=node, line=node.fromlineno, args=margs)
      if l.startswith('@return'):
        margs['section'] = 'Returns'
        self.add_message('C9007', node=node, line=node.fromlineno, args=margs)

      # See if we can detect incorrect behavior.
      section = l.split(':', 1)[0]

      # Remember whether we're currently in the Args: section so we don't treat
      # named arguments as sections (e.g. a function has a "returns" arg).  Use
      # the indentation level to detect the start of the next section.
      if in_args_section:
        in_args_section = (indent_len < line_indent_len)

      if not in_args_section:
        # We only parse known invalid & valid sections here.  This avoids
        # picking up things that look like sections but aren't (e.g. "Note:"
        # lines), and avoids running checks on sections we don't yet support.
        if section.lower() in invalid_sections_map:
          margs['section'] = invalid_sections_map[section.lower()]
          self.add_message('C9007', node=node, line=node.fromlineno, args=margs)
        elif section in self.ALL_VALID_SECTIONS:
          if section in sections:
            # We got the same section more than once?
            margs_copy = margs.copy()
            margs_copy.update({
                'line_old': sections[section].lineno,
                'section': section,
            })
            self.add_message('C9017', node=node, line=node.fromlineno,
                             args=margs_copy)
          else:
            # Gather the order of the sections.
            sections[section] = last_section = DocStringSectionDetails(
                name=section, header=line, lineno=lineno)

        # Detect whether we're in the Args section once we've processed the Args
        # section itself.
        in_args_section = (section in ('Args', 'Attributes'))

      if l == '' and last_section:
        last_section.lines = lines[last_section.lineno:lineno - 1]
        last_section = None

    return sections

  def _check_section_lines(self, node, lines, sections, valid_sections):
    """Verify each section (e.g. Args/Returns/etc...) is sane"""
    indent_len = self._docstring_indent(node)

    # Make sure the sections are in the right order.
    found_sections = [x for x in valid_sections if x in sections]
    if found_sections != list(sections):
      margs = {'sections': ', '.join(valid_sections)}
      self.add_message('C9008', node=node, line=node.fromlineno, args=margs)

    for section in sections.values():
      # We're going to check the section line itself.
      lineno = section.lineno
      line = section.header
      want_indent = indent_len + self._indent_len
      line_indent_len = len(line) - len(line.lstrip(' '))
      margs = {
          'offset': lineno,
          'line': line,
          'want_indent': want_indent,
          'curr_indent': line_indent_len,
      }

      # Make sure it has some number of leading whitespace.
      if not line.startswith(' '):
        self.add_message('C9004', node=node, line=node.fromlineno, args=margs)

      # Make sure it has a single trailing colon.
      if line.strip() != '%s:' % section.name:
        margs['section'] = section.name
        self.add_message('C9007', node=node, line=node.fromlineno, args=margs)

      # Verify blank line before it.  We use -2 because lineno counts from one,
      # but lines is a zero-based list.
      if lines[lineno - 2] != '':
        self.add_message('C9006', node=node, line=node.fromlineno, args=margs)

      # Check the indentation level on the section header (e.g. Args:).
      if line_indent_len != indent_len:
        self.add_message('C9015', node=node, line=node.fromlineno, args=margs)

      # Now check the indentation of subtext in each section.
      saw_exact = False
      for i, line in enumerate(section.lines, start=1):
        # Every line should be indented at least the minimum.
        # Always update margs so that if we drop through below, it has
        # reasonable values when generating the message.
        line_indent_len = len(line) - len(line.lstrip(' '))
        margs.update({
            'line': line,
            'offset': lineno + i,
            'curr_indent': line_indent_len,
        })
        if line_indent_len == want_indent:
          saw_exact = True
        elif line_indent_len < want_indent:
          self.add_message('C9015', node=node, line=node.fromlineno, args=margs)

      # If none of the lines were indented at the exact level, then something
      # is amiss like they're all incorrectly offset.
      if not saw_exact:
        self.add_message('C9015', node=node, line=node.fromlineno, args=margs)

  def _check_all_args_in_doc(self, node, _lines, sections):
    """All function arguments are mentioned in doc"""
    if not hasattr(node, 'argnames'):
      return

    # If they don't have an Args section, then give it a pass.
    section = sections.get('Args')
    if section is None:
      return

    # Now verify all args exist.
    # TODO: Should we verify arg order matches doc order ?
    # TODO: Should we check indentation of wrapped docs ?
    missing_args = []
    for arg in node.args.args:
      # Ignore class related args.
      if arg.name in ('cls', 'self'):
        continue
      # Ignore ignored args.
      if arg.name.startswith('_'):
        continue

      # Valid arguments may look like `<arg>:` or `<arg> (<type>):`.
      arg_re = re.compile(r'%s( \([^)]+\))?:' % re.escape(arg.name))
      for l in section.lines:
        aline = l.lstrip()
        m = arg_re.match(aline)
        if m:
          amsg = aline[m.end():]
          if amsg and len(amsg) - len(amsg.lstrip()) != 1:
            margs = {'arg': l}
            self.add_message('C9012', node=node, line=node.fromlineno,
                             args=margs)
          break
      else:
        missing_args.append(arg.name)

    if missing_args:
      margs = {'arg': '|, |'.join(missing_args)}
      self.add_message('C9010', node=node, line=node.fromlineno, args=margs)

  def _check_func_signature(self, node):
    """Require *args to be named args, and **kwargs kwargs"""
    vararg = node.args.vararg
    if vararg and vararg != 'args' and vararg != '_args':
      margs = {'arg': vararg}
      self.add_message('C9011', node=node, line=node.fromlineno, args=margs)

    kwarg = node.args.kwarg
    if kwarg and kwarg != 'kwargs' and kwarg != '_kwargs':
      margs = {'arg': kwarg}
      self.add_message('C9011', node=node, line=node.fromlineno, args=margs)


class Py3kCompatChecker(pylint.checkers.BaseChecker):
  """Make sure we enforce py3k compatible features"""

  __implements__ = pylint.interfaces.IAstroidChecker

  # pylint: disable=class-missing-docstring,multiple-statements
  class _MessageR9100(object): pass
  # pylint: enable=class-missing-docstring,multiple-statements

  name = 'py3k_compat_checker'
  priority = -1
  MSG_ARGS = 'offset:%(offset)i: {%(line)s}'
  msgs = {
      'R9100': ('Missing "from __future__ import print_function" line',
                ('missing-print-function'), _MessageR9100),
  }
  options = ()

  def __init__(self, *args, **kwargs):
    super(Py3kCompatChecker, self).__init__(*args, **kwargs)
    self.seen_print_func = False
    self.saw_imports = False

  def close(self):
    """Called when done processing module"""
    if not self.seen_print_func:
      # Do not warn if moduler doesn't import anything at all (like
      # empty __init__.py files).
      if self.saw_imports:
        self.add_message('R9100')

  def _check_print_function(self, node):
    """Verify print_function is imported"""
    if node.modname == '__future__':
      for name, _ in node.names:
        if name == 'print_function':
          self.seen_print_func = True

  def visit_importfrom(self, node):
    """Process 'from' statements"""
    self.saw_imports = True
    self._check_print_function(node)

  def visit_import(self, _node):
    """Process 'import' statements"""
    self.saw_imports = True


class SourceChecker(pylint.checkers.BaseChecker):
  """Make sure we enforce rules on the source."""

  __implements__ = pylint.interfaces.IAstroidChecker

  # pylint: disable=class-missing-docstring,multiple-statements
  class _MessageR9200(object): pass
  class _MessageR9201(object): pass
  class _MessageR9202(object): pass
  class _MessageR9203(object): pass
  class _MessageR9204(object): pass
  class _MessageR9205(object): pass
  # pylint: enable=class-missing-docstring,multiple-statements

  name = 'source_checker'
  priority = -1
  MSG_ARGS = 'offset:%(offset)i: {%(line)s}'
  msgs = {
      'R9200': ('Shebang should be #!/usr/bin/env python2 or '
                '#!/usr/bin/env python3',
                ('bad-shebang'), _MessageR9200),
      'R9201': ('Shebang is missing, but file is executable (chmod -x to fix)',
                ('missing-shebang'), _MessageR9201),
      'R9202': ('Shebang is set, but file is not executable (chmod +x to fix)',
                ('spurious-shebang'), _MessageR9202),
      'R9203': ('Unittest not named xxx_unittest.py',
                ('unittest-misnamed'), _MessageR9203),
      'R9204': ('File encoding missing (the first line after the shebang'
                ' should be "# -*- coding: utf-8 -*-")',
                ('missing-file-encoding'), _MessageR9204),
      'R9205': ('File encoding should be "utf-8"',
                ('bad-file-encoding'), _MessageR9205),
  }
  options = ()

  # Taken from PEP-263.
  _ENCODING_RE = re.compile(br'^[ \t\v]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)')

  def visit_module(self, node):
    """Called when the whole file has been read"""
    with node.stream() as stream:
      st = os.fstat(stream.fileno())
      self._check_shebang(node, stream, st)
      self._check_encoding(node, stream, st)
      self._check_module_name(node)

  def _check_shebang(self, _node, stream, st):
    """Verify the shebang is version specific"""
    stream.seek(0)

    mode = st.st_mode
    executable = bool(mode & 0o0111)

    shebang = stream.readline()
    if shebang[0:2] != b'#!':
      if executable:
        self.add_message('R9201')
      return
    elif not executable:
      self.add_message('R9202')

    if shebang.strip() not in (
        b'#!/usr/bin/env python2', b'#!/usr/bin/env python3'):
      self.add_message('R9200')

  def _check_encoding(self, _node, stream, st):
    """Verify the file has an encoding set

    See PEP-263 for more details.
    https://www.python.org/dev/peps/pep-0263/
    """
    # Only allow empty files to have no encoding (e.g. __init__.py).
    if not st.st_size:
      return

    stream.seek(0)
    encoding = stream.readline()

    # If the first line is the shebang, then the encoding is the second line.
    if encoding[0:2] == b'#!':
      encoding = stream.readline()

    # See if the encoding matches the standard.
    m = self._ENCODING_RE.match(encoding)
    if m:
      if m.group(1) != b'utf-8':
        self.add_message('R9205')
    else:
      self.add_message('R9204')

  def _check_module_name(self, node):
    """Make sure the module name is sane"""
    # Catch various typos.
    name = node.name.rsplit('.', 2)[-1]
    if name.rsplit('_', 2)[-1] in ('unittests',):
      self.add_message('R9203')


class CommentChecker(pylint.checkers.BaseTokenChecker):
  """Enforce our arbitrary rules on comments."""

  __implements__ = pylint.interfaces.ITokenChecker

  # pylint: disable=class-missing-docstring,multiple-statements
  class _MessageR9250(object): pass
  # pylint: enable=class-missing-docstring,multiple-statements

  name = 'comment_checker'
  priority = -1
  MSG_ARGS = 'offset:%(offset)i: {%(line)s}'
  msgs = {
      'R9250': ('One space needed at start of comment: %(comment)s',
                ('comment-missing-leading-space'), _MessageR9250),
  }
  options = ()

  def _visit_comment(self, lineno, comment):
    """Process |comment| at |lineno|."""
    if comment == '#':
      # Ignore standalone comments for spacing.
      return

    if lineno == 1 and comment.startswith('#!'):
      # Ignore shebangs.
      return

    # We remove multiple leading # to support runs like ###.
    if not comment.lstrip('#').startswith(' '):
      self.add_message('R9250', line=lineno, args={'comment': comment})

  def process_tokens(self, tokens):
    """Process tokens and look for comments."""
    for (tok_type, token, (start_row, _), _, _) in tokens:
      if tok_type == tokenize.COMMENT:
        self._visit_comment(start_row, token)


class ChromiteLoggingChecker(pylint.checkers.BaseChecker):
  """Make sure we enforce rules on importing logging."""

  __implements__ = pylint.interfaces.IAstroidChecker

  # pylint: disable=class-missing-docstring,multiple-statements
  class _MessageR9301(object): pass
  # pylint: enable=class-missing-docstring,multiple-statements

  name = 'chromite_logging_checker'
  priority = -1
  MSG_ARGS = 'offset:%(offset)i: {%(line)s}'
  msgs = {
      'R9301': ('logging is deprecated. Use "from chromite.lib import '
                'cros_logging as logging" to import chromite/lib/cros_logging',
                ('cros-logging-import'), _MessageR9301),
  }
  options = ()
  # This checker is disabled by default because we only want to disallow "import
  # logging" in chromite and not in other places cros lint is used. To enable
  # this checker, modify the pylintrc file.
  enabled = False

  def visit_import(self, node):
    """Called when node is an import statement."""
    for name, _ in node.names:
      if name == 'logging':
        self.add_message('R9301', line=node.lineno)


def register(linter):
  """pylint will call this func to register all our checkers"""
  # Walk all the classes in this module and register ours.
  this_module = sys.modules[__name__]
  for member in dir(this_module):
    if not member.endswith('Checker'):
      continue
    cls = getattr(this_module, member)
    linter.register_checker(cls(linter))
