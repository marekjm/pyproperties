#### Changelog file for pyproperties


----


#### Version 0.1.8 (2012.12.02):

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


----


#### Version 0.1.7 (2012.11.25):

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


----


#### Version 0.1.6 (2012.11.18):

* __upd__:  ```__extract__()``` renamed to ```__extractprops__()```
* __upd__:  changed way of compiling regexp idetifiers
* __upd__:  ```merge()``` renamed to ```update()``` to have a name which is more accurate,
* __upd__:  ```addcomment()``` stores plain (without '#' and whitespace on the begining) text,
* __upd__:  ```complete()``` completes value, comment and status (un/commented) of properties, 
* __upd__:  ```rsave()``` renamed to ```revert()```, 
* __upd__:  because the name was freed ```melt()``` is now renamed to ```merge()```, 
* __upd__:  from now on also ```hexadecimal``` numbers are considered groupers by the ```getgroups()``` method, 
* __upd__:  updated old regexp in ```__tcasts__()``` method, 
* __upd__:  pyproperties will warn user if there are duplicates in loaded file, if they are found only last value if loaded


* __fix__:  ```_storesrc()``` takes values from ```propsorigin``` and not ```properties```
* __fix__:  when searching for comments ```__extractcomments__()``` will not wrap around the file end 
    (bug fixed but not listed in version 0.1.5),
* __fix__:  comments have origin-style variable now: ```origin_propcomments```, 
* __fix__:  save now saves ```origin_propcomments```, 
* __fix__:  ```__extractcomments__()``` saves also to ```origin_propcomments```, 
* __fix__:  ```complete()``` and ```merge()``` are now taking props from the ```origins``` variables, 
* __fix__:  fixed a bug in storing procedure which would crash the process if some properties from original file were removed, 


* __new__:  ```__extractcommentedprops__()``` method, read ```manual/commenting.txt``` to learn more
* __new__:  ```comment()``` and ```uncomment()``` methods added, read ```manual/commenting.txt``` to learn more
* __new__:  ```comments()``` and ```uncomments()``` methods added, read ```manual/commenting.txt``` to learn more
* __new__:  unit tests for comments added,
* __new__:  ```_storeprop()``` method which generate lines for single property, saved a few lines with this reusable code,


----


#### Version 0.1.5 (2012.11.11):

* __upd__:  ```addcomment()``` takes list of strings as an argumet, read DOC for more


* __fix__:  fixed regexp used in multi- methods (they were not catching properties whose names contained '-' inside)


* __new__:  ```store()``` has new submethod: ```_dump()``` which takes previously generated lines and writes them to file; read DOC for more,
* __new__:  ```store()``` accepts ```no_dump``` argument which tells it to finish after generating lines,
* __new__:  ```__init__()``` accepts ```no_read``` argument which tells it to dont't read the file of specified path, creates blank props with set path
* __new__:  ```__extractcomments__()``` method which cuts comments out from the source and saves them to the ```propcomments``` variable
* __new__:  ```getcomment()``` method which returns comment of a property
* __new__:  ```store()``` has new submethod - ```_storecomment()``` which is responsible for storing comments,
