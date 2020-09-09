import re

from simple_ast.model import CompareOperator, Function
from simple_ast.visitor import AbstractVisitor, LanguagePart


class ErrorRegistry(object):
    def __init__(self):
        self._errors = []

    def save_error(self, rule_name, metainf):
        self._errors.append((rule_name, metainf,))

    # TODO: sort by line number
    def get_error_message(self):
        return sorted(self._errors, key=lambda rule: rule[0])


class Variable(object):
    """
    Represents a variable in the DSL scope
    """
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data


class Scope(object):
    """
    Represents DSL scope
    """
    def __init__(self, variables: list):
        self._variables = {}
        for variable in variables:
            self._variables[variable.name] = variable.data

    def get_value(self, variable_name: str, properties: list):
        if variable_name not in self._variables:
            raise Exception("Variable " + variable_name + "not found in current scope")
        variable = self._variables[variable_name]
        for prop in properties:
            if prop not in variable:
                raise Exception(variable_name + " has no property " + prop)
            variable = variable[prop]
            variable_name += prop
        if isinstance(variable, dict):
            raise Exception(variable_name + " is not a value; it has properties {" + ",".join(variable.keys()) + "}")
        return variable


class Rule(object):
    """
    rule is a function (Scope -> object), where the object is the assertion failed or none
    """
    def __init__(self, name: str, rule: callable):
        self.name = name
        self.rule = rule


class Validate(object):
    def __init__(self):
        self._rules = {}

    def register_rule(self, language_part: LanguagePart, rule: Rule):
        self._rules.setdefault(language_part, [])
        self._rules[language_part].append(rule)

    def register_all_rules(self, other):
        for language_part, rules in other._rules.items():
            for rule in rules:
                self.register_rule(language_part, rule)

    def validate_rule(self, language_part: LanguagePart, scope: Scope, error_registry: ErrorRegistry):
        rules = self._rules[language_part]
        if rules is None:
            return
        for rule in rules:
            error = rule.rule(scope)
            if error is not None:
                error_registry.save_error(rule.name, error)


class IfStatementFunction(object):
    def __init__(self, condition_res, if_res, else_res):
        self.condition_res = condition_res
        self.if_res = if_res
        self.else_res = else_res

    def __call__(self, *args, **kwargs):
        condition = self.condition_res(*args, **kwargs)
        if condition[1] is not None:
            return None, condition[1]
        if not isinstance(condition[0], bool):
            raise Exception('Can\'t use ' + str(condition[0]) + ' as bool')
        return self.if_res(*args, **kwargs) if condition[0] else self.else_res(*args, **kwargs)


class LikeFunction(object):
    def __init__(self, operands):
        if len(operands) != 2:
            raise Exception("like expects 2 arguments, found " + str(len(operands)))
        self.operands = operands

    def __call__(self, *args, **kwargs):
        expression, pattern = list(map(lambda operand: operand(*args, **kwargs), self.operands))
        if expression[1] is not None:
            return None, expression[1]
        if pattern[1] is not None:
            return None, pattern[1]
        if not isinstance(expression[0], str):
            raise Exception('Can\'t match expression ' + str(expression[0]) + ", string expected")
        if not isinstance(pattern[0], str):
            raise Exception('Can\'t match pattern ' + str(pattern[0]) + ", string expected")
        pattern = re.compile(pattern[0])
        return pattern.search(expression[0]) is not None, None


class CompareFunction(object):
    def __init__(self, operator: CompareOperator, lhs: callable, rhs: callable):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __call__(self, *args, **kwargs):
        lhs_result, lhs_error = self.lhs(*args, **kwargs)
        if lhs_error is not None:
            return None, lhs_error
        rhs_result, rhs_error = self.rhs(*args, **kwargs)
        if rhs_error is not None:
            return None, rhs_error
        if self.operator == CompareOperator.LT:
            return lhs_result < rhs_result, None
        elif self.operator == CompareOperator.LTE:
            return lhs_result <= rhs_result
        elif self.operator == CompareOperator.GT:
            return lhs_result > rhs_result
        elif self.operator == CompareOperator.GTE:
            return lhs_result >- rhs_result
        elif self.operator == CompareOperator.EQ:
            return lhs_result == rhs_result
        elif self.operator == CompareOperator.NEQ:
            return lhs_result != rhs_result
        else:
            raise Exception('Unknown operator ' + str(self.operator))


class AssertFunction(object):
    def __init__(self, operand: callable, assert_description):
        self.operand = operand
        self.assert_description = assert_description

    def __call__(self, *args, **kwargs):
        operand_result = self.operand(*args, **kwargs)
        if operand_result[1] is not None:
            return None, operand_result[1]
        if not isinstance(operand_result[0], bool):
            raise Exception('Can\'t use ' + str(operand_result[0]) + ' as an assertion')
        return None, None if operand_result[0] else self.assert_description


class ValidateGenerator(AbstractVisitor):
    """
    Generates a Validate instance.

    Functions with the following signatures are returned when calling
        - RuleSet: (Scope -> Validate)
        - Rule: (Scope -> Validate)
        - LanguagePartRule: (Scope -> Validate)
        - Statement(including Expression, Assertion): (Scope -> tuple). The return value is a tuple of 2 elements:
            - the result of the expression or None
            - the assertion failed or None.
    """

    def __init__(self):
        self._cur_rule = None

    def visit_rule_set(self, rules: list):
        return self._merge_validates(list(map(self.visit, rules)))

    def visit_rule(self, message: str, language_part_rules: list):
        self._cur_rule = message
        return self._merge_validates(list(map(self.visit, language_part_rules)))

    def visit_language_part_rule(self, part: LanguagePart, rule):
        res = Validate()
        visited_rule = self.visit(rule)
        res.register_rule(part, Rule(self._cur_rule, lambda scope: visited_rule(scope)[1]))
        return res

    def visit_if_statement(self, condition, if_true, if_false):
        condition_res = self.visit(condition)
        if_res = self.visit(if_true)
        else_res = self.visit(if_false)
        return IfStatementFunction(condition_res, if_res, else_res)

    def visit_pass_statement(self):
        return lambda scope: (None, None)

    def visit_function_expression(self, function: Function, operands):
        if Function.LIKE.name != function.name:
            raise NotImplementedError("function " + function.name + " evaluator not implemeted")
        return LikeFunction(list(map(self.visit, operands)))

    def visit_compare_expression(self, operator: CompareOperator, lhs, rhs):
        return CompareFunction(operator, self.visit(lhs), self.visit(rhs))

    def visit_int_constant(self, value: int):
        return lambda scope: (value, None)

    def visit_string_constant(self, value: str):
        return lambda scope: (value, None)

    def visit_variable_with_property(self, variable: str, props: list):
        return lambda scope: (scope.get_value(variable, props), None)

    def visit_assert(self, expression):
        operand = self.visit(expression)
        return AssertFunction(operand, expression.parent)

    @staticmethod
    def _merge_validates(validates):
        res = Validate()
        for validate in validates:
            res.register_all_rules(validate)
        return res

