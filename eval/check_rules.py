"""Static rules check for our team files (docs/rules.md, docs/traps.md section A/B).

Usage:  python eval/check_rules.py my_team.py teams/*.py
Exit code 1 if any ERROR is found. WARNINGs need a human look but do not fail.

It is a tripwire, not a proof: it catches the accidental violations we listed in traps.md
(T-01..T-07, T-17, T-18, T-20, T-21). Runtime checks live in eval/sentinel_team.py.
"""
import ast
import sys

FORBIDDEN_MODULES = {
    'threading', '_thread', 'multiprocessing', 'concurrent', 'asyncio', 'subprocess', 'socket',
    'ssl', 'http', 'urllib', 'requests', 'gc', 'inspect', 'ctypes', 'signal', 'pickle', 'marshal',
}
# Installed on the tournament cluster only on request (rules.md Q2) -> error until requested and confirmed.
UNCONFIRMED_MODULES = {'numpy', 'scipy', 'torch', 'tensorflow', 'sklearn', 'keras', 'pandas', 'jax'}
FORBIDDEN_CALLS = {
    ('random', 'seed'), ('random', 'setstate'), ('random', 'getstate'),
    ('sys', '_getframe'), ('sys', 'settrace'), ('sys', 'setprofile'),
    ('os', 'system'), ('os', 'popen'), ('os', 'fork'), ('functools', 'cache'),
}
PY39_STR_METHODS = {'removeprefix', 'removesuffix'}
# Attributes of engine objects (AgentState, Configuration, GameState(.data), Grid, Layout).
# Writing them on anything but `self` is a likely mutation of shared engine state (T-01).
ENGINE_ATTRS = {'pos', 'direction', 'start', 'is_pacman', 'scared_timer', 'num_carrying', 'num_returned',
                'agent_states', 'food', 'capsules', 'layout', 'walls', 'score', 'score_change',
                'timeleft', 'data', 'agent_distances'}
# Methods returning objects shared with (or owned by) the engine.
SHARED_GETTERS = {'get_walls', 'get_agent_state', 'get_current_observation', 'get_previous_observation'}
BUILTIN_GENERICS = {'list', 'dict', 'tuple', 'set', 'frozenset', 'type'}


class Checker(ast.NodeVisitor):

    def __init__(self, path):
        self.path = path
        self.findings = []
        self.shared_names = set()  # local names bound to get_walls()/get_agent_state()/... results

    # writes to engine objects (T-01)
    def visit_Assign(self, node):
        value = node.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                and value.func.attr in SHARED_GETTERS:
            self.shared_names.update(t.id for t in node.targets if isinstance(t, ast.Name))
        for target in node.targets:
            self._check_target(target)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        self._check_target(node.target)
        self.generic_visit(node)

    def _check_target(self, target):
        if isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._check_target(elt)
            return
        if isinstance(target, ast.Attribute):
            base = target.value.id if isinstance(target.value, ast.Name) else None
            if base not in ('self', 'cls'):
                if target.attr == 'configuration':
                    self.report('WARNING', target, 'assignment to .configuration - only OK on your own state copy '
                                                   'with a NEW Configuration object (T-01)')
                elif target.attr in ENGINE_ATTRS:
                    self.report('ERROR', target, 'write to engine attribute .%s - shared with the real game? (T-01)'
                                % target.attr)
        if isinstance(target, ast.Subscript):
            root = target
            while isinstance(root, (ast.Subscript, ast.Attribute)):
                root = root.value
            if isinstance(root, ast.Name) and root.id in self.shared_names:
                self.report('ERROR', target, 'item assignment into %r, which came from a shared engine getter '
                                             '(T-01); copy it first' % root.id)
            elif isinstance(root, ast.Call) and isinstance(root.func, ast.Attribute) \
                    and root.func.attr in SHARED_GETTERS:
                self.report('ERROR', target, 'item assignment into the result of %s() (T-01)' % root.func.attr)

    def report(self, level, node, message):
        self.findings.append((level, getattr(node, 'lineno', 0), message))

    # imports
    def visit_Import(self, node):
        for alias in node.names:
            self._check_module(node, alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self._check_module(node, node.module)
            if node.module == 'functools' and any(a.name == 'cache' for a in node.names):
                self.report('ERROR', node, 'functools.cache is Python 3.9+ (T-17)')
        self.generic_visit(node)

    def _check_module(self, node, name):
        root = name.split('.')[0]
        if root in FORBIDDEN_MODULES:
            self.report('ERROR', node, 'forbidden module %r (threads/processes/introspection/IO, R2/R5)' % name)
        if root in UNCONFIRMED_MODULES:
            self.report('ERROR', node, 'module %r not confirmed on the cluster (R9, Q2)' % name)
        if name == '__main__' or root == 'builtins':
            self.report('ERROR', node, 'access to %r (introspection, T-04)' % name)

    # attribute access
    def visit_Attribute(self, node):
        base = node.value.id if isinstance(node.value, ast.Name) else None
        if (base, node.attr) in FORBIDDEN_CALLS:
            self.report('ERROR', node, '%s.%s is forbidden (T-02/T-04/T-07/T-17)' % (base, node.attr))
        if base == 'sys' and node.attr in ('stdout', 'stderr') and isinstance(node.ctx, ast.Store):
            self.report('ERROR', node, 'assignment to sys.%s (R7)' % node.attr)
        if node.attr.startswith('_') and not node.attr.startswith('__') and base not in ('self', 'cls'):
            self.report('ERROR', node, 'private attribute %r accessed (T-04)' % node.attr)
        if node.attr in PY39_STR_METHODS:
            self.report('ERROR', node, '%s is Python 3.9+ (T-17)' % node.attr)
        if node.attr == '__main__' or base == '__main__':
            self.report('ERROR', node, '__main__ access (T-04)')
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id == '__main__':
            self.report('ERROR', node, '__main__ access (T-04)')
        self.generic_visit(node)

    # definitions
    def visit_FunctionDef(self, node):
        if node.name == 'observation_function':
            self.report('ERROR', node, 'observation_function overridden (T-03)')
        if node.name == 'get_action':
            self.report('WARNING', node, 'get_action overridden - make sure observation handling is unchanged')
        for arg in node.args.args + node.args.kwonlyargs:
            if arg.annotation is not None:
                self._check_annotation(arg.annotation)
        if node.returns is not None:
            self._check_annotation(node.returns)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_AnnAssign(self, node):
        self._check_annotation(node.annotation)
        self.generic_visit(node)

    def _check_annotation(self, ann):
        for sub in ast.walk(ann):
            if isinstance(sub, ast.Subscript) and isinstance(sub.value, ast.Name) and sub.value.id in BUILTIN_GENERICS:
                self.report('ERROR', sub, '%s[...] annotation fails at runtime on Python 3.8 (T-17)' % sub.value.id)
            if isinstance(sub, ast.BinOp) and isinstance(sub.op, ast.BitOr):
                self.report('ERROR', sub, 'X | Y annotation is Python 3.10+ (T-17)')

    # exceptions
    def visit_Try(self, node):
        reraises_timeout = False
        for handler in node.handlers:
            names = self._handler_names(handler)
            if 'TimeoutFunctionException' in names and any(isinstance(s, ast.Raise) for s in handler.body):
                reraises_timeout = True
            broad = handler.type is None or names & {'Exception', 'BaseException'}
            if broad and not reraises_timeout:
                self.report('ERROR', handler, 'broad except would swallow the framework timeout (T-05); '
                                              're-raise TimeoutFunctionException first')
        self.generic_visit(node)

    @staticmethod
    def _handler_names(handler):
        if handler.type is None:
            return set()
        nodes = handler.type.elts if isinstance(handler.type, ast.Tuple) else [handler.type]
        return {n.id if isinstance(n, ast.Name) else getattr(n, 'attr', '') for n in nodes}

    # calls
    def visit_Call(self, node):
        func = node.func
        if isinstance(func, ast.Name) and func.id == 'open':
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == 'mode'), None)
            mode_value = getattr(mode, 'value', getattr(mode, 's', None))
            if mode is None or (isinstance(mode_value, str) and not any(c in mode_value for c in 'wax+')):
                self.report('WARNING', node, 'file read - only shipped read-only data relative to __file__ is OK (Q6, T-21)')
            else:
                self.report('ERROR', node, 'file opened for writing (R8, T-21)')
        if isinstance(func, ast.Name) and func.id in ('eval', 'exec', '__import__'):
            self.report('WARNING', node, '%s() - make sure it cannot load anything but our own code' % func.id)
        if isinstance(func, ast.Name) and func.id == 'print':
            self.report('WARNING', node, 'print() - must be off in tournament mode (R7, T-20)')
        self.generic_visit(node)

    def visit_Match(self, node):  # only reachable when run on Python >= 3.10
        self.report('ERROR', node, 'match statement is Python 3.10+ (T-17)')
        self.generic_visit(node)


def check_file(path):
    with open(path, encoding='utf-8') as f:
        source = f.read()
    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError as e:
        return [('ERROR', e.lineno or 0, 'syntax error under Python %d.%d: %s' % (sys.version_info[:2] + (e.msg,)))]
    checker = Checker(path)
    checker.visit(tree)
    return sorted(checker.findings, key=lambda f: f[1])


def main(paths):
    if sys.version_info[:2] != (3, 8):
        print('note: run with the Python 3.8 venv to also catch 3.9+ syntax (T-17)')
    errors = 0
    for path in paths:
        findings = check_file(path)
        errors += sum(1 for level, _, _ in findings if level == 'ERROR')
        status = 'OK' if not any(level == 'ERROR' for level, _, _ in findings) else 'FAIL'
        print('%s  %s' % (status, path))
        for level, line, message in findings:
            print('  %s line %d: %s' % (level, line, message))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
