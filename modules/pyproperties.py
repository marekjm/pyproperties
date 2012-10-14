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
    *   pyproperites is capable of reading properties splitted into several lines, 
"""

import os, re


__major__ = 0
__minor__ = 1
__changes__ = 1
__version__ = "{}.{}.{}".format(__major__, __minor__, __changes__)


class Properties():
    """
    This class provides methods for working with properties files. 
    You should call it with a path pointing to the file you want to load. 
    """

    def __init__( self, path ):
        """
        First, defines self.path and extracts name of loaded properties file and stores it in self.name.
        Then runs these methods in following order:
            self.__load__( path )
            self.__extract__()
            self.__split__()
        """
        self.path = path.strip()
        self.name = os.path.splitext( os.path.split( self.path )[-1] )[0]
        self.__load__( path )
        self.__extract__()
        self.__split__()


    def __load__( self, path ):
        """
        This method loads properties file from given path to a self.source list. 
        It also strips it of any newline character and whitespace on both sides but leaves it otherwise unprocessed. 
        Path is saved to self.path
        """
        src = open( self.path, "rt" )
        lines = []
        try :
            lines = src.readlines()
        except UnicodeDecodeError as e : 
            print( "\a\v\tpyproperties: Error was encountered while reading properties from '{0}'".format(path) )
            raise
        finally :
            src.close()
        for i in range( len( lines ) ) : lines[i] = lines[i].rstrip()
        self.source = lines


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
            if self.__isvalidline__( self.source[i] ) : extracted.append( self.source[i] )

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
        properties = {}
        for i in range( len( self.properties ) ): properties[ self.__getkey__(self.properties[i]) ] = self.__getvalue__(self.properties[i])
        self.properties = properties


    def __getkey__( self, line, strip=True ):
        """
        Extracts key from given line and returns it. 
        If the line is comment or is an empty string returns empty string.
        """
        if strip : line = line.strip()
        if line == "" : key = ""
        elif line[0] == "#" or line.isspace() : key = ""
        elif line.find("=") == -1 : key = ""
        else : key = line[ : line.find("=") ]
        return key


    def __getvalue__( self, line ):
        """
        Extracts value from given line and returns it. 
        If the line is comment or is an empty string returns empty string.
        """
        line = line.strip()
        if line == "" : value = ""
        elif line[0] == "#" or line.isspace() : value = ""
        elif line.find("=") == -1 : value = ""
        else : value = line[ line.find("=")+1 : ]
        return value


    def reload( self ):
        """
        Reloads *.properties file. Missing values are added. Existing values are overwritten. 
        Values which are not found in file are deleted.
        """
        self.__load__( self.path )
        self.__split__()


    def refresh( self, overwrite = True ):
        """
        Refreshes *.properties file. Missing values are added.
        If 'overwrite' is set to True: existing values are overwritten. (merge() is used)
        Else: existing values are kept unchanged. (complete() is used)
            'overwrite' defaults to True.
        Values which are not found in file are not deleted.
        """
        new = Properties( self.path )
        if overwrite : self.merge( new )
        else : self.complete( new )


    def parseline( self, value ):
        """
        This method searches for every $(reference) string in given line and 
        replaces it with value of corrsponding property. 
        """
        while "$(" in value and ")" in value :
            a = value.find("$(")
            b = value[a:].find(")")
            name = value[ a+2 : a+b ]
            if a == -1 or b == -1 : break
            value = value.replace("$({0})".format(name), self.properties[ name ])
        return value


    def parse( self ):
        """
        This methode parses and returns parsed self.properties
        """
        parsed = {}
        for key, value in self.properties.items(): parsed[ key ] = self.get( key, True )
        return parsed


    def join(self, path, mode="c", prefix=" "):

        """
        Loads external properties and completes base. 
        If mode is set to "c": 
            comlete() method is used and properties are added with given prefix,
        if mode is set to "m": 
            merge() method is used (any prefix is discarded and new properties are not added).

        You can pass 'prefix' as empty string to add properties without prefix. 
        It defaluts to joined modules name.
        """
        path = path.strip()
        new = None
        try : 
            new = Properties( path )
            if prefix == " " : prefix = new.name
        except IOError : 
            print( "IOError: [Errno 2]: file not found '{0}': properties cannot be joined".format( path ) )
        finally :
            if new and mode == "c" : 
                self.complete( new, prefix )
                self.source.append( "" )
                self.source += new.source
            elif new and mode == "m" : self.merge( new )


    def complete( self, properties, prefix = "" ):
        """
        This methode completes base dictionary with properties of the given one. 
        If the base does not have some property it will be added. 
        Values of the existing properties are not overwritten. 
        """
        for key, value in properties.properties.items() :
            if prefix != "" : key = "{0}.{1}".format(prefix, key)
            if key not in self.properties : self.properties[ key ] = value


    def merge( self, properties ):
        """
        This methode merges given dictionary with the base one. 
        """
        for key, value in properties.properties.items() : 
            if key in self.properties : self.properties[ key ] = value


    def store(self, path = ""):
        """
        Writes properties to given 'path'.
        'path' defaults to self.path
        """
        stored = []
        if path == "" : path = self.path
        file = open( path, "w" )
        for i in range( len( self.source ) ) : 
            if self.source[i] == "" : 
                file.write( "{0}\n".format( self.source[i] ) )
            elif self.source[i][0] == "#" : 
                file.write( "{0}\n".format( self.source[i] ) )
            elif self.__getkey__( self.source[i] ) != "" and self.__getkey__( self.source[i] ) in self.properties : 
                stored.append( self.__getkey__( self.source[i] ) )
                file.write( "{0}={1}\n".format(self.__getkey__( self.source[i], False ), self.get( self.__getkey__( self.source[i] ) ) ) )
            else : 
                pass
        for key, value in self.properties.items() :
            if key not in stored : 
                file.write( "{0}={1}\n".format(key, value) )
                stored.append( key )
        file.close()


    def get(self, identifier, parsed = False):
        """
        Returns value of identifier. 
        If identifier is not found KeyError is raised.
        If parsed is set to True value will be parsed before returning.
        """
        if parsed : value = self.parseline( self.properties[ identifier ] )
        else : value = self.properties[ identifier ]
        return value


    def gets(self, identifier, parsed = False):
        """
        Returns dict of properties which names matched pattern given as identifier.
        If parsed is set to True values will be parsed before returning.
        """
        matched = {}
        identifier = identifier.replace("*", "[a-z0-9\.\*]*")
        identifier = re.compile(identifier)
        for key, value in self.properties.items():
            if re.match(identifier, key) and parsed : matched[ key ] = self.parseline( value )
            elif re.match(identifier, key) and not parsed : matched[ key ] = value
        return matched


    def set(self, identifier, value):
        """
        Sets key to value. 
        """
        self.properties[ identifier ] = value


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
        for key, value in kwargs.items() : _kwargs[ key.replace("_DOT_", ".") ] = value
        kwargs = _kwargs

        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
        for key, x in self.properties.items() :
            if re.match(identifier, key) : keys.append( key )

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
        for key in self.properties.keys() :
            if re.match( identifier, key ) : to_remove.append( key )
        for key in to_remove : self.properties.pop( key )


    def pop(self, identifier):
        """
        This methode removes specified property from interal dictionary and returns its value. 
        Removed property will be not saved using store().
        """
        return self.properties.pop( identifier )


    def pops(self, identifier):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        Removed properties will be not saved using store().
        """
        popped = {}
        identifier = re.compile( identifier.replace("*", "[a-z0-9\.\*]*") )
        for key, value in self.properties.items() :
            if re.match( identifier, key ) : popped[ key ] = value
        return popped


    def getnames(self):
        """
        Returns list of the property names. 
        """
        return sorted( list( self.properties.keys() ) )