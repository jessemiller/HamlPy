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
        ATOM = Combine(NAME ^ quotedString ^ NUMBER ^ NONE)
        TRAILER = '.' + NAME
        FACTOR = Forward()
        POWER = Combine(ATOM + ZeroOrMore(TRAILER)) + Optional(Keyword('**') + FACTOR)
        FACTOR = ((Keyword('+') ^ Keyword('-') ^ Keyword('~')) + FACTOR) ^ POWER
        TERM = FACTOR + ZeroOrMore((Keyword('*') ^ Keyword('/') ^ Keyword('%') ^ Keyword('//')) + FACTOR)
        ARITH_EXPRESSION = TERM + ZeroOrMore((Keyword('+') ^ Keyword('-')) + TERM)
        SHIFT_EXPRESSION = ARITH_EXPRESSION + ZeroOrMore((Keyword('<<') ^ Keyword('>>')) + ARITH_EXPRESSION)
        AND_EXPRESSION = SHIFT_EXPRESSION + ZeroOrMore(Keyword('&') + SHIFT_EXPRESSION)
        XOR_EXPRESSION = AND_EXPRESSION + ZeroOrMore(Keyword('^') + AND_EXPRESSION)
        EXPRESSION = XOR_EXPRESSION + ZeroOrMore(Keyword('|') + XOR_EXPRESSION)
        COMPARISON_OP = Keyword('<') ^ Keyword('>') ^ Keyword('==') ^ Keyword('>=') ^ Keyword('<=') ^ Keyword('<>') ^ Keyword('!=') ^ Keyword('in') ^ Keyword('not in') ^ Keyword('is') ^ Keyword('is not')
        COMPARISON = Combine(EXPRESSION + ZeroOrMore(COMPARISON_OP + EXPRESSION), adjacent=False, joinString=' ')
        NOT_TEST = Forward()
        NOT_TEST << Combine((Keyword('not') + NOT_TEST) ^ COMPARISON, adjacent=False, joinString=' ')
        AND_TEST = NOT_TEST + ZeroOrMore(Keyword('and') + NOT_TEST)
        TEST = AND_TEST + ZeroOrMore(Keyword('or') + AND_TEST)

        VALUE = STRING ^ NUMBER ^ TUPLE ^ LIST ^ NONE
        ATTRIBUTE = Group(STRING + Suppress(':') + VALUE + Optional(Keyword('if').suppress() + TEST + Optional(Keyword('else').suppress() + VALUE)))
        ATTRIBUTES = delimitedList(ATTRIBUTE)

        parsed = {}

        for group in ATTRIBUTES.parseString(self.string[1:-1]):
            key = group[0]
            value = group[1]
            condition = group[2] if len(group) > 2 else None
            alt_value = group[3] if len(group) > 3 else None

            parsed[key] = (value, condition, alt_value)

        return parsed
