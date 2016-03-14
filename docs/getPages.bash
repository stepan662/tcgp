#!/bin/bash

characters=$(detex obsah.tex | sed '/^\s*$/d' | wc -m)
pages=$(bc <<< "scale=3; $characters / 1800")

echo "Znaku: $characters"
echo "Normovanych stran: $pages"
