# README #

## Tree controlled grammar parser (TCGP) ##

For running use python3.

### Grammar file ###

This file specifies tree controlled grammar.

Mandatory part is controlled grammar, which syntax is following:

```
grammar = (
 {<id>, <id>, ..., <id>},          # nonterminals
 {<str>, <str>, ..., <str>},       # terminals
 {
  
 }
)
```