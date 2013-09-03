tests=*.py
nosetests ${1:-$tests} --with-coverage --cover-html --cover-inclusive --cover-package=hamlpy.*
