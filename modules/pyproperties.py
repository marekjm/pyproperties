#!/usr/bin/python3

"""Working with *.properties files.

pyproperites aims to ease manipulation, interaction and use of *.properties files in Python 3.x programs
by providing methods like merge(), complete(), join(), parse() and store(). 

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
"""

import os
import re


__major__ = 0
__minor__ = 1
__changes__ = 3
__version__ = "{}.{}.{}".format(__major__, __minor__, __changes__)


class Properties():
    """
    This class provides methods for working with properties files. 
    You should call it with a path pointing to the file you want to load. 
    """

    def __init__( self, path = "", type_convert=False ):
        """
        If you give a path as an argument it will be loaded and processed as properties file. 
        If you call Properties() without an argument created object will be "blank" - in this case you will have to call 
        foo.read( path, type_convert ) to load some properties.
        You can pass type_convert as True to tell pyproperites that it should guess the type of the property 
        and convert it accordingly.

        This method (__init__) just calls read() with arguments passed to itself.
        """
        if path != "" and not path.isspace(): self.read( path, type_convert )


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
            source[i] = source[i].rstrip()
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
                proppaths.append( os.path.abspath( "{0}{1}{2}".format( root, os.path.sep, file ) ) )

        for i in range( len( proppaths ) ):
            propnames.append( proppaths[i].replace("{0}{1}".format(self.path, os.path.sep), "").replace( os.path.sep, "." ) )

        for i in range( len( proppaths ) ):
            value = open( proppaths[i] ).read()
            if value[-2:] == "\\n" : value = value[:-2]
            propvalues[ propnames[i] ] = value

        for key, value in propvalues.items():
            source.append()

        self.source = source
        self.srcorigin = srcorigin


    def __isvalidline__( self, line ):
        """
        Checks if the line contains valid property string. 
        It isn't empty string and its first character is not #.
        """
        result = line != "" and line[0] != "#"
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
            while line[-1] == "\\" :
                #  if line ends with backslash read next line and append it to
                i += 1
                line = line[:-1] + extracted[i]
            properties.append( line )
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
        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
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
        re_int = re.compile("^[0-9]+$")
        re_float = re.compile("^[0-9]*\.[0-9]+$")

        if re.match(re_int, prop): ptype = int
        elif re.match(re_float, prop): ptype = float
        else : ptype = str
        return ptype


    def __getkey__( self, line, strip=True ):
        """
        Extracts key from given line and returns it. 
        If the line is comment or is an empty string returns empty string.
        """
        if strip : line = line.strip()
        if line == "" : key = ""
        elif line[0] == "#" or line.isspace(): key = ""
        elif line.find("=") == -1 : key = ""
        else : key = line[: line.find("=")]
        return key


    def __getvalue__( self, line ):
        """
        Extracts value from given line and returns it. 
        If the line is comment or is an empty string returns empty string.
        """
        line = line.strip()
        if line == "" : value = ""
        elif line[0] == "#" or line.isspace(): value = ""
        elif line.find("=") == -1 : value = ""
        else : value = line[line.find("=")+1 :]
        return value


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
        else : self.__loadd__( self.path )
        self.__extract__()
        self.__split__()
        if cast : self.__tcasts__( "*" )


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


    def parse( self, cast=False ):
        """
        This methode parses and returns parsed self.properties
        """
        parsed = {}
        for key, value in self.properties.items(): parsed[key] = self.get( key, True, cast )
        return parsed


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
                self.source.append( "" )
                self.source += new.source
            else : pass


    def melt(self, properties ):
        """
        Completes and merges 'properties' with the base. 
        Source of melted properties is appended to base source.
        """
        self.complete( properties )
        self.merge( properties )
        self.source.append("")
        self.source += properties.source


    def complete( self, props, prefix="" ):
        """
        This methode completes base dictionary with properties of the given one. 
        If the base does not have some property it will be added. 
        Values of the existing properties will be not overwritten. 
        """
        for key, value in props.properties.items():
            if prefix != "" : key = "{0}.{1}".format(prefix, key)
            if key not in self.properties : self.properties[key] = value


    def merge( self, properties, with_prefix="" ):
        """
        This methode base dictionary with the given one. 
        If the base does not have some property it will not be added. 
        Values of the existing properties will be overwritten. 

        If prefix is specified only properties which are preceded with 
        this key will have their value changed.
        """
        for key, value in properties.properties.items(): 
            if with_prefix : key = "{0}.{1}".format( with_prefix, key )
            if key in self.properties : self.properties[key] = value


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


    def store(self, path = ""):
        """
        Writes properties to given 'path'.
        'path' defaults to self.path
        """
        stored = []
        if path == "" : path = self.path

        file = open( path, "w" )
        for i in range( len( self.source ) ): 
            if self.source[i] == "" : 
                # saves empty line
                file.write( "{0}\n".format( self.source[i] ) )
            elif self.source[i][0] == "#" : 
                # saves commented line
                file.write( "{0}\n".format( self.source[i] ) )
            elif self.__getkey__( self.source[i] ) != "" and self.__getkey__( self.source[i] ) in self.propsorigin and self.__getkey__( self.source[i] ) not in stored : 
                # checks if current line has a key (is a valid property line)
                # and is in defined in self.propsorigin
                stored.append( self.__getkey__( self.source[i] ) )
                file.write( "{0}={1}\n".format(self.__getkey__( self.source[i], False ), self.propsorigin[self.__getkey__( self.source[i] )] ) )
            else : 
                pass

        for key, value in self.propsorigin.items():
            if key not in stored : 
                file.write( "{0}={1}\n".format(key, value) )
                stored.append( key )

        file.close()


    def get(self, identifier, parsed=False, cast=False):
        """
        Returns value of identifier. 
        If identifier is not found KeyError is raised.
        If parsed is set to True value will be parsed before returning.
        """
        if parsed : value = self.parseline( self.properties[identifier] )
        else : value = self.properties[identifier]
        if cast : value = self.__typeguess__( value )(value)
        return value


    def gets(self, identifier, parsed=False, cast=False):
        """
        Returns dict of properties which names matched pattern given as identifier.
        If parsed is set to True values will be parsed before returning.
        """
        matched = {}
        identifier = identifier.replace("*", "[a-z0-9\.\*]*")
        identifier = re.compile(identifier)
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


    def sets(self, identifier, value, *args, **kwargs):
        """
        Sets every property which name matched pattern given as identifier to value. 
        You can pass more than one value. If more keys are found than values passed 
        last value is passed to every key above number of values. 
        After completing sort() method is used on keys list so the first value goes to first key. 
        If the key is in kwargs its value if taken from the dict and the value counter is not increased. 
        If you want to keyword a property which name contains a dot character "." you should use __DOT__ 
        as a substitute for this character - 'foo__DOT__bar' will be converted to 'foo.bar'.
        """
        keys = []
        values = [value]
        values.extend(args)
        _kwargs = {}
        for key, value in kwargs.items(): _kwargs[key.replace("_DOT_", ".")] = value
        kwargs = _kwargs

        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
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


    def remove(self, identifier):
        """
        This methode removes specified property from interal dictionary. 
        Removed property will be not saved using store().
        """
        self.properties.pop( identifier )


    def removes(self, identifier):
        """
        This methode removes properties matching given pattern from interal dictionary. 
        Removed properties will be not saved using store().
        """
        to_remove = []
        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
        for key in self.properties.keys():
            if re.match( identifier, key ): to_remove.append( key )
        for key in to_remove : self.properties.pop( key )


    def pop(self, identifier, cast=False):
        """
        This methode removes specified property from interal dictionary and returns its value. 
        Removed property will be not saved using store().
        """
        prop = self.properties.pop( identifier )
        if cast : prop = self.__typeguess__( prop )( prop )
        return prop


    def pops(self, identifier, cast=False):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        Removed properties will be not saved using store().
        """
        popped = {}
        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
        for key, value in self.properties.items():
            if re.match( identifier, key ): 
                popped[key] = value
        for key in popped.keys(): self.properties.pop( key )
        if cast : 
            for key, value in popped.items():
                popped[key] = self.__typeguess__( value )( value )
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
        will not form a group even if gets('person.*') will return 
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
