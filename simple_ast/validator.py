import ast
import os

from simple_ast.model import LanguagePart
from simple_ast.validate_generator import Validate, ErrorRegistry, Scope, Variable


def run_validate(validate: Validate, source_file_name: str):
    error_registry = ErrorRegistry()
    visitor = ValidateAstVisitor(validate, error_registry, os.path.split(source_file_name)[1])
    with open(source_file_name) as f:
        source = f.read()
    parsed_source = ast.parse(source)
    # add parent ref
    for node in ast.walk(parsed_source):
        for child in ast.iter_child_nodes(node):
            child.parent = node
    visitor.visit(parsed_source)
    return error_registry


class ValidateAstVisitor(ast.NodeVisitor):
    def __init__(self, validate: Validate, error_registry: ErrorRegistry, file_name: str):
        self.validate = validate
        self.error_registry = error_registry
        self.file_name = file_name
        self.xxx = []

    def visit_Module(self, node):
        # TODO: debug purposes; remove
        self.last_module = node
        if len(node.body) > 0:
            lines_count = node.body[-1].end_lineno - node.body[0].lineno + 1
        else:
            lines_count = 0
        file_props = {'lines': lines_count, 'name': self.file_name, 'is_single_class': (len(node.body) == 1)}
        if file_props['is_single_class']:
            file_props['single_class'] = self._create_class_variable(node.body[0]).data
        scope = Scope([Variable('file', file_props),
                       Variable('_meta_inf', {'_description': 'Module ' + self.file_name,
                                              '_file_name': self.file_name,
                                              '_line_number': 1 if len(node.body) == 0 else node.body[0].lineno})])
        self.validate.validate_rule(LanguagePart.FILE, scope, self.error_registry)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # TODO: debug purposes; remove
        self.last_class_def = node
        scope = Scope([self._create_class_variable(node),
                       Variable('_meta_inf', {'_description': 'Class ' + node.name,
                                              '_file_name': self.file_name,
                                              '_line_number': node.lineno})])
        self.validate.validate_rule(LanguagePart.CLASS, scope, self.error_registry)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        lines_count = node.end_lineno - node.lineno + 1
        scope = Scope([Variable('function', {'lines': lines_count, 'name': node.name}),
                       Variable('_meta_inf', {'_description': 'Function ' + node.name,
                                              '_file_name': self.file_name,
                                              '_line_number': node.lineno})])
        self.validate.validate_rule(LanguagePart.FUNCTION, scope, self.error_registry)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            parent = node.parent.parent if isinstance(node.parent, ast.Assign) else node.parent
            name_props = {'identifier': node.id,
                          'is_parent_class': isinstance(parent, ast.ClassDef),
                          'is_parent_file': isinstance(parent, ast.Module)}
            if name_props['is_parent_class']:
                name_props['parent_class'] = self._create_class_variable(parent).data
            scope = Scope([Variable('name', name_props),
                           Variable('_meta_inf', {'_description': 'Name ' + node.id,
                                                  '_file_name': self.file_name,
                                                  '_line_number': node.lineno})])
            self.validate.validate_rule(LanguagePart.NAME, scope, self.error_registry)
        else:
            self.xxx.append(node)
        self.generic_visit(node)

    @staticmethod
    def _create_class_variable(node):
        lines_count = node.end_lineno - node.lineno + 1
        return Variable('class', {'lines': lines_count,
                                  'name': node.name,
                                  'is_enum': 'Enum' in
                                             map(lambda x: x.id if isinstance(x, ast.Name) else None, node.bases)})
