from pyparsing import *

class AttributesParser:
    def __init__(self, string):
        self.string = string

    def parse(self):
        def evalCode(input, position, tokens):
            return eval(u''.join(tokens))

        STRING = quotedString.copy().setParseAction(evalCode)

        NUMBER = Combine(
            Optional('-') + ('0' | Word('123456789',nums)) +
            Optional('.' + Word(nums)) +
            Optional(Word('eE', exact=1) + Word(nums + '+-',nums))
        ).setParseAction(evalCode)

        NONE = Keyword('None').setParseAction(replaceWith(None))

        DELIMITED_LIST = (quotedString ^ NUMBER) + ZeroOrMore(',' + (quotedString ^ NUMBER))
        TUPLE = (Suppress('(') + DELIMITED_LIST + Suppress(')')).setParseAction(evalCode)
        LIST = (Suppress('[') + DELIMITED_LIST + Suppress(']')).setParseAction(evalCode)

        NAME = Word(alphanums + '_')
        ATOM = NAME ^ quotedString ^ NUMBER ^ NONE
        TRAILER = '.' + NAME
        FACTOR = Forward()
        POWER = ATOM + ZeroOrMore(TRAILER) + Optional(Literal('**') + FACTOR)
        FACTOR = ((Literal('+') ^ Literal('-') ^ Literal('~')) + FACTOR) ^ POWER
        TERM = FACTOR + ZeroOrMore((Literal('*') ^ Literal('/') ^ Literal('%') ^ Literal('//')) + FACTOR)
        ARITH_EXPRESSION = TERM + ZeroOrMore((Literal('+') ^ Literal('-')) + TERM)
        SHIFT_EXPRESSION = ARITH_EXPRESSION + ZeroOrMore((Literal('<<') ^ Literal('>>')) + ARITH_EXPRESSION)
        AND_EXPRESSION = SHIFT_EXPRESSION + ZeroOrMore('&' + SHIFT_EXPRESSION)
        XOR_EXPRESSION = AND_EXPRESSION + ZeroOrMore('^' + AND_EXPRESSION)
        EXPRESSION = XOR_EXPRESSION + ZeroOrMore('|' + XOR_EXPRESSION)
        COMPARISON_OP = ' ' + (Literal('<') ^ Literal('>') ^ Literal('==') ^ Literal('>=') ^ Literal('<=') ^ Literal('<>') ^ Literal('!=') ^ Literal('in') ^ Literal('not in') ^ Literal('is') ^ Literal('is not')) + ' '
        COMPARISON = EXPRESSION + ZeroOrMore(COMPARISON_OP + EXPRESSION)
        NOT_TEST = Forward()
        NOT_TEST << ((Literal('not') + NOT_TEST) ^ COMPARISON)
        AND_TEST = NOT_TEST + ZeroOrMore(Literal('and') + NOT_TEST)
        TEST = AND_TEST + ZeroOrMore(Literal('or') + AND_TEST)

        VALUE = STRING ^ NUMBER ^ TUPLE ^ LIST ^ NONE
        ATTRIBUTE = Group(STRING + Suppress(':') + VALUE + Optional(Keyword('if').suppress() + Combine(TEST) + Optional(Keyword('else').suppress() + VALUE)))
        ATTRIBUTES = delimitedList(ATTRIBUTE)

        parsed = {}

        for group in ATTRIBUTES.parseString(self.string[1:-1]):
            key = group[0]
            value = group[1]
            condition = group[2] if len(group) > 2 else None
            alt_value = group[3] if len(group) > 3 else None

            parsed[key] = (value, condition, alt_value)

        return parsed
