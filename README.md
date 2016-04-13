# README #

## Tree controlled grammar parser (TCGP) ##

Tree controlled grammar parser is a part of bachelor thesis: Parsing Based on Tree-Controled Grammars, Brno University of Technology 2016.

Basic usage is for verification, that text string belongs to specified grammar.
This parser expands common LR parser, so it allows parsing of some non-context free grammars.

For execution use python3.

Usage:
~~~
python3 tcgp.py [-h] -g GRAMMAR [-p CHOICE [CHOICE ...]] [-i INPUT] [-o OUTPUT]
               [-u U]

Tree controlled grammar parser

optional arguments:
  -h, --help            show this help message and exit
  -g GRAMMAR, --grammar GRAMMAR
                        Input grammar file
  -p CHOICE [CHOICE ...], --print CHOICE [CHOICE ...]
                        Decide what to print from these CHOICES:
                         - tree:       final derivation tree
                         - trees:      derivation tree development
                         - stack:      continuously print stack of symbols
                         - rules:      continuously print applied rules
                         - groups:     lr groups generated from rules
                         - table:      lr table
                         - eff:        empty, first and follow sets
                         - automat:    print final state machine
                         - precedence: print precedence table
                         - grammar:    print input grammar
                         - all:        print all
  -i INPUT, --input INPUT
                        Input string file, tokens separated by white space
  -o OUTPUT, --output OUTPUT
                        Output file
~~~


### Grammar file ###

This file specifies tree controlled grammar.

Mandatory part is controlled grammar, which syntax is following,
this part must be defined first:

~~~
grammar = (
  {<id>, <id>, ..., <id>},         # nonterminals
  {<str>, <str>, ..., <str>},      # terminals
  {                                # rules
    <id> -> [<id>|<str>]* ;
    <id> -> [<id>|<str>]* ;
    ...
    <id> -> [<id>|<str>]* ;
  },
  <id>                             # start symbol
)
~~~

Other parts optional parts:

* `levels` - define control language by enumeration

~~~
levels = {
  [<str>]* ;                      # listed symbols
  [<str>]* ;
  ...
  [<str>]* ;
}
~~~

* `automaton` - define control language by finite automaton

~~~
automaton = (
  {<id>, <id>, ..., <id>},        # states
  {                               # rules
    <id> <str> -> <id> ;
    <id> <str> -> <id> ;
    ...
    <id> <str> -> <id> ;
  },
  <id>,                           # start state
  {<id>, <id>, ..., <id>}         # final states         
)
~~~

* `precedence` - define precedence rules for operators priority

~~~
precedence = (
  <dir>: [<id>|<str>], [<id>|<str>], ..., [<id>|<str>] ;
  <dir>: [<id>|<str>], [<id>|<str>], ..., [<id>|<str>] ;
  ...
  <dir>: [<id>|<str>], [<id>|<str>], ..., [<id>|<str>] ;
)
~~~

Meaning of shortcuts in syntax of grammar file:

* <id>  - c-like id
* <str> - string bounded by simple quotes (`'`), quote can escaped by `\`
* <dir> - associativity direction in precedence table, values:
    * `left`      - left associativity
    * `right`     - right associativity
    * `nonassoc`  - no associativity, considered as error