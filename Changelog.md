#### Changelog file for pyproperties

------------------------------------------------

#### Version 0.1.6 ():

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

&nbsp; 

#### Version 0.1.5 (2012.11.11):

* __upd__:  ```addcomment()``` takes list of strings as an argumet, read DOC for more


* __fix__:  fixed regexp used in multi- methods (they were not catching properties whose names contained '-' inside)


* __new__:  ```store()``` has new submethod: ```_dump()``` which takes previously generated lines and writes them to file; read DOC for more,
* __new__:  ```store()``` accepts ```no_dump``` argument which tells it to finish after generating lines,
* __new__:  ```__init__()``` accepts ```no_read``` argument which tells it to dont't read the file of specified path, creates blank props with set path
* __new__:  ```__extractcomments__()``` method which cuts comments out from the source and saves them to the ```propcomments``` variable
* __new__:  ```getcomment()``` method which returns comment of a property
* __new__:  ```store()``` has new submethod - ```_storecomment()``` which is responsible for storing comments,
