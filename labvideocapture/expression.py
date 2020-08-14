#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import numpy as _np
import math as _math

class ParseError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)

def bool_like(x):
    return isinstance(x, (bool, _np.bool_))

class Alternator:
    def __init__(self, n):
        self.i      = 0
        self.n      = n
        self.status = False

    def get(self):
        self.i += 1
        if self.i % self.n == 0:
            self.i      = 0
            self.status = not self.status
        return self.status

class BodyPart:
    def __init__(self, index):
        self._index = index

    @property
    def x(self):
        return f"__pred__[{self._index}, 0]"

    @property
    def y(self):
        return f"__pred__[{self._index}, 1]"

    @property
    def p(self):
        return f"__pred__[{self._index}, 2]"

    def __format__(self, spec=''):
        if spec not in ("", "s"):
            raise TypeError(f"cannot format a body part representation into spec '{spec}'")
        return f"__pred__[{self._index}, :2]"

def parse(line_expr, bodyparts):
    """parses the expression and returns the corresponding evaluator function.

    the expression can contain '{<part name>.<axis>}',
    where the <axis> may be one of (x, y, p).

    the expression can also refer to the common 'math' and 'numpy' libraries
    as 'math' and 'np'.

    parameters
    ----------
    line_expr -- the expression in a line of string.
    bodyparts -- a list of N body part names (as it appears in "config.yaml").

    returns
    -------
    run       -- a function that takes a (N, 3) array and returns a boolean value.
    """
    mapping = dict((part, BodyPart(i)) for i, part in enumerate(bodyparts))
    try:
        expr    = compile(line_expr.format(**mapping),
                          "<expression>", mode="eval")
    except KeyError as e:
        raise ParseError(f"{e}")

    every10 = Alternator(10)
    def _run(estimation):
        return eval(expr, dict(math=_math, np=_np,
                               __pred__=estimation,
                               EVERY10=every10), {})
    try:
        ret = _run(_np.empty((len(bodyparts), 3), dtype=_np.float64)*_np.nan)
    except BaseException as e:
        raise ParseError(f"{e}")
    if not bool_like(ret):
        raise ParseError(f"the expression does not return a boolean value but a {type(ret)}")
    return _run
