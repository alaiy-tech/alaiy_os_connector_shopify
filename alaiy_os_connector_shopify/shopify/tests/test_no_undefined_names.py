"""Every name a module uses must actually resolve in that module.

A products/update webhook ran for three days raising

    NameError: name '_as_administrator' is not defined

because one call site relied on an import that only existed inside a
different function. Nothing caught it: the module imported fine, the
tests that touch this file never entered that branch, and the handler
catches Exception broadly, so it logged and returned 200 to Shopify
rather than failing loudly.

A unit test only covers the branch it walks. This walks every module's
AST instead and asserts that each name it loads is bound somewhere that
name could actually see -- module globals, an enclosing function, a
comprehension, builtins. Cheap, and it fails on the line rather than
three days later in a log nobody is reading.

Run with:  bench --site <site> run-tests --module \
    alaiy_os_connector_shopify.shopify.tests.test_no_undefined_names
"""

import ast
import builtins
import os
import unittest

_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Module dunders are injected by the import machinery, so they are bound at
# runtime without appearing anywhere in the source.
_BUILTINS = set(dir(builtins)) | {
    "__file__", "__name__", "__doc__", "__package__", "__spec__",
    "__loader__", "__builtins__", "__path__", "__class__",
}


def _iter_modules():
    for dirpath, dirnames, filenames in os.walk(_PACKAGE_ROOT):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for filename in filenames:
            if filename.endswith(".py"):
                yield os.path.join(dirpath, filename)


class _ScopeChecker(ast.NodeVisitor):
    """Collects every Name load that no enclosing scope binds.

    Deliberately conservative -- it only reports a name when NO scope in
    the chain binds it, so a false positive would need the name to be
    absent everywhere, which is the bug being looked for."""

    def __init__(self):
        self.undefined = []
        self.scopes = [set()]

    # -- binding helpers ---------------------------------------------------
    def _bind(self, name):
        if name:
            self.scopes[-1].add(name)

    def _bind_target(self, node):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name):
                self._bind(sub.id)

    def _visit_scope(self, node, params=()):
        self.scopes.append(set(params))
        for child in node.body if isinstance(node.body, list) else [node.body]:
            self.visit(child)
        self.scopes.pop()

    # -- bindings ----------------------------------------------------------
    def visit_Import(self, node):
        for alias in node.names:
            self._bind((alias.asname or alias.name).split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self._bind(alias.asname or alias.name)

    def visit_Assign(self, node):
        self.visit(node.value)
        for target in node.targets:
            self._bind_target(target)

    def visit_AnnAssign(self, node):
        if node.value:
            self.visit(node.value)
        self._bind_target(node.target)

    def visit_AugAssign(self, node):
        self.visit(node.value)
        self._bind_target(node.target)

    def visit_NamedExpr(self, node):
        self.visit(node.value)
        self._bind_target(node.target)

    def visit_For(self, node):
        self.visit(node.iter)
        self._bind_target(node.target)
        for child in node.body + node.orelse:
            self.visit(child)

    visit_AsyncFor = visit_For

    def visit_With(self, node):
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self._bind_target(item.optional_vars)
        for child in node.body:
            self.visit(child)

    visit_AsyncWith = visit_With

    def visit_ExceptHandler(self, node):
        if node.type:
            self.visit(node.type)
        self._bind(node.name)
        for child in node.body:
            self.visit(child)

    def visit_Global(self, node):
        for name in node.names:
            self._bind(name)

    visit_Nonlocal = visit_Global

    # -- scopes ------------------------------------------------------------
    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            self.visit(decorator)
        args = node.args
        params = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
        if args.vararg:
            params.append(args.vararg.arg)
        if args.kwarg:
            params.append(args.kwarg.arg)
        for default in args.defaults + [d for d in args.kw_defaults if d]:
            self.visit(default)
        self._bind(node.name)
        self._visit_scope(node, params)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, node):
        args = node.args
        params = [a.arg for a in args.posonlyargs + args.args + args.kwonlyargs]
        if args.vararg:
            params.append(args.vararg.arg)
        if args.kwarg:
            params.append(args.kwarg.arg)
        self.scopes.append(set(params))
        self.visit(node.body)
        self.scopes.pop()

    def visit_ClassDef(self, node):
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        self._bind(node.name)
        self._visit_scope(node)

    def _visit_comprehension(self, node):
        self.scopes.append(set())
        for generator in node.generators:
            self.visit(generator.iter)
            self._bind_target(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        for attr in ("elt", "key", "value"):
            child = getattr(node, attr, None)
            if child is not None:
                self.visit(child)
        self.scopes.pop()

    visit_ListComp = _visit_comprehension
    visit_SetComp = _visit_comprehension
    visit_GeneratorExp = _visit_comprehension
    visit_DictComp = _visit_comprehension

    # -- the actual check --------------------------------------------------
    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Load):
            return
        if node.id in _BUILTINS:
            return
        if any(node.id in scope for scope in self.scopes):
            return
        self.undefined.append((node.id, node.lineno))


def _collect_bindings(tree):
    """Module-level names, gathered first so a function defined above a
    call site still counts as bound."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    return names


class TestNoUndefinedNames(unittest.TestCase):
    def test_every_name_resolves(self):
        failures = []
        for path in _iter_modules():
            source = open(path, encoding="utf-8").read()
            try:
                tree = ast.parse(source)
            except SyntaxError as exc:
                failures.append(f"{path}: syntax error: {exc}")
                continue

            checker = _ScopeChecker()
            checker.scopes = [_collect_bindings(tree)]
            for node in tree.body:
                checker.visit(node)

            rel = os.path.relpath(path, _PACKAGE_ROOT)
            for name, lineno in checker.undefined:
                failures.append(f"{rel}:{lineno}: undefined name {name!r}")

        self.assertEqual(
            failures, [],
            "Names used but never bound in their module:\n  " + "\n  ".join(failures),
        )
