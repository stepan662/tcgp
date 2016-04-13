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