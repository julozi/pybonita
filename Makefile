NAME=pybonita
VERSION=`python setup.py --version`
DOCDIR=documentation
LOCALPYPI=http://pypi.igbmc.u-strasbg.fr/

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
	rm -Rf pybonita.egg-info
	rm -Rf dist

.PHONY : doc
doc:
	cd $(DOCDIR); make html

.PHONY : tests
tests:
	nosetests -v -s -d -x

.PHONY : silent-tests
silent-tests:
	nosetests

.PHONY : flake8
flake8:
	flake8 --ignore=E501,W293 --max-complexity=12 $(NAME)

.PHONY : strict-flake8
strict-flake8:
	flake8 $(NAME)

###################################################################
# Package builders.
###################################################################
local-pypi:
	python setup.py register -r $(LOCALPYPI) sdist upload -r $(LOCALPYPI) 

dist: local-pypi
