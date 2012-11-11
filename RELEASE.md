#### Release 0.1.5

>   This release brings new submethod which runs during store(). It is called _dump().
>   While it is yet-another-one submethod in store() it gives programmer even greter control
>   over the process of writing properties to file. By passing 'no_dump' argument as True to
>   store() method you can tell it to only generate lines and use your custom function to write 
>   them to file.

---------------------------------------------------------------------------------------------


##### This release brings you:
*   1 update(s),
*   1 fix(es),
*   6 new feature(s).


* __upd__:  ```addcomment()``` takes list of strings as an argumet, read DOC for more
* __fix__:  fixed regexp used in multi- methods (they were not catching properties whose names contained '-' inside)
* __new__:  ```store()``` has new submethod: ```_dump()``` which takes previously generated lines and writes them to file; read DOC for more,
* __new__:  ```store()``` accepts ```no_dump``` argument which tells it to finish after generating lines,
* __new__:  ```__init__()``` accepts ```no_read``` argument which tells it to dont't read the file of specified path, creates blank props with set path
* __new__:  ```__extractcomments__()``` method which cuts comments out from the source and saves them to the ```propcomments``` variable
* __new__:  ```getcomment()``` method which returns comment of a property
* __new__:  ```store()``` has new submethod - ```_storecomment()``` which is responsible for storing comments,


Yours,
Marek Marecki.