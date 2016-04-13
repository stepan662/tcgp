# README #

## Tree controlled grammar parser (TCGP) ##

For running use python3.

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