```
pip install pypandoc
pip install wheel
pip install twine
rm -R dist/
python setup.py sdist
python setup.py bdist_wheel --universal
twine upload -u nyaruka dist/*
```
