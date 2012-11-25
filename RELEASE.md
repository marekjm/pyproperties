#### Release 0.1.7

>   Fixes in the lowest level internals of ```pyproperties```for bugs which were uncovered by introducing ```_makeincludes()``` and ```_include()``` 
>   methods. They are not mentioned in Changelog because (shame on me) I have not kept track of them. But since they are fixed I hope you will forgive me.  
>   What is funny for me that the ```read()``` method which I considered kind of low-level actually turns out to be very _high_ level. 
>   Adding capability of ```__include__``` directive to it was one line and one new argument. 
>   And if a method needed only one line to add a whole new functionality which spans multiple lines of backstage implementation it is certainly high level.  
>   ```__include__``` is covered by four unit tests - for simple, prefixed, commented and prefixed/commented include.  
>
>   There is also new manual describing usage of [```__include__```](manual/include.mdown).


----


##### This release brings you:
*   9 update(s),
*   1 fix(es),
*   3 new feature(s).


* __upd__:  ```__tcasts__()```, ```__tcast__()``` and ```__typeguess__()``` were renamed to ```_tcast()```, ```_tcasts()``` and ```_typeguess()``` respectively,
* __upd__:  ```__getkey__()``` and ```__getvalue__()``` were renamed to ```_getlinekey()```, ```_getlinevalue()```,
* __upd__:  ```__isvalidline__()``` was renamed to ```_isvalidline()```,
* __upd__:  ```__iscommentedprop__()``` was renamed to ```_islinecommentedprop()```,
* __upd__:  ```__iscommentedprop__()``` was renamed to ```_islinecommentedprop()```,
* __upd__:  ```__iscommentedprop__()``` was renamed to ```_islinecommentedprop()```,
* __upd__:  ```addcomment()```, ```rmcomment()``` and ```uncomment()``` have ```self.unsaved = True``` line removed because all of these actions implicitly 
    set this variable to ```False```
* __upd__:  ```__extracteprops__()``` and ```__extractcommentedprops__()``` use ```enumerate()``` instead of expilict ```while``` loop,
* __upd__:  ```__split__()``` use ```enumerate()``` instead of expilict ```while``` loop,


* __fix__:  ```copy()``` copies status (commented/not-commented) of properties,


* __new__:  ```no_includes``` argument in which tell ```read()``` whether it should include other files into one that is being loaded or not,
* __new__:  ```no_source``` argument in ```store()``` which drops the original source,
* __new__:  unit tests for ```__include__``` directive,

&nbsp;

Yours,  
Marek Marecki.