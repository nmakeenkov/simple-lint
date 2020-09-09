import os
from simple_lint import run_lint


def main():
    # cd to project root
    os.chdir(os.path.dirname(os.path.dirname(__file__)))

    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__init__.py')) == 0

    assert len(run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/ok_class.py')) == 0

    long_init_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__too_long_init__.py')
    assert len(long_init_res) == 1
    assert long_init_res[0][0] == "Length limit"

    big_class_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/big_class.py')
    assert len(big_class_res) == 1
    assert big_class_res[0][0] == "Length limit"

    big_class_in_init_res = run_lint('rule_set.tx', 'simple_rule_set.rules', 'examples/__big_class_in_init__.py')
    assert len(big_class_in_init_res) == 2
    assert big_class_in_init_res[0][0] == "Length limit"
    assert big_class_in_init_res[1][0] == "Length limit"


if __name__ == '__main__':
    main()
