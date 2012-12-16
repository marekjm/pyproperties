#### Release 0.2.0


>   This is the first ```beta``` release. It introduces more strict rules about how properties are parsed, better manual and more unit tests. 
>   For me it is end of a semester so no big things or improvements (I have plenty of school-related stuff). 
>   
>   Also, ```pyproperties``` reached the 1000 lines (1012 to be exact with 513 of them actual code).


----


##### This release brings you:
*   4 update(s),
*   1 fix(es),
*   7 new feature(s).


#### Version 0.2.0 (2012.12.16):

* __upd__:  ```_convert()``` can convert positive and negative hexadecimal and octal integers,
* __upd__:  slight change in regular expression patterns; ```[-]?``` changed to ```-?```,
* __upd__:  ```onlyhexchars()``` renamed to ```ishex()```,
* __upd__:  ```getlinekey()``` has new ```strict``` argument (read DOC for more),


* __fix__:  ```getlinekey()``` is more strict and accurate,


* __new__:  ```__vertuple__``` variable,
* __new__:  ```guess_hex_re``` regular expression,
* __new__:  ```guess_oct_re``` regular expression,
* __new__:  ```isoct()``` method,
* __new__:  new ```_getidentifier()``` method for compiling regular expression patterns of identifiers in 
    methods dealing with multiple properties at once (the ```-s()``` methods),
* __new__:  ```_iscommentline()``` method,
* __new__:  global ```strict``` variable (read DOC for ```getlinekey()``` or [this manual](manual/keys_and_values.mdown) for more information),

&nbsp;

Yours,  
Marek Marecki.