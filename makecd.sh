#!/bin/bash
echo "Creating CD structure ..."
mkdir .cd
mkdir .cd/src
mkdir .cd/docs
mkdir .cd/docs/fig
mkdir .cd/tests
mkdir .cd/tests/outputs

echo "Copying files ..."
cp docs/*.tex .cd/docs/
cp docs/*.bib .cd/docs/
cp docs/*.bst .cd/docs/
cp docs/fitthesis.cls .cd/docs/
cp docs/fig/* .cd/docs/fig/
cp docs/Makefile .cd/docs/
cp README.* .cd/
cp *.py .cd/src/
cp ../tcgp-tests/*.in .cd/tests
cp ../tcgp-tests/test.sh .cd/tests
# change relative position in test.sh file
sed -i -e 's/BINARY="python3 ..\/tcgp\/tcgp.py"/BINARY="python3 ..\/src\/tcgp.py"/g' .cd/tests/test.sh

echo "Building documentation ..."
cd .cd/docs
make > /dev/null
cp thesis.pdf ../
make clean > /dev/null
cd ..

echo "Building archive ..."
tar czvf ../bp-xgrana02.tar.gz * >/dev/null

cd ..

echo "Removing temporary files ..."
rm -r -f ".cd"
