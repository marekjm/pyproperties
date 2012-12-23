#### Release 0.2.1


>   This release brings deprecation of ```_isvalidline()``` in favour of ```_linehaskey()```. 
>   _Being a valid line_ was too broad term and the method functionality really had been to check if a line contained a valid key. 
>   The new ```_linehaskey()``` method has more functionality: it will not only check if a line contains a key but also will issue a warning if the key 
>   is not valid (this depend on parser mode).
>
>   What is more, ```typeguess()``` is also deprecated in favour of internal method ```_convert()```. It is not only more powerful but is actualy 
>   being used. I realised that ```typeguess()``` was a piece of _dead code_. It is shame to say that but even it's docstring was not accurate... 
>   And so the method became deprecated and will be removed in version ```0.2.2```.
>
>   ```strict``` argument was also removed from bunch of methods in order to simplify them. Now, the only methods able to accept ```strict``` as an argument are 
>   ```blank()``` and ```read()``` (and ```__init__()``` but this is not used explicitly).


----


##### This release brings you:
*   9 update(s),
*   3 fix(es),
*   4 new feature(s),
*   1 removal(s),


#### Version 0.2.1 (2012.12.14):

* __upd__:  mode ```strict``` defaults to ```True```,
* __upd__:  checking line validity is now performed by ```_linehaskey()``` inside ```pyproperties``` and ```_isvalidline()``` becomes deprecated,
* __upd__:  ```copy()``` uses ```merge()``` as a backend instead of copying everything by itself,
* __upd__:  ```_getidentifier()``` renamed to ```_expandidentifier()``` and does not return compiled pattern,
* __upd__:  ```identifier``` in ```pop()``` renamed to ```key```,
* __upd__:  ```strict``` argument removed from ```getlinekey()```,
* __upd__:  change in ```guess_hex_re``` and ```guess_oct_re``` - ```0x``` and ```0o``` prefixes are now mandatory,
* __upd__:  octal numbers are considered groupers by ```getgroups()```,
* __upd__:  deprecation of ```_isvalidline()``` and ```typeguess()```,


* __fix__:  changed mistake in [grouping manual](manual/grouping.mdown),
* __fix__:  ```removes()``` uses ```_expandidentifier()``` to get pattern for regular expression,
* __fix__:  improved accuracy of ```_islinehiddenprop()``` by checking if the comment character is not followed by whitespace (``` ```),


* __new__:  ```_linehaskey()``` method used for checking if line contains a key,
* __new__:  ```_isvalidline()``` is deprecated and will issue warnings about that - you should use ```_linehaskey()``` as it provides better accuracy,
* __new__:  unit tests for ```_islinehiddenprop()```,
* __new__:  method ```setstrict()``` for setting parser mode,


* __rem__:  unit tests for ```_isvalidline()``` removed (due to its deprecation - it is now only a proxy for ```_linehaskey()```)


&nbsp;

Yours,  
Marek Marecki.