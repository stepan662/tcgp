#!/bin/bash
rm -rf .cd
echo "Creating CD structure archive ..."
mkdir .cd
mkdir .cd/src
mkdir .cd/docs
cp *.py .cd/src/
cd docs
echo "Building documentation ..."
make > /dev/null
cp projekt.pdf ../.cd/
make clean > /dev/null
cd ..
cp docs/{czechiso.bst, fitthesis.cls, *.tex, *.bib, *.bst, fig/*, Makefile}
cp README.* .cd/
#tar czvf bp-xgrana02.tar.gz czechiso.bst fitthesis.cls *.tex *.bib *.bst ./fig/* Makefile
#rm -rf .cd
