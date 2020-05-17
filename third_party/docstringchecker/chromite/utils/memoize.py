# -*- coding: utf-8 -*-
# Copyright 2018 The Chromium OS Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Functions for automatic caching of expensive function calls."""

from __future__ import print_function

import functools
import sys

import six


def MemoizedSingleCall(functor):
  """Decorator for simple functor targets, caching the results

  The functor must accept no arguments beyond either a class or self (depending
  on if this is used in a classmethod/instancemethod context).  Results of the
  wrapped method will be written to the class/instance namespace in a specially
  named cached value.  All future invocations will just reuse that value.

  Note that this cache is per-process, so sibling and parent processes won't
  notice updates to the cache.
  """
  # TODO(build): Should we rebase to snakeoil.klass.cached* functionality?
  # pylint: disable=protected-access
  @functools.wraps(functor)
  def wrapper(obj):
    key = wrapper._cache_key
    val = getattr(obj, key, None)
    if val is None:
      val = functor(obj)
      setattr(obj, key, val)
    return val

  # Use name mangling to store the cached value in a (hopefully) unique place.
  wrapper._cache_key = '_%s_cached' % (functor.__name__.lstrip('_'),)
  return wrapper


def Memoize(f):
  """Decorator for memoizing a function.

  Caches all calls to the function using a ._memo_cache dict mapping (args,
  kwargs) to the results of the first function call with those args and kwargs.

  If any of args or kwargs are not hashable, trying to store them in a dict will
  cause a ValueError.

  Note that this cache is per-process, so sibling and parent processes won't
  notice updates to the cache.
  """
  # pylint: disable=protected-access
  f._memo_cache = {}

  @functools.wraps(f)
  def wrapper(*args, **kwargs):
    # Make sure that the key is hashable... as long as the contents of args and
    # kwargs are hashable.
    # TODO(phobbs) we could add an option to use the id(...) of an object if
    # it's not hashable.  Then "MemoizedSingleCall" would be obsolete.
    key = (tuple(args), tuple(sorted(kwargs.items())))
    if key in f._memo_cache:
      return f._memo_cache[key]

    result = f(*args, **kwargs)
    f._memo_cache[key] = result
    return result

  return wrapper


def SafeRun(functors, combine_exceptions=False):
  """Executes a list of functors, continuing on exceptions.

  Args:
    functors: An iterable of functors to call.
    combine_exceptions: If set, and multiple exceptions are encountered,
      SafeRun will raise a RuntimeError containing a list of all the exceptions.
      If only one exception is encountered, then the default behavior of
      re-raising the original exception with unmodified stack trace will be
      kept.

  Raises:
    The first exception encountered, with corresponding backtrace, unless
    |combine_exceptions| is specified and there is more than one exception
    encountered, in which case a RuntimeError containing a list of all the
    exceptions that were encountered is raised.
  """
  errors = []

  for f in functors:
    try:
      f()
    except Exception as e:
      # Append the exception object and the traceback.
      errors.append((e, sys.exc_info()[2]))

  if errors:
    if len(errors) == 1 or not combine_exceptions:
      # To preserve the traceback.
      inst, tb = errors[0]
      six.reraise(inst, None, tb)
    else:
      raise RuntimeError([e[0] for e in errors])
