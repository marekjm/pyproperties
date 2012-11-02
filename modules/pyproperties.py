#!/usr/bin/python3

"""Working with *.properties files.

pyproperites aims to ease manipulation, interaction and use of *.properties files in Python 3.x programs.

It features:
    *   merging different properties with merge() method,
    *   comleteing different properties with complete() method,
    *   getter for single and multiple ('foo.*') properties,
    *   setter for single and multiple ('foo.*') properties,
    *   joining multiple properties files with join() method,
    *   storing loaded properties while preserving comments and empty lines,
    *   parsing loaded properties,
    *   parsing single lines,
    *   referencing other properties values with $(foo.bar) syntax, 
    *   removing and poping single an multiple properties, 
    *   guessing types of properties (str, int, float) and casting them during load and post-load,
    *   securing your work by providing you two dictionaries - one for saved work and one as a 'working copy',
    *   pyproperites is capable of reading properties splitted into several lines, 
    *   commenting loaded properties,
"""

import os
import re


__version__ = "0.1.4"


wildcart_re = "[a-z0-9_.]*"
guess_int_re = "^[+-]{0,1}[0-9]+$"
guess_float_re = "^[+-]{0,1}[0-9]*\.[0-9]+$"


class LoadError(IOError): pass
class StoreError(IOError): pass
class UnsavedChangesError(BaseException): pass


class Properties():
    """
    This class provides methods for working with properties files. 
    You should call it with a path pointing to the file you want to load. 

    It contains variables used for working with properties files:

        self.path           -   path used for reading and storing properties,
        self.source         -   working copy of source file
        self.srcorigin      -   original lines of source file
        self.properties     -   working copy of properties dictionary
        self.propsorigin    -   original dictionary of properties
        self.propcomments   -   dictionary storing comments of properties (only added by pyproperites interface)
    """

    def __init__( self, path = "", type_convert=False ):
        """
        If you give a path as an argument it will be loaded and processed as properties file. 
        If you call Properties() without an argument created object will be "blank" - in this case you will have to call 
        foo.read( path, type_convert ) to load some properties or 
        you can use the blank properties to create completly new set of properties.
        You can pass type_convert as True to tell pyproperites that it should guess the type of the property 
        and convert it accordingly.

        This method (__init__) just calls read() with arguments passed to itself.
        """
        if path != "" and not path.isspace(): self.read( path, type_convert )
        elif path == "" : self.blank()


    def __loadf__( self, path ):
        """
        This method loads properties file from given path to a self.source list. 
        It also strips it of any newline character and whitespace on both sides but leaves it otherwise unprocessed. 
        """
        srcorigin = []
        source = []
        src = open( path, "rt" )
        source = src.readlines()
        src.close()
        for i in range( len( source ) ): 
            source[i] = source[i].lstrip()
            srcorigin.append( source[i] )
        self.source = source
        self.srcorigin = srcorigin


    def __loadd__( self, path ):
        """
        This method reads directory tree as if it was properties file.
        """
        srcorigin = []
        source = []
        proppaths = []
        propnames = []
        propvalues = {}

        for root, dirs, files in os.walk( self.path ):
            for file in files :
                proppaths.append( os.path.normpath( os.path.abspath( "{0}{1}{2}".format( root, os.path.sep, file ) ) ) )

        for i in range( len( proppaths ) ):
            propnames.append( proppaths[i].replace("{0}{1}".format(self.path, os.path.sep), "").replace( os.path.sep, "." ) )

        for i in range( len( proppaths ) ):
            value = open( proppaths[i] ).read()
            if value[-2:] == "\\n" : value = value[:-2]
            propvalues[ propnames[i] ] = value

        for key, value in propvalues.items():
            source.append( "{0}={1}".format(key, value) )

        self.source = source
        self.srcorigin = srcorigin


    def __isvalidline__( self, line ):
        """
        Checks if the line contains valid property string. 
        valid string is not an empty string and its first character is not '#'.
        """
        result = line != "" and line[0] not in ["#", "!"]
        return result


    def __extract__( self ):
        """
        Extracts lines containing valid properties strings from loaded source to self.properties 
        It parses self.source line by line. 
        Every line begining with # is considered comment and not parsed. 
        Lines containing only whitespace are also not parsed. 
        """
        extracted = []
        properties = []
        for i in range( len( self.source ) ):
            if self.__isvalidline__( self.source[i] ): extracted.append( self.source[i] )

        i = 0
        while i < len( extracted ):
            line = extracted[i]
            while line[-1] == "\\" :    #  if line ends with backslash read next line and append it to
                i += 1
                line = line[:-1] + extracted[i].lstrip()
            properties.append( line.lstrip() )
            i += 1
        self.properties = properties


    def __split__( self ):
        """
        This methode converts self.properties from list containing extracted lines to a dictionary.
        """
        props = {}
        origin = {}
        for i in range( len( self.properties ) ): 
            key = self.__getkey__( self.properties[i] )
            value = self.__getvalue__(self.properties[i])
            origin[key] = props[key] = value
        self.propsorigin = origin
        self.properties = props


    def __tcast__( self, identifier ):
        """
        Converts property of the given key from str (default) to int or float if needed.
        """
        ptype = self.__typeguess__( self.get( identifier ) )
        self.set( identifier, ptype( self.get( identifier ) ) )


    def __tcasts__( self, identifier ):
        """
        Converts properties from str (default) to int or float (if needed). 
        """
        keys = []
        identifier = re.compile( identifier.replace("*", wildcart_re) )
        for key in self.properties.keys():
            if re.match(identifier, key): keys.append( key )
        for key in keys : self.__tcast__( key )


    def __typeguess__(self, prop):
        """
        Tries to guess the type of property (initially all properties are stored as strings) and 
        convert it accordingly.
        It can guess three types: int, float and string.
        If property contains only digits and a dot inside - it's considered float (re: "^[0-9]*\.[0-9]+$").
        If property contains only digits and not a dot inside - it's considered int (re: "^[0-9]+$").
        Otherwise: property is considered str.
        """
        re_int = re.compile(guess_int_re)
        re_float = re.compile(guess_float_re)

        if re.match(re_int, prop): ptype = int
        elif re.match(re_float, prop): ptype = float
        else : ptype = str
        return ptype


    def __getkey__( self, line):
        """
        Extracts key from given line and returns it. 
        If the line is comment or is blank returns None.
        """
        if line == "" : key = None
        elif line[0] in ["#", "!"] or line.isspace(): key = None
        elif ":" in line[:line.find("=")]: key = line.split(":", 1)[0]
        else : key = line.split("=", 1)[0]
        return key.strip()


    def __getvalue__( self, line ):
        """
        Extracts value from given line and returns it. 
        If the line is comment or is blank returns None. 
        It is done this way to distinguish properties with empty value 
        from lines which do not carry a property.
        """
        if line[-1] == "\n": line = line[:-1]   # striping newline while preserving newlines in value and trailing whitespace
        if line == "" : value = None
        elif line[0] in ["#", "!"] or line.isspace(): value = None
        elif ":" in line[:line.find("=")]: value = line.split(":", 1)[1].lstrip()
        else: value = line.split("=", 1)[1].lstrip()
        if value:
            if value[0] == "\\": value = value[1:]
        return value


    def _appendsrc(self, props, prefix=""):
        """
        This methods appends source of given properties 
        to the base.
        """
        lines = []
        for line in props.srcorigin:
            if line == "": lines.append(line)
            elif line[0] in ["#", "!"] or line.isspace(): lines.append(line)
            elif self.__isvalidline__(line) and not prefix: lines.append(line)
            elif self.__isvalidline__(line) and prefix: lines.append("{0}.{1}".format(prefix, line))
            else: pass
        if self.source: self.source.append("")
        self.source.extend(lines)


    def blank(self):
        """
        Creates blank properties object.
        """
        self.path = ""
        self.name = ""
        self.srcorigin = []
        self.source = []
        self.properties = {}
        self.propsorigin = {}
        self.propcomments = {}
        self.unsaved = False


    def read(self, path, cast=False):
        """
        Reads properties file and processes it to be available in Python 3 program.
        This method defines self.path and extracts name of loaded properties file and stores it in self.name.
        Then runs these methods in following order:
            self.__load__( path )
            self.__extract__()
            self.__split__()
        You can pass cast as True to tell pyproperites that it should guess the type of the property 
        and convert it accordingly (the __tcasts__ method will be called).
        """
        self.path = os.path.expanduser( path ).strip()
        self.name = os.path.splitext( os.path.split( self.path )[-1] )[0]
        if os.path.isfile( self.path ): self.__loadf__( self.path )
        elif os.path.isdir( self.path ): self.__loadd__( self.path )
        else : raise LoadError("'{0}' no such file or directory".format( path ) )
        self.__extract__()
        self.__split__()
        if cast : self.__tcasts__( "*" )
        self.propcomments = {}
        self.unsaved = False


    def reload( self ):
        """
        Reloads from file. Missing values are added. Existing values are overwritten. 
        Values which are not found in file are deleted.
        """
        new = Properties( self.path )
        self.source = new.source
        self.properties = new.properties


    def refresh( self, overwrite=True ):
        """
        Refreshes from file. Missing values are added.
        If 'overwrite' is set to True existing values are overwritten - merge() is used.
        'overwrite' defaults to True.
        Values which are not found in file are not deleted.
        """
        new = Properties( self.path )
        self.complete( new, "" )
        if overwrite : self.merge( new )


    def parseline( self, value ):
        """
        This method searches for every $(reference) string in given line and 
        replaces it with value of corresponding property. 
        """
        init_value = value
        while "$(" in value and ")" in value :
            a = value.find("$(")
            b = value[a:].find(")")
            name = value[a+2 : a+b]
            if a == -1 or b == -1 : break
            value = value.replace("$({0})".format(name), str( self.properties[name] ) )
        return value


    def parse( self, cast=False, props=False ):
        """
        This methode parses and returns parsed self.properties

        If props argument is passed as True parse() will return
        an Properties() object with all values parsed.
        """
        if props:
            parsed = Properties()
            parsed.melt(self)
            parsed.properties = parsed.parse()
            parsed.save()
        else :
            parsed = {}
            for key in self.properties: parsed[key] = self.get( key, True, cast )
        return parsed


    def copy(self):
        """
        Returns exact copy of a Properties() object.
        """
        return self


    def join(self, path, prefix=" "):
        """
        Loads external properties and completes base. 
        You can pass 'prefix' as empty string to add properties without prefix. 
        Prefix defaluts to joined modules name. 
        Source of joined properties is appended to base source.
        """
        path = path.strip()
        new = None
        try : 
            new = Properties( path )
            if prefix == " " : prefix = new.name
        except IOError : 
            print( "\v\tIOError: [Errno 2]: file not found '{0}': properties cannot be joined\v".format( path ) )
            raise
        finally :
            if new :
                self.complete( new, prefix )
                self._appendsrc(new, prefix)
            else : pass
        self.unsaved = True


    def melt(self, properties ):
        """
        Completes and merges 'properties' with the base. 

        Source of melted properties is appended to base.
        """
        self.complete( properties )
        self.merge( properties )
        self.source.append("")
        self.source += properties.source
        self.unsaved = True


    def complete( self, props, prefix="" ):
        """
        This methode completes base dictionary with properties of the given one. 
        If the base does not have some property it will be added. 
        Values of the existing properties will be not overwritten. 

        Source of merged properties are not appended to the base.
        """
        for key, value in props.properties.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.properties : self.properties[key] = value
        self.unsaved = True


    def merge( self, props, with_prefix="" ):
        """
        This methode base dictionary with the given one. 
        If the base does not have some property it will not be added. 
        Values of the existing properties will be overwritten. 

        If prefix is specified only properties which are preceded with 
        this key will have their value changed.

        Source of merged properties are not appended to the base.
        """
        for key, value in props.properties.items(): 
            if with_prefix: key = "{0}.{1}".format( with_prefix, key )
            if key in self.properties: self.properties[key] = value
        self.unsaved = True


    def save(self):
        """
        Saves changes made in self.properties by moving self.properties to self.propsorigin
        and self.source to self.srcorigin
        """
        saved = {}
        for key, value in self.properties.items(): saved[key] = value
        self.propsorigin = saved
        saved = []
        for line in self.source: saved.append( line )
        self.srcorigin = saved
        self.unsaved = False


    def rsave(self):
        """
        Undoes changes made in self.properties by moving self.propsorigin to self.properties
        and self.srcorigin to self.source
        """
        rsaved = {}
        for key, value in self.propsorigin.items(): rsaved[key] = value
        self.properties = rsaved
        rsaved = []
        for line in self.srcorigin: rsaved.append( line )
        self.source = rsaved
        self.unsaved = False


    def _storesrc(self):
        """
        Prepares data which came with source for storing.
        """
        for i in range( len( self.srcorigin ) ): 
            if self.source[i] == "" : self.lines.append( "{0}".format( self.srcorigin[i] ) )
            elif self.source[i][0] == "#" : self.lines.append( "{0}".format( self.srcorigin[i] ) )
            # checks if current line has a key which is in defined in self.propsorigin and has not been stored yet
            elif self.__getkey__( self.srcorigin[i] ) != "" and self.__getkey__( self.srcorigin[i] ) not in self.stored: 
                # appends comments attached by the program
                if self.__getkey__(self.srcorigin[i]) in self.propcomments: [ self.lines.append("{0}".format(line)) for line in self.propcomments[self.__getkey__(self.srcorigin[i])] ]
                self.lines.append( "{0}={1}".format(self.__getkey__(self.source[i]), self.propsorigin[self.__getkey__(self.source[i])] ) )
                self.stored.append( self.__getkey__( self.source[i] ) )
            else : pass


    def _storegroups(self):
        """
        Prepares groups not found in source file.
        """
        if self.lines != [] : self.lines.append("")
        groups = self.getgroups()
        for identifier in groups:
            previous_len = len(self.lines)
            props = self.gets( identifier )
            keys = []
            [ keys.append(key) for key in props ]
            for key in sorted(keys):
                if key not in self.stored and key in self.propsorigin:
                    if key in self.propcomments: [ self.lines.append( "{0}".format(line) ) for line in self.propcomments[ key ] ]
                    self.lines.append( "{0}={1}".format(key, props[key]) )
                    self.stored.append( key )
            if len(self.lines) > previous_len: self.lines.append("")


    def _storesingles(self):
        """
        Preprares single values not found in source.
        """
        for key, value in self.propsorigin.items():
            if key not in self.stored : 
                if key in self.propcomments: [ self.lines.append( "{0}".format(line) ) for line in self.propcomments[ key ] ]
                self.lines.append( "{0}={1}".format(key, value) )
                self.stored.append( key )


    def store(self, path = "", force=False):
        """
        Writes properties to given 'path'.
        'path' defaults to self.path

        If store will encounter some unsaved changes it will
        raise UnsavedChangesError.
        You can explicitly silence it by passing force as True.

        If self.path is empty it will be set to given path.
        """
        if self.unsaved and not force: raise UnsavedChangesError("trying to store with unsaved changes")
        self.stored = []
        self.lines = []
        if path == "" : path = self.path    # this line defaults the value
        if path == "" or path.isspace(): raise StoreError("no path specified")
        if path and not self.path: self.path = path
        self._storesrc()
        self._storegroups()
        self._storesingles()
        file = open( path, "w" )
        for line in self.lines: file.write( "{0}\n".format(line) )
        file.close()
        self.stored = []
        self.lines = []


    def get(self, identifier, parsed=False, cast=False):
        """
        Returns value of identifier. 
        If identifier is not found KeyError is raised.
        If parsed is set to True value will be parsed before returning.
        """
        if type(identifier) is not str: raise TypeError("identifer must be string but '{0}' was given".format( str(type(identifier))[8:-2] ) )
        if parsed : value = self.parseline( self.properties[identifier] )
        else : value = self.properties[identifier]
        if cast : value = self.__typeguess__( value )(value)
        return value


    def gets(self, identifier, parsed=False, cast=False):
        """
        Returns dict of properties which names matched pattern given as identifier.
        If parsed is set to True values will be parsed before returning.
        """
        if type(identifier) is not str: raise TypeError("identifer must be string but '{0}' was given".format( str(type(identifier))[8:-2] ) )

        matched = {}
        identifier = re.compile("^{0}$".format(identifier.replace("*", wildcart_re).replace(".", "\.")))
        for key, value in self.properties.items():
            if re.match(identifier, key) and parsed : matched[key] = self.parseline( value )
            elif re.match(identifier, key) and not parsed : matched[key] = value
        if cast : 
            for key, value in matched.items(): matched[key] = self.__typeguess__( value )( value )
        return matched


    def getre(self, identifier, parsed=False, cast=False):
        """
        Returns dict of properties which names matched given pattern.
        If parsed is set to True values will be parsed before returning. 
        If cast is passed as True pyproperites will try to cast types of properties.
        """
        matched = {}
        if type(identifier) == str: identifier= re.compile( identifier )
        elif str(type(identifier)) == "<class '_sre.SRE_Pattern'>": pass
        else : raise TypeError("identifer must be either compiled or string regular expression pattern, but '{0}' type was given".format( str(type(identifier))[8:-2] ) )

        for key, value in self.properties.items():
            if re.match(identifier, key) and parsed : matched[key] = self.parseline( value )
            elif re.match(identifier, key) and not parsed : matched[key] = value
        if cast : 
            for key, value in matched.items(): matched[key] = self.__typeguess__( value )( value )
        return matched


    def set(self, identifier, value):
        """
        Sets key to value. 
        """
        self.properties[identifier] = value
        self.unsaved = True


    def sets(self, identifier, *values, **kwargs):
        """
        Sets every property which name matched pattern given as identifier to value. 
        You can pass more than one value. If more keys are found than values passed 
        last value is passed to every key above number of values. 

        After completing, sort() method is used on keys list so the first value goes to first key. 
        If the key is in kwargs its value if taken from the dict and the value counter is not increased. 
        If you want to keyword a property which name contains a dot character "." you should use __DOT__ 
        as a substitute for this character - 'foo__DOT__bar' will be converted to 'foo.bar'.
        """
        keys = []
        _kwargs = {}
        for key, value in kwargs.items(): _kwargs[key.replace("_DOT_", ".")] = value
        kwargs = _kwargs

        identifier = re.compile("^{0}$".format(identifier.replace("*", wildcart_re).replace(".", "\.")))
        for key, x in self.properties.items():
            if re.match(identifier, key): keys.append( key )

        keys.sort()
        i = 0
        for key in keys :
            try : value = values[i]
            except IndexError : value = values[-1]
            finally : 
                if key in kwargs : value = kwargs[key]
                else : i += 1   # increasing the counter if value wasn't taken from the kwargs
                self.set( key, value )
        self.unsaved = True


    def remove(self, identifier):
        """
        This methode removes specified property from interal dictionary. 
        Removed property will be not saved using store().
        """
        self.properties.pop( identifier )
        self.unsaved = True


    def removes(self, identifier):
        """
        This methode removes properties matching given pattern from interal dictionary. 
        Removed properties will be not saved using store().
        """
        to_remove = []
        identifier = re.compile("^{0}$".format(identifier.replace("*", wildcart_re).replace(".", "\.")))
        for key in self.properties.keys():
            if re.match( identifier, key ): to_remove.append( key )
        for key in to_remove : self.properties.pop( key )
        self.unsaved = True


    def pop(self, identifier, cast=False):
        """
        This methode removes specified property from interal dictionary and returns its value. 
        Removed property will be not saved using store().
        """
        prop = self.properties.pop( identifier )
        if cast : prop = self.__typeguess__( prop )( prop )
        self.unsaved = True
        return prop


    def pops(self, identifier, cast=False):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        Removed properties will be not saved using store().
        """
        popped = {}
        identifier = re.compile("^{0}$".format(identifier.replace("*", wildcart_re).replace(".", "\.")))
        for key, value in self.properties.items():
            if re.match( identifier, key ): 
                popped[key] = value
        for key in popped.keys(): self.properties.pop( key )
        if cast : 
            for key, value in popped.items():
                popped[key] = self.__typeguess__( value )( value )
        self.unsaved = True
        return popped


    def getnames(self):
        """
        Returns sorted list of the property names. 
        """
        return sorted( list( self.properties.keys() ) )


    def getkeysof( self, value ):
        """
        Returns list of keys containing given value. 
        Returns empty list if no key was matched.
        """
        keys = []
        for propkey, propvalue in self.properties.items():
            if value == propvalue : keys.append( propkey )
        return keys


    def getgroups(self):
        """
        Returns list of properties-groups in the internal dictionary. 
        Group is understood by two or more properties which can 
        be obtained with the same gets() identifier.

        For example:
            language.0=Python 2.x
            language.1=Python 3.x
        will form group with identifer 'language.*'. 

        And:
            customer.0.address=Some Street 16.
            customer.1.address=Other Street 17.
        will form group with identifer 'customer.*.address'. 

        But:
            person.name=John
            person.surname=Average
        will not form a group although gets('person.*') will return 
        list of length greater than two.

        This is because only digits are considered as 'groupers'.
        """
        skeys = []
        [ skeys.append( key.split(".") ) for key in self.getnames() ]
        groups = []
        for skey in skeys :
            identifier = ""
            for key in skey :
                if key.isdigit() : key = "*"
                identifier = "{}.{}".format(identifier, key)
            identifier = identifier[1:]
            if identifier not in groups and len( self.gets( identifier ) ) > 1 : groups.append( identifier )
        return groups


    def getsingles(self):
        """
        Returns list of properties which do not 
        belong to any group.
        """
        groups = self.getgroups()
        singles = []
        for key in self.getnames() :
            key = re.sub( re.compile("\.[0-9]+\."), ".*.", key )
            key = re.sub( re.compile("\.[0-9]+$"), ".*", key )
            if key not in groups : singles.append( key )
        return singles


    def addcomment(self, identifier, comment):
        """
        Attaches comment to property. 
        Comment can be passed as a string or a list. 
        Multiline comments are supported - either by passing a list of lines or
        by passing a string containing newline characters '\\n'.
        """
        if type(comment) == str and "\n" in comment: comment = comment.split("\n")
        elif type(comment) == list: pass
        else: comment = [comment]
        for i in range(len(comment)): comment[i] = "#\t{0}".format(comment[i])
        self.propcomments[ identifier ] = comment
        self.unsaved = True


    def addcomments(self, identifier, *comments):
        """
        Attaches comment to properties which will match the identifier. 
        Comment can be passed as a string or a list. 
        Multiline comments are supported - either by passing a list of lines or
        by passing a string containing newline characters '\\n'.

        addcomments('foo.*.bar', 'first comment', 'second\ncomment', ['third', 'comment'])
        """
        keys = self.gets(identifier)
        i = 0
        for key in keys:
            try : self.addcomment(key, comments[i])
            except IndexError: self.addcomment(key, comments[-1])
            finally: i += 1
