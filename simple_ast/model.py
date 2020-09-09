from enum import Enum


class LanguagePart(Enum):
    FILE = 1
    CLASS = 2

    @classmethod
    def get_by_string(cls, string: str):
        res = list(filter(lambda x: x.name == string, cls))
        if len(res) != 1:
            raise Exception('Can\'t find language part ' + string)
        return res[0]


class Function(Enum):
    LIKE = 1
    AND = 2
    OR = 3

    @classmethod
    def get_by_string(cls, string: str):
        res = list(filter(lambda x: x.name == string, cls))
        if len(res) != 1:
            raise Exception('Can\'t find function ' + string)
        return res[0]


class CompareOperator(Enum):
    LT = 1
    LTE = 2
    GT = 3
    GTE = 4
    EQ = 5
    NEQ = 6

    @classmethod
    def get_by_string(cls, string: str):
        if string == '<':
            return cls.LT
        elif string == '<=':
            return cls.LTE
        elif string == '>':
            return cls.GT
        elif string == '>=':
            return cls.GTE
        elif string == '=':
            return cls.EQ
        elif string == '!=':
            return cls.NEQ
        else:
            raise Exception('Can\'t find compare operator ' + string)

