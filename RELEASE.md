#### Release 0.1.8


>   This is very poor release. I am sorry but I was busy with school stuff. 
>   After all I need to pass this semester (rember your highschool time?). 
>
>   This release brings just three updates, and five bug fixes. Not impressive at all. 
>   I will try to do better next week.


----


##### This release brings you:
*   3 update(s),
*   5 fix(es),
*   1 new feature(s).


#### Version 0.1.8 ():

* __upd__:  ```no_source``` argument in ```store()``` renamed to ```drop_source```,
* __upd__:  changes in ```read()```, it now uses ```blank()``` to create all initial variables and generate path and name,
* __upd__:  argument ```idetifier``` in ```remove()``` renamed to ```key``` - it only applies to one key, identifiers apply to many keys,


* __fix__:  ```reload()``` requires ```save()```,
* __fix__:  ```refresh()``` requires ```save()```,
* __fix__:  ```remove()``` removes comment attached to the property from the dict,
* __fix__:  ```copy()``` now works with files containing commented properties,
* __fix__:  ```getnames()``` has new argument - ```commented``` which if set to ```True``` returns names of commented properties 
    (this fixes situation when you were not able to get names of commented properties at all),


* __new__:  ```path``` argument in ```blank()``` method,

&nbsp;

Yours,  
Marek Marecki.