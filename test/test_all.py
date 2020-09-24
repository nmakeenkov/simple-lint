import os
from simple_lint import run_lint


def main():
    # cd to project root
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__init__.py')) == 0

    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/ok_class.py')) == 0

    long_init_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__too_long_init__.py')
    assert len(long_init_res) == 3
    assert long_init_res[0][0] == "File called by single class name"
    assert long_init_res[1][0] == "Length limit"
    assert long_init_res[2][0] == "Names"
    assert long_init_res[2][1].line_number == 4

    big_class_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/big_class.py')
    assert len(big_class_res) == 3
    assert big_class_res[0][0] == "File called by single class name"
    assert big_class_res[1][0] == "Length limit"
    assert big_class_res[1][1].line_number == 3
    assert big_class_res[2][0] == "Length limit"
    assert big_class_res[2][1].line_number == 226

    big_class_in_init_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__big_class_in_init__.py')
    assert len(big_class_in_init_res) == 4
    assert big_class_in_init_res[0][0] == "File called by single class name"
    assert big_class_in_init_res[1][0] == "Length limit"
    assert big_class_in_init_res[1][1].description.startswith("Class")
    assert big_class_in_init_res[2][0] == "Length limit"
    assert big_class_in_init_res[2][1].description.startswith("Module")
    assert big_class_in_init_res[3][0] == "Names"
    assert big_class_in_init_res[3][1].line_number == 3

    # Testing this project sources: almost no rules should be violated
    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_lint.py')) == 0
    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_ast/__init__.py')) == 0
    # UPPDER_CASE constants
    all(violation[0] == 'Names' for violation in run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_ast/model.py'))
    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_ast/validate_generator.py')) == 0
    # UPPDER_CASE constants
    all(violation[0] == 'Names' for violation in run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_ast/validator.py'))
    all(violation[0] == 'Names' for violation in run_lint('rule_set.tx', 'simple_rule_set.rules', 'simple_ast/visitor.py'))


if __name__ == '__main__':
    main()
