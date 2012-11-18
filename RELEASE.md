#### Release 0.1.6

>   This release brings full support for comments. You can now read, write and modify properties 
>   comments using methods provided by ```pyproperties```. What is more - it is possible to comment 
>   a property and it will become unmodifiable. During ```store()``` commented properties are 
>   saved as with preceding '#' character.
>   ```pyproperties``` can distinguish ordinary comments from commented property. This was inspired 
>   by ```*.properties``` used by [SciTE](http://www.scintilla.org/SciTE.html) where ```# comment: #``` is a comment but ```#comment: #```
>   is comented property. As you see - whitespace matters.  
>   Main goal for version 0.1.6 was to improve support for comments but this great functionality 
>   is not everything what is included. 
>   Unit tests for ```pyproperties``` were updated and in some places refactored. Few of them had been
>   deleted but new ones emerged in an instant and now ```pyproperties``` is armed with about _60_
>   unit tests.
>   
>   This release is not backward compatible with previous versions. But since everything is in [changelog](Changelog.md) it will not be a
>   huge pain.
>
>   Note: from this release all manuals are formatted using Markdown.

---------------------------------------------------------------------------------------------


##### This release brings you:
*   10 update(s),
*   7 fix(es),
*   5 new feature(s).


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


Yours,
Marek Marecki.