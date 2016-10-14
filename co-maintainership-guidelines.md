These are a series of guidelines to follow if you are a maintainer of this repository.

General stuff
=============

- based on current size and activity, the ideal number of maintainers should be around 3-4 (this can change in the future)
- the motivation is to avoid a repeat of the situation of hamlpy where the maintainer disappeared
- this project should not become a burden for you
- release early, release often
- Laurent is the "lazy BDFL" of this project but wishes to never have to use this power
- try to be a friendly human being as much as it's possible for you
- exclusionist behavior is prohibited (sexism, homophobic, racist, transphobic, etc...)
- if you make a mistake don't worry, it's not the end of the world, we are all humans

Programming rules
=================

- follow pep8 as long as it makes sense
- write a reasonable amount of tests
- document for every new user feature
- update changelog.md (but everyone always forgot to do that)
- no breaking backward compatibility except if it's really needed or justified (security for example)

When to merge
=============

Small contributions that shouldn't generate diverging opinion can be directly
pushed to master. This include things like typos, pep8, small refactoring that
don't modify behavior and have a very low chance of breaking things.

All other contributions needs to pass by a pull request.

- bugfixes requires at least one maintainer's approval (other than the submitter)
- medium features/modifications require at least 2 maintainers' approval
- big features/modifications require all maintainers' approval

If everyone has approved a pull request **or** enough people (as specified
before) have approved, and that a reasonable time has passed (1-2 weeks depending
on the size of the PR and availability of everyone and potential chances of
different opinions) the PR can be merged.
