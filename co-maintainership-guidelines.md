Those are a series of guidelines to follow is you are a maintainer of this
repository.

General stuff
=============

- as of its current size and activity, the ideal number of maintainer should be around 3-4 (this can change in the future)
- the idea is to avoid falling back in the situation of hamlpy where the maintainer disappeared
- this project should not become a burden for you
- release early, release often
- Laurent is the "lazy BDFL" of this project but wish to never have to use this power
- try to be a friendly human being as much as it's possible for you
- exclusionist behavior is prohibited (sexism, homophobic, racist, transphobic, etc...)
- if you do a mistake don't worry, it's not the end of the world, we are all humans

Programming rules
=================

- follows pep8 as long as it makes sense
- write a reasonable amount of tests
- document for every new user feature
- update changelog.md (but everyone always forgot to do that)
- no backward compatibility break except if it's really needed or justified (security for example)

When to merge
=============

Small contributions that shouldn't generate diverging opinion can be directly
push on master. This include things like typo, pep8, small refactoring that
don't modify behavior and have a very low chance of breaking things.

All other contributions needs to pass by a pull request.

- bugfixs requires at least one maintainer approval (other than the submitter)
- medium features/modifications requires at least 2 maintainers approval
- big features/modifications requires all maintainers approval

If everyone has approved a pull request **or** that enough people (as specified
before) has approved and that a reasonable time has passed (1-2 weeks depending
on the size of the PR and availability of everyone and potential chances of
different opinions) the PR can be merged.
