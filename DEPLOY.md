```
pip install pypandoc
pip install wheel
rm -R dist/
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload -u nicpottier dist/*
```
