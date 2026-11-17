"""Restricted expression language for cuts, derived variables and histogram axes.

Grammar (Python syntax, parsed with `ast`; anything else is a configuration error):
  objects     boson, leptons, jets, met, event, eec           whole (num(jets)) or by field (jets.pt, event.PV.npvsGood)
  literals    numbers, True, False
  operators   + - * / ** %, unary -, comparisons (chains allowed: 200 < boson.pt < 400), and, or, not
  functions   abs sqrt log log10 exp cos sin (elementwise); num sum any all max min lead (reduce one level);
              deltaR(a, b)
  variables   names defined in the configuration's `variables:` section

Every expression has a static level: event, jet, lepton or eec (an EEC entry). jet and lepton refine event, eec refines
jet; jet and lepton (or eec and lepton) do not combine. Reductions take a level to its parent (eec -> jet -> event,
lepton -> event).
"""
import ast
import operator

import awkward as ak
import numpy as np

OBJECTS = {'boson': 'event', 'met': 'event', 'event': 'event', 'jets': 'jet', 'leptons': 'lepton', 'eec': 'eec'}
PARENT = {'eec': 'jet', 'jet': 'event', 'lepton': 'event'}
DEPTH = {'event': 0, 'jet': 1, 'lepton': 1, 'eec': 2}

ELEMENTWISE = {'abs': np.abs, 'sqrt': np.sqrt, 'log': np.log, 'log10': np.log10, 'exp': np.exp, 'cos': np.cos,
               'sin': np.sin}
REDUCTIONS = {'num': lambda x: ak.num(x, axis=-1), 'sum': lambda x: ak.sum(x, axis=-1),
              'any': lambda x: ak.any(x, axis=-1), 'all': lambda x: ak.all(x, axis=-1),
              'max': lambda x: ak.max(x, axis=-1), 'min': lambda x: ak.min(x, axis=-1),
              'lead': lambda x: ak.firsts(x, axis=-1)}
BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
          ast.Pow: operator.pow, ast.Mod: operator.mod}
COMPARE = {ast.Lt: operator.lt, ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge, ast.Eq: operator.eq,
           ast.NotEq: operator.ne}


class ExprError(ValueError):
    pass


def combine(a, b, text):
    """The finer of two levels; raises if they lie on different branches (jet vs lepton)."""
    for x, y in ((a, b), (b, a)):
        z = x
        while z != 'event' and z != y:
            z = PARENT[z]
        if z == y:
            return x
    raise ExprError('%r combines %s-level and %s-level quantities' % (text, a, b))


MEMO = '__memo__'   # namespace key of the per-namespace result cache; not a valid object name in expressions


class Expr:
    """A parsed expression; `level` is static, `__call__(namespace)` evaluates it on awkward arrays."""

    def __init__(self, text, variables=None):
        self.text = str(text)
        self.variables = variables or {}
        try:
            self.tree = ast.parse(self.text, mode='eval').body
        except SyntaxError as e:
            raise ExprError('%r: %s' % (self.text, e.msg)) from None
        self.level = self._level(self.tree)

    def _level(self, n):
        t = self.text
        if isinstance(n, ast.Constant):
            if isinstance(n.value, bool) or isinstance(n.value, (int, float)):
                return 'event'
            raise ExprError('%r: only numbers and booleans are allowed as literals' % t)
        if isinstance(n, ast.Name):
            if n.id in self.variables:
                return self.variables[n.id].level
            if n.id in OBJECTS:
                return OBJECTS[n.id]
            raise ExprError('%r: unknown name %r' % (t, n.id))
        if isinstance(n, ast.Attribute):
            base = n
            while isinstance(base, ast.Attribute):
                base = base.value
            if not (isinstance(base, ast.Name) and base.id in OBJECTS):
                raise ExprError('%r: field access must start from one of %s' % (t, sorted(OBJECTS)))
            return OBJECTS[base.id]
        if isinstance(n, ast.BinOp) and type(n.op) in BINARY:
            return combine(self._level(n.left), self._level(n.right), t)
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd, ast.Not)):
            return self._level(n.operand)
        if isinstance(n, ast.BoolOp):
            lv = 'event'
            for v in n.values:
                lv = combine(lv, self._level(v), t)
            return lv
        if isinstance(n, ast.Compare) and all(type(o) in COMPARE for o in n.ops):
            lv = self._level(n.left)
            for c in n.comparators:
                lv = combine(lv, self._level(c), t)
            return lv
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and not n.keywords:
            f, args = n.func.id, n.args
            if f in ELEMENTWISE and len(args) == 1:
                return self._level(args[0])
            if f in REDUCTIONS and len(args) == 1:
                lv = self._level(args[0])
                if lv == 'event':
                    raise ExprError('%r: %s() of an event-level quantity' % (t, f))
                return PARENT[lv]
            if f == 'deltaR' and len(args) == 2:
                return combine(self._level(args[0]), self._level(args[1]), t)
            raise ExprError('%r: unknown function %s/%d' % (t, f, len(args)))
        raise ExprError('%r: %s is not allowed' % (t, type(n).__name__))

    def __call__(self, ns):
        # The memo is keyed by text: within one namespace, all expressions share the configuration's variables.
        memo = ns.get(MEMO)
        if memo is None:
            return self._eval(self.tree, ns)
        if self.text not in memo:
            memo[self.text] = self._eval(self.tree, ns)
        return memo[self.text]

    def _eval(self, n, ns):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return self.variables[n.id](ns) if n.id in self.variables else ns[n.id]
        if isinstance(n, ast.Attribute):
            return field(self._eval(n.value, ns) if not isinstance(n.value, ast.Name) else ns[n.value.id], n.attr)
        if isinstance(n, ast.BinOp):
            return BINARY[type(n.op)](self._eval(n.left, ns), self._eval(n.right, ns))
        if isinstance(n, ast.UnaryOp):
            v = self._eval(n.operand, ns)
            return -v if isinstance(n.op, ast.USub) else v if isinstance(n.op, ast.UAdd) else ~asBool(v)
        if isinstance(n, ast.BoolOp):
            vals = [asBool(self._eval(v, ns)) for v in n.values]
            out = vals[0]
            for v in vals[1:]:
                out = (out & v) if isinstance(n.op, ast.And) else (out | v)
            return out
        if isinstance(n, ast.Compare):
            left, out = self._eval(n.left, ns), None
            for op, c in zip(n.ops, n.comparators):
                right = self._eval(c, ns)
                r = COMPARE[type(op)](left, right)
                out = r if out is None else (out & r)
                left = right
            return out
        f, args = n.func.id, [self._eval(a, ns) for a in n.args]
        if f in ELEMENTWISE:
            return ELEMENTWISE[f](args[0])
        if f in REDUCTIONS:
            return REDUCTIONS[f](args[0])
        return args[0].delta_r(args[1])


def field(obj, name):
    """Stored field if there is one, else the attribute: vector methods shadow fields (jets.tau2 is the proper time squared)."""
    if isinstance(obj, ak.Array) and name in (obj.fields or ()):
        return obj[name]
    return getattr(obj, name)


def asBool(x):
    """Masks: missing values (e.g. max() of no jets) count as False."""
    if isinstance(x, (bool, np.bool_)):
        return x
    return ak.fill_none(x, False) if isinstance(x, ak.Array) else x


def compileVariables(spec):
    """{name: text} -> {name: Expr}, in order, so a variable may use the ones defined before it."""
    out = {}
    for name, text in (spec or {}).items():
        if name in OBJECTS:
            raise ExprError('variable %r shadows an object' % name)
        out[name] = Expr(text, dict(out))
    return out
