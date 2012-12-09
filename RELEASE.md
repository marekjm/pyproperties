#### Release 0.1.9


>   This release breaks backwards compatibility with all previous versions. It is due to changes in behaviour of some methods and 
>   renamed methods related to properties comments and _hiding_. Yes - _hiding_. I have finally found a proper name for this.  
>   Commented properties are the ones which have comments attached to them. And hidden properties (don't you think it is a good name?) are 
>   the ones which are, well, hidden.  
>   
>   &nbsp;
>
>   In this release one unit test was removed due to simplification of the ```parse()``` method.  
>
>   &nbsp;
>
>   Many internal methods were renamed to use ```_single()``` preceding underscore instead of two ```__underscores__()``` on both sides. 
>   This change improved readablility and provided easily spottable distinction between provided API and internal methods.  
>
>   &nbsp;
>
>   ```0.1.9``` is the last _alpha_ release and last from line ```0.1.x```. ```pyproperties``` is now entering _beta_ stage and line ```0.2.x```. 


----


##### This release brings you:
*   19 update(s),
*   1 fix(es),
*   4 new feature(s).


#### Version 0.1.9 (2012.12.09):

* __upd__:  ```_typeguess()``` renamed to ```typeguess()```,
* __upd__:  ```__tcast__()``` and ```__tcasts__()``` renamed to ```_tcast()``` and ```_tcasts()``` respectively,
* __upd__:  ```_getlinekey()``` renamed to ```getlinekey()```,
* __upd__:  ```_getlinevalue()``` renamed to ```getlinevalue()```,
* __upd__:  ```comment()``` renamed to ```hide()```,
* __upd__:  ```commented``` argument in ```_include()``` renamed to ```hidden```,
* __upd__:  ```commented``` keyword in properties files renamed to ```hidden```,
* __upd__:  ```commented``` internal variable was renamed to ```hidden```,
* __upd__:  all ```__extract*__``` methods were renamed to ```_extract*```,
* __upd__:  ```__split__()``` renamed to ```_split()```,
* __upd__:  ```__loadf__()``` renamed to ```_loadf()```,
* __upd__:  ```getcomment()``` returns a string (lines are joined with unescaped ```\n```),
* __upd__:  ```remove()``` no longer issues KeyErrors,
* __upd__:  ```parse()``` returns ```pyproperties.Properties``` object by deafult, functionality for returning simple dict is removed,
* __upd__:  ```parseline()``` renamed to ```_parseline()```,
* __upd__:  ```parsed``` argument in ```get()```, ```gets()```, ```getre()``` renamed to ```parse```,
* __upd__:  ```_tcast()``` now uses ```_convert()``` as backend (it provides convertion to more types),
* __upd__:  ```__loadd__()``` renamed to ```_loadd()``` and issues a warning when used,
* __upd__:  ```getlinevalue()``` no longer removes backslash preceding whitespace at the beginning of value,


* __fix__:  ```hide()``` does not allow duplicates,


* __new__:  ```set()``` now has default value (empty string) for new properties,
* __new__:  ```_notavailable()``` method which issuse KeyError with appropriate message,
* __new__:  ```getcomment()``` has new argument - ___```(bool)```___```lines``` which will tell it to give you lines (list of strings) instead of string,
* __new__:  ```_convert()``` method which can convert property from ```str``` to ```bool``` (```True``` & ```False```), ```int```, ```float```, ```None```,
    read ```manual/casting.mdown``` for more details,

&nbsp;

Yours,  
Marek Marecki.