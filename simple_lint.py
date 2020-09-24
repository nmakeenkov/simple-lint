import sys
from textx import metamodel_from_file

from simple_ast.validate_generator import ValidateGenerator
from simple_ast.validator import run_validate


def run_lint(metamodel_file_name, model_file_name, source_file_name):
    rule_set_meta = metamodel_from_file(metamodel_file_name)
    rules = rule_set_meta.model_from_file(model_file_name)
    validate = ValidateGenerator().visit(rules)
    error_registry = run_validate(validate, source_file_name)
    return error_registry.get_error_message()


def main(metamodel_file_name, model_file_name, source_file_name):
    print('\n\n'.join(map(str, run_lint(metamodel_file_name, model_file_name, source_file_name))))


if __name__ == '__main__':
    metamodel_file_name = sys.argv[1]
    model_file_name = sys.argv[2]
    source_file_name = sys.argv[3]
    main(metamodel_file_name, model_file_name, source_file_name)
