#!/usr/bin/env python
#
# structmatch() hack
#
# 2004-08-10 erik heneryd
#

import sre_parse, sre_compile
from sre_constants import BRANCH, MAX_REPEAT, MIN_REPEAT, SUBPATTERN

def structmatch(pstr, target):
    r"""
    # mismatch
    >>> structmatch(r'(hej)', 'abcdef')
    []


    # group
    >>> structmatch(r'(...)', 'abcdef')
    [['abc']]
    >>> structmatch(r'(...).(..)', 'abcdef')
    [['abc'], ['ef']]


    # group (repeated)
    >>> structmatch(r'([^d])*', 'abcdef')
    [['a', 'b', 'c']]
    >>> structmatch(r'([^d])*(.)*', 'abcdef')
    [['a', 'b', 'c'], ['d', 'e', 'f']]
    >>> structmatch(r'(..)*', 'abcdef')
    [['ab', 'cd', 'ef']]
    >>> structmatch(r'(.){2}', 'abcdef')
    [['a', 'b']]


    # group with subgroups
    >>> structmatch(r'((...))', 'abcdef')
    [[['abc']]]
    >>> structmatch(r'((...)(...))', 'abcdef')
    [[['abc'], ['def']]]


    # group with subgroups (repeated)
    >>> structmatch(r'((...))*', 'abcdef') # FIXME: really?
    [[[['abc']], [['def']]]]
    >>> structmatch(r'((...)*)', 'abcdef')
    [[['abc', 'def']]]
    >>> structmatch(r'(.(.)(.(.)).(.))', 'abcdef')
    [[['b'], [['d']], ['f']]]

    >>> structmatch(r'((.).(.))*', 'abcdef')    # FIXME: really?
    [[[['a'], ['c']], [['d'], ['f']]]]

    >>> structmatch(r'(([ab])*(x)*)*', 'baxbxx') # FIXME: really?
    [[[['b', 'a'], ['x']], [['b'], ['x', 'x']]]]


    # alternation
    >>> structmatch(r'([^a])+|([^d])+', 'abcdef')
    [['a', 'b', 'c']]


    # non-capturing groups
    >>> structmatch(r'(?:(.).(.))', 'abcdef')
    [['a'], ['c']]
    >>> structmatch(r'(?:(.).(.))*', 'abcdef')
    [['a'], ['c'], ['d'], ['f']]
    >>> structmatch(r'((.).(.))*', 'abcdef') # FIXME: really?
    [[[['a'], ['c']], [['d'], ['f']]]]

    # passwd example
    >>> structmatch(r'(((^|:)([^:\n]*))*\n)', 'root:x:0:\ndaemon:x:1:\nbin:x:2:\nsys:x:3:\n')
    [[[[[''], ['root']], [[':'], ['x']], [[':'], ['0']], [[':'], ['']]]]]

    # non-greedy matching
    >>> structmatch(r'(a)*?(aardvark)', 'aaaaardvark')
    [['a', 'a', 'a'], ['aardvark']]


    # misc grouping and repeat tests
    >>> structmatch(r'(a)*', 'aaa')
    [['a', 'a', 'a']]
    >>> structmatch(r'(a*)', 'aaa')
    [['aaa']]
    >>> structmatch(r'((a)*b)', 'aaab')
    [[['a', 'a', 'a']]]
    >>> structmatch(r'((a*)b)', 'aaab')
    [[['aaa']]]

    # FIXME: filter out non-lists
    >>> structmatch(r'(?:a)*', 'aaa')
    'aaa'
    >>> structmatch(r'(?:a*)', 'aaa')
    'aaa'
    >>> structmatch(r'a*', 'aaa')
    'aaa'

    """

    pattern = sre_parse.parse(pstr)
    rx = sre_compile.compile(pattern)
    m = rx.match(target)
    if not m:
        return []
    pattern.pattern.groups += 1 # make room for fake hack group
    return _traverse(pattern, target, 0, m.end())


def _traverse(pattern, target, start, end):
    subgroups = []
    mstr = ""
    gflag = pattern.pattern.groups-1

    while start < end:
        for ix in range(len(pattern)):
            rest = pattern[ix:]

            op, arg = rest[0]

            if op == SUBPATTERN and arg[0] is not None:
                gid = arg[0]
            else:
                gid = gflag
                rest[0] = (SUBPATTERN, (gid, rest[0:1]))

            rx = sre_compile.compile(rest)
            m = rx.match(target, start, end)

            if m:
                if op == BRANCH:
                    for b in arg[-1]:
                        sp = sre_parse.SubPattern(pattern.pattern, b)
                        rx = sre_compile.compile(sp)
                        if rx.match(target, start, end):
                            r = _traverse(sp, target, start, m.end(gid))
                            if type(r) is str:
                                mstr += r
                            else:
                                subgroups.extend(r)
                            break

                elif op in (MAX_REPEAT, MIN_REPEAT):
                    sp = sre_parse.SubPattern(pattern.pattern, arg[-1])
                    r = _traverse(sp, target, start, m.end(gid))

                    sop, sarg = sp[0]

                    if sop == SUBPATTERN:
                        if sarg[0] is None:
                            # non-capturing
                            rr = reduce(lambda x,y: x+y, r)
                            if type(r) is str:
                                mstr += rr
                            else:
                                subgroups.extend(r)
                        else:
                            rr = []
                            for e in r:
                                if type(e) is list and len(e) == 1 and type(e[0]) is str:
                                    rr.append(e[0])
                                else:
                                    rr = r
                                    break
                            subgroups.append(rr)
                    else:
                        mstr += r

                elif op == SUBPATTERN:
                    sp = sre_parse.SubPattern(pattern.pattern, arg[-1])
                    r = _traverse(sp, target, start, m.end(gid))

                    if arg[0] is None:
                        # non-capturing
                        if type(r) is str:
                            mstr += r
                        else:
                            subgroups.extend(r)
                    elif type(r) is not list:
                        subgroups.append([r])
                    else:
                        subgroups.append(r)

                else:
                    mstr += m.group(gid)

                start = m.end(gid)

    if subgroups:
        return subgroups
    else:
        return mstr


def _test():
    import doctest, structmatch
    doctest.testmod(structmatch)

if __name__ == "__main__":
    _test()