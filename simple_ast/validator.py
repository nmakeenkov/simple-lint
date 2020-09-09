import ast
import os

from simple_ast.model import LanguagePart
from simple_ast.validate_generator import Validate, ErrorRegistry, Scope, Variable


def run_validate(validate: Validate, source_file_name: str):
    error_registry = ErrorRegistry()
    visitor = ValidateAstVisitor(validate, error_registry, os.path.split(source_file_name)[1])
    with open(source_file_name) as f:
        source = f.read()
    visitor.visit(ast.parse(source))
    return error_registry


class ValidateAstVisitor(ast.NodeVisitor):
    def __init__(self, validate: Validate, error_registry: ErrorRegistry, file_name: str):
        self.validate = validate
        self.error_registry = error_registry
        self.file_name = file_name

    def visit_Module(self, node):
        if len(node.body) > 0:
            lines_count = node.body[-1].end_lineno - node.body[0].lineno + 1
        else:
            lines_count = 0
        scope = Scope([Variable('file', {'lines': lines_count, 'name': self.file_name})])
        self.validate.validate_rule(LanguagePart.FILE, scope, self.error_registry)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        lines_count = node.end_lineno - node.lineno + 1
        scope = Scope([Variable('class', {'lines': lines_count})])
        self.validate.validate_rule(LanguagePart.CLASS, scope, self.error_registry)
        self.generic_visit(node)
