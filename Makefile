NAME=pybonita
VERSION=`python setup.py --version`
DOCDIR=documentation

###################################################################
# Standard targets.
###################################################################
.PHONY : clean
clean:
	find . -name "*.pyc" -o -name "*.pyo" | xargs -n1 rm -f
	rm -Rf build
	cd $(DOCDIR); make clean

.PHONY : distclean
distclean: clean
	rm -Rf dist

.PHONY : doc
doc:
	cd $(DOCDIR); make html

.PHONY : tests
tests:
	nosetests

###################################################################
# Package builders.
###################################################################
local-pypi:
	python setup.py register -r local sdist upload -r local

dist: local-pypi
