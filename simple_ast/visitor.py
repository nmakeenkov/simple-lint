from abc import ABC, abstractmethod

from simple_ast.model import LanguagePart, Function, CompareOperator

RULE_SET = 'RuleSet'
RULE = 'Rule'
LANGUAGE_PART_RULE = 'LanguagePartRule'
IF_STATEMENT = 'IfStatement'
PASS_STATEMENT = 'PassStatement'
FUNCTION_EXPRESSION = 'FunctionExpression'
COMPARE_EXPRESSION = 'CompareExpression'
INT_CONSTANT = 'IntConstant'
STRING_CONSTANT = 'StringConstant'
VARIABLE_WITH_PROPERTY = 'VariableWithProperty'
ASSERT = 'Assert'


class AbstractVisitor(ABC):

    def visit(self, node):
        if node.__class__.__name__ == RULE_SET:
            return self.visit_rule_set(node.rules)
        elif node.__class__.__name__ == RULE:
            return self.visit_rule(node.message, node.language_parts)
        elif node.__class__.__name__ == LANGUAGE_PART_RULE:
            return self.visit_language_part_rule(LanguagePart.get_by_string(node.part), node.statement)
        elif node.__class__.__name__ == IF_STATEMENT:
            return self.visit_if_statement(node.condition, node.ifTrueStatement, node.ifFalseStatement)
        elif node.__class__.__name__ == PASS_STATEMENT:
            return self.visit_pass_statement()
        elif node.__class__.__name__ == FUNCTION_EXPRESSION:
            return self.visit_function_expression(Function.get_by_string(node.function),
                                                  [node.operand1] + node.operands)
        elif node.__class__.__name__ == COMPARE_EXPRESSION:
            return self.visit_compare_expression(CompareOperator.get_by_string(node.operator), node.lhs, node.rhs)
        elif node.__class__.__name__ == INT_CONSTANT:
            return self.visit_int_constant(node.value)
        elif node.__class__.__name__ == STRING_CONSTANT:
            return self.visit_string_constant(node.value)
        elif node.__class__.__name__ == VARIABLE_WITH_PROPERTY:
            return self.visit_variable_with_property(node.variable, node.properties)
        elif node.__class__.__name__ == ASSERT:
            return self.visit_assert(node.expression)
        else:
            raise Exception('Can\'t visit ' + node.__class__.__name__)

    @abstractmethod
    def visit_rule_set(self, rules: list):
        pass

    @abstractmethod
    def visit_rule(self, message: str, language_part_rules: list):
        pass

    @abstractmethod
    def visit_language_part_rule(self, part: LanguagePart, rule):
        pass

    @abstractmethod
    def visit_if_statement(self, condition, if_true, if_false):
        pass

    @abstractmethod
    def visit_pass_statement(self):
        pass

    @abstractmethod
    def visit_function_expression(self, function: Function, operands):
        pass

    @abstractmethod
    def visit_compare_expression(self, operator: CompareOperator, lhs, rhs):
        pass

    @abstractmethod
    def visit_int_constant(self, value: int):
        pass

    @abstractmethod
    def visit_string_constant(self, value: str):
        pass

    @abstractmethod
    def visit_variable_with_property(self, variable: str, props: list):
        pass

    @abstractmethod
    def visit_assert(self, expression):
        pass

