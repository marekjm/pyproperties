#!/usr/bin/env python3

"""Working with *.properties files."""

import os
import re
import warnings
import json

__version__ = "0.2.6"
__vertuple__ = tuple( int(n) for n in __version__.split(".") )

wildcart_re = "[a-zA-Z0-9_.-]+"
guess_int_re = "^-?[0-9]+$"
guess_bin_re = "^-?0b[0-1]+$"
guess_oct_re = "^-?0o[0-7]+$"
guess_hex_re = "^-?0x[0-9a-fA-F]+$"
guess_float_re = "^-?[0-9]*\.[0-9]+(e[+-]{0,1})?[0-9]+$"

class ReadError(IOError): pass
class StoreError(IOError): pass
class UnsavedChangesError(BaseException): pass
class IncludeError(Exception): pass
class IncludeWarning(UserWarning): pass
class MultipleDeclarationWarning(UserWarning): pass

def isbin(s):
    """
    Returns True if given string contains valid binary number.
    """
    result = False
    if re.match(re.compile(guess_bin_re), s): result = True
    return result

def isoct(s):
    """
    Returns True if given string contains valid octal number.
    """
    result = False
    if re.match(re.compile(guess_oct_re), s): result = True
    return result

def ishex(s):
    """
    Returns True if given string contains valid hexadecimal number.
    """
    result = False
    if re.match(re.compile(guess_hex_re), s): result = True
    return result

def linehaskey(line, strict=True):
    """
    Checks if the line contains a key. 
    """
    result = False
    if ":" in line[:line.find("=")]: key = line.split(":", 1)[0].strip()
    elif "=" in line[:line.find(":")]: key = line.split("=", 1)[0].strip()
    else: key = None

    if key != None and key[0] not in ["#", "!"]:
        if strict and " " in key:
            warnings.warn("space found in key '{0}'".format(key))
            result = False
        elif not strict and " " in key:
            warnings.warn("space found in key: '{0}'".format(key))
            result = True
        else: 
            result = True
    return result

def iscomment(line):
    """
    Checks if given line is a comment.
    """
    line = line.strip()
    return line != "" and line[0] in ["#", "!"]

def getlinekey(line, strict=True):
    """
    Extracts key from given line and returns it. 
    If the line does not contain a key returns None. 
    
    If in strict mode (default) and find a whitespace in key it will 
    complain with a warning and return None. 
    If in non-strict mode (strict passed as `False`) it will only complain and 
    do nothing else.
    """
    if not linehaskey(line, strict): key = None
    elif ":" in line[:line.find("=")]: key = line.split(":", 1)[0].strip()
    else: key = line.split("=", 1)[0].strip()
    return key

def getlinevalue(line, strict=True):
    """
    Extracts value from given line and returns it. 
    If the line does not have a value returns None (remeber: empty string is returned when line has it as a value). 
    It is done this way to distinguish properties with empty value 
    from lines which do not carry a property.
    """
    if not linehaskey(line, strict): value = None
    elif ":" in line[:line.find("=")]: value = line.split(":", 1)[1].lstrip()
    else: value = line.split("=", 1)[1].lstrip()

    if line != "" and line[-1] == "\n": line = line[:-1]   # striping newline while preserving newlines in value and trailing whitespace
    return value

def expandidentifier(identifier):
    """
    Applies needed changes to identifier pattern (regular expression). 
    """
    return "^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re))


class Reader():
    """
    This class utilizes methods for reading properties files.
    """
    
    def __init__(self, path, includes=True, cast=False, strict=True):
        self._path = os.path.abspath(path)
        self._includes, self._cast, self._strict = (includes, cast, strict)
        self._source, self._hidden, self._included, self._comments, self._properties = ([], [], [], {}, [])

    def loadf(self):
        """
        Loads file to which `_path` points, and 
        concatenates properties split into several lines. 
        Lines are loaded with trailing newlines characters and preceding whitespace stripped. 
        Comments which end with backslash (`\\`) are left untouched but a warning is raised.
        """
        try:
            path = open(self._path)
            file = path.readlines()
            path.close()
        except (IOError, FileNotFoundError) as e:
            raise ReadError(e)
        source = []
        i = 0
        while i < len(file):
            line = file[i].lstrip()
            while line != "" and line[-1] == "\n": line = line[:-1]
            if line != "" and line[-1] == "\\" and line[0] in ["#", "!"]: warnings.warn("comment ending with backslash: {0}:{1}".format(self._path, i+1))
            while line != "" and line[-1] == "\\" and line[0] not in ["#", "!"]:
                i += 1
                line = line[:-1]
                while file[i] != "" and file[i][-1] == "\n": file[i] = file[i][:-1]
                line += file[i]
            i += 1
            source.append(line)
        self._source = source

    def _include(self, line_number, path, prefix="", hidden=False):
        """
        This method is only run when a property file is being read. 
        It will dump another file in place specified by `__include__` directive.
        """
        if not os.path.isabs(path): tpath = os.path.join(os.path.split(self._path)[0], path)
        else: tpath = path
        if tpath.strip() == "": raise IncludeError("__include__ must point to a file: cannot accept empty path")
        if not os.path.isfile(tpath): raise IncludeError("__include__ file not found: {0}".format(tpath))
        
        fpath = open(tpath)
        file = fpath.readlines()
        fpath.close()

        if (path, prefix, hidden) not in self._included: self._included.append( (path, prefix, hidden) )
        
        for i, line in enumerate(file):
            if linehaskey(line, strict=self._strict) and prefix: line = "{0}.{1}".format(prefix, line.lstrip())
            elif self._islinehiddenprop(line) and prefix: line = "#{0}.{1}".format(prefix, line[1:])
            if linehaskey(line, strict=self._strict) and hidden: line = "#{0}".format(line.lstrip())
            if line[-1] == "\n": line = line[:-1]
            file[i] = line

        self._source = self._source[:line_number] + file + self._source[line_number+1:]

    def makeincludes(self):
        """
        This method runs during load and is kind of preprocessor. It will replace 
        every line which key begins with `__include__` with lines of file 
        it will try to read from the path specified in the value of the mentioned line. 
        
        Although it may be temptating - using `for` loop in this method is not good. 
        `for` will not "keep track" of changes in file lenghts and you will end up on overwriting previous __include__'s contents. 
        Indexes generated by `for` will not take into account the fact that source may have been already expanded. 
        Adding this functionality will result in unnecessary bloat so `while` stays.
        """
        i = 0
        while i < len(self._source):
            key = getlinekey(self._source[i])
            value = getlinevalue(self._source[i])
            if key == "__include__": self._include(i, value)
            elif key == "__include__.hidden": self._include(i, value, hidden=True)
            elif key != None and key[:15] == "__include__.as.": self._include(i, value, prefix=key[15:])
            elif key != None and key[:22] == "__include__.hidden.as.": self._include(i, value, prefix=key[22:], hidden=True)
            i += 1

    def _islinehiddenprop(self, line):
        """
        Defines if commented line is commented property or casual comment.
        Used to distinguish comments from commented properties during load.
        """
        # a little hack to not generate too many warnings when just checking if a line is hidden property
        if iscomment(line) and line[1] != " ": result = linehaskey(line[1:], strict=self._strict)
        else: result = False
        return result

    def uncoverhidden(self):
        """
        Unvoers hidden properties -- makes them available for `_extractprops()`.
        """
        source = []
        hidden = []
        for line in self._source:
            if self._islinehiddenprop(line):
                line = line[1:]
                hidden.append( getlinekey(line) )
            source.append(line)
        self._hidden = hidden
        self._source = source
    
    def extractprops(self):
        """
        Extracts lines containing valid properties from `_source` to `_properties`.
        """
        properties = []
        for line in self._source:
            if linehaskey(line=line, strict=self._strict): properties.append(line)
        self._properties = properties

    def extractcomments(self):
        """
        Extracts comments from `_source` and attaches them to properties.
        """
        comments = {}
        i = 0
        while i < len(self._source):
            line = self._source[i]
            if linehaskey(line=line, strict=self._strict):
                comment, n = ([], i-1)
                while n >= 0 and iscomment(self._source[n]):
                    comment.append( self._source[n][1:].strip() )
                    n -= 1
                if n != i-1:
                    comment.reverse()
                    comments[ getlinekey(line) ] = "\n".join(comment)
                    self._source = self._source[:n+1] + self._source[i:]
            i += 1
        self._comments = comments

    def splitprops(self):
        """
        This method converts self.properties from list containing extracted lines to a dictionary.
        """
        properties = {}
        for line in self._properties:
            key = getlinekey(line)
            value = getlinevalue(line)
            properties[key] = value
        self._properties = properties
    
    def castprops(self):
        """
        This method tries to cast values of loaded properties.
        """
        for key, value in self._properties.items():
            self._properties[key] = convert(value)
    
    def read(self):
        self.loadf()
        if self._includes: self.makeincludes()
        self.uncoverhidden()
        self.extractcomments()
        self.extractprops()
        self.splitprops()
        if self._cast: self.castprops()
    
    def keys(self):
        """
        Returns list of keys in read file.
        """
        return list(self._properties.keys())


class Exporter:
    """
    This class conatins engines for exporting properties to different formats.
    """
    class JSON():
        """
        This class provides functionality for storing properties in JSON format. 
        
        **IMPORTANT NOTE**
        During conversion all information about included files, comments and 
        properties' status (hidden/not-hidden) is lost.
        Only data is exported.
        """
        def __init__(self, properties):
            self._properties, self._path = (properties, "{0}.json".format(os.path.splitext(properties.path)[0]))
            if self._path == ".json": self._path = ""
            
            self._origin_properties = self._properties.origin_properties
            self._origin_propcomments = self._properties.origin_propcomments
            self._origin_hidden = self._properties.origin_hidden
            self._json, self.json = ({}, "")

        def encode(self, pretty=False):
            """
            **JSON Writer version**
            This method encode generated Python dict to JSON.
            """
            if pretty:
                self.json = json.dumps(self._json, sort_keys=True, indent=4)
                self.json = [line.rstrip() for line in self.json.splitlines()]
            else:
                self.json = json.dumps(self._json)
            
        def storeprop(self, key):
            """
            **JSON Writer version**
            This method stores single property and takes responsibility of storing it's comment and status. 
            This method looks at the `stored` list and checks if the given key has already 
            been stored to prevent storing it two times.
            It will also check if the key is in `origin_properties` dict to ensure that unsaved properties 
            would not get stored.
            """
            self._json[key] = self._properties.get(key)
            
        def storegroups(self):
            """
            Generates lines for groups not found in source.
            """
            for identifier in self._properties.getgroups():
                keys = [ key for key in dict(self._properties.gets(identifier)) ]
                for key in sorted(keys): self.storeprop(key)

        def storesingles(self):
            """
            Generates lines for single properties not found in source.
            """
            for key in sorted(self._origin_properties.keys()): self.storeprop(key)

        def dump(self, path):
            """
            Dumps generated lines to file given in path and clears 
            variables defined by store() and its subemthods. 
            """
            file = open(path, "w")
            if type(self.json) == list: [file.write("{0}\n".format(line)) for line in self.json]
            else: file.write(self.json)
            file.close()

        def store(self, path="", force=False, no_dump=False, pretty=False):
            """
            **JSON Writer version**
            Writes properties to given 'path'.
            'path' defaults to path set if given properties, but extension is set to '.json'.

            If store will encounter some unsaved changes it will
            raise UnsavedChangesError.
            You can explicitly silence it by passing force as True.

            If 'no_dump' is passed as True lines will be generated 
            but not written to file.
            
            **WARNING!**
            During conversion to JSON information about includes are lost.
            """
            if self._properties.unsaved and not force: raise UnsavedChangesError("trying to store with unsaved changes")
            if path == "": path = self._path
            if path == "" or path.isspace(): raise StoreError("no path specified")
            
            self.storesingles()
            self.storegroups()
            self.encode(pretty=pretty)
            if not no_dump: self.dump(path)


class Writer():
    """
    This class utilizes methods for storing properties. 
    When creating new instance of Writer pass a Properties() object to it.
    
    This class is written for storing edited properties. 
    It can use original source as a template for new file but 
    can also generate new file entirely on its own. 
    Styling features of `Writer.Properties` can be handy at times. 
    When you have to deal with badly formed and hard to read file `Writer` can act as a *cleaner*. 
    It will parse properties and write new file which will have properties grouped and styled in 
    human-readable way.
    """
    def __init__(self, properties):
        self.properties = properties
        self.stored, self.includes_stored, self.lines = ([], self.properties.includes_stored, [])
        self.origin_properties, self.origin_includes = (self.properties.origin_properties, self.properties.origin_includes)
        self.origin_propcomments, self.origin_hidden = (self.properties.origin_propcomments, self.properties.origin_hidden)
        self.source = self.properties.origin_source
    
    def storeprop(self, key):
        """
        This method stores single property and takes responsibility of storing it's comment and 
        possibly hiding the property itself. 
        This method looks at the `stored` list and checks if the given key has already 
        been stored to prevent storing it two times.
        It will also check if the key is in `origin_properties` dict to ensure that unsaved properties 
        would not get stored.
        """
        if key not in self.stored and key in self.origin_properties:
            if key in self.origin_propcomments: self.storecomment(key)
            if key not in self.origin_hidden: self.lines.append("{0}={1}".format(key, self.origin_properties[key]))
            else: self.lines.append("#{0}={1}".format(key, self.origin_properties[key]))
            self.stored.append(key) 

    def storeincludes(self):
        """
        This method stores __include__ directives added via the library. 
        Each directive is separated by a blank line.
        """
        if self.lines != [] and self.lines[-1] != "": self.lines.append("")
        for path, prefix, hidden in self.origin_includes:
            if (path, prefix, hidden) not in self.includes_stored:
                if prefix and hidden: line = "__include__.hidden.as.{0}={1}".format(prefix, path)
                elif prefix and not hidden: line = "__include__.as.{0}={1}".format(prefix, path)
                elif not prefix and hidden: line = "__include__.hidden={0}".format(path)
                else: line = "__include__={0}".format(path)
                self.lines.append(line)
                self.lines.append("")
                self.includes_stored.append( (path, prefix, hidden) )
    
    def storesrc(self):
        """
        Prepares data which came with source for storing.
        """
        for i in range(len(self.source)):
            if self.source[i] == "" or self.source[i].isspace(): self.lines.append("")
            elif self.source[i][0] == "#": self.lines.append("{0}".format(self.source[i]))
            elif getlinekey(self.source[i], strict=self.properties.strict) != "": self.storeprop(getlinekey(self.source[i], strict=self.properties.strict))
    
    def storegroups(self):
        """
        Generates lines for groups not found in source.
        """
        if self.lines != [] and self.lines[-1] != "": self.lines.append("")
        for identifier in self.properties.getgroups():
            previous_len = len(self.lines)
            keys = [ key for key in self.properties.gets(identifier) ]
            for key in sorted(keys): self.storeprop(key)
            if len(self.lines) > previous_len: self.lines.append("")

    def storesingles(self):
        """
        Generates lines for single properties not found in source.
        """
        for key in sorted(self.origin_properties.keys()): self.storeprop(key)

    def storecomment(self, key):
        """
        Appends comment of a property of given key to self.lines
        """
        [ self.lines.append("#   {0}".format(line)) for line in self.origin_propcomments[key].split("\n") ]

    def dump(self, path):
        """
        Dumps generated lines to file given in path and clears 
        variables defined by store() and its subemthods. 
        """
        file = open(path, "w")
        for line in self.lines: file.write("{0}\n".format(line))
        file.close()
        self.lines, self.stored = ([], [])

    def store(self, path="", force=False, no_dump=False, drop_source=False):
        """
        Writes properties to given 'path'.
        'path' defaults to path set if given properties.

        If store will encounter some unsaved changes it will
        raise UnsavedChangesError.
        You can explicitly silence it by passing force as True.

        If 'no_dump' is passed as True lines will be generated 
        but not written to file.
        """
        if self.properties.unsaved and not force: raise UnsavedChangesError("trying to store with unsaved changes")
        if path == "": path = self.properties.path    # this line defaults the value
        if path == "" or path.isspace(): raise StoreError("no path specified")
        if path and not self.properties.path: self.properties.path = path
            
        if not drop_source: self.storesrc()
        self.storegroups()
        self.storesingles()
        self.storeincludes()
        try:
            while self.lines[-1] == "": self.lines = self.lines[:-1]
        except IndexError: pass
        finally:
            if not no_dump: self.dump(path)


class Engine:
    """
    Class containing engine-classes from which main `Properties` class
    inherits. Used for more modularization and separation.
    
    Functions found in `Engine` can be used freely if needed.

    WARNING!
    Classes in `Engine` are intended to be used only by main `Properties` class via 
    inheritance. On its own it can cause errors because it is sometime missing methods
    present only in `Properties` class.
    """
 
    def notavailable(properties, key):
        """
        Raises KeyError which will tell user that the property is not available eg. 
        is not in currently used set of properties or is hidden.
        """
        if key in properties.hidden: message = "'{0}' is not available in {1}: hidden property".format(key, properties)
        else: message = "'{0}' is not available in {1}".format(key, properties) 
        raise KeyError(message)

    def convert(value, strict=True):
        """
        Returns value with it's type converted. 
        Can convert from str to: int, float, True/False and None.
        """
        value = str(value)
        if value == "None": value = None
        elif value == "True": value = True
        elif value == "False": value = False
        elif ishex(value): value = int(value, 16)
        elif isoct(value): value = int(value, 8)
        elif isbin(value): value = int(value, 2)
        elif re.match(re.compile(guess_int_re), value): value = int(value)
        elif re.match(re.compile(guess_float_re), value): value = float(value)
        return value


    class Includer():
        """
        Class utilizing mechanisms used by `__include__` directive.
        """
        def __init__(self):
            self.includes, self.origin_includes = ([], [])
            self.includes_stored = ([])
            self.unsaved = True
         
        def _rmkeysfrom(self, path, prefix=""):
            """
            Removes all properties present in file to which given path is pointing.
            """
            path = os.path.abspath(os.path.join(os.path.split(self.path)[0], path))
            reader = Reader(path=path)
            reader.read()
            for key in reader.keys():
                if prefix: key = "{0}.{1}".format(prefix, key)
                self.remove(key)
    
        def addinclude(self, path, prefix="", hidden=False):
            """
            This method places __include__ directive in the properties.
            """
            if not os.path.isfile(path): warnings.warn("file for __include__ not found: '{0}'".format(path), IncludeWarning)
            if path.strip() == "": raise IncludeError("__include__ must point to a file: cannot accept empty path".format(path))
            
            if (path, prefix, hidden) not in self.includes: self.includes.append( (path, prefix, hidden) )

        def rminclude(self, path, prefix="", hidden=False):
            """
            Removes include directive from a list of directives. 
            """
            for _path, _prefix, _hidden in self.includes:
                if path == _path and prefix == _prefix and hidden == _hidden: 
                    self.includes.remove( (path, prefix, hidden) )
                    break

        def purgeinclude(self, path, prefix="", hidden=False):
            """
            Removes include directive from a list of directives and all properties corresponding to it.
            """
            for i, (ipath, iprefix, ihidden) in enumerate(self.includes):
                if path == ipath and prefix == iprefix and hidden == ihidden:
                    self.rminclude(path, prefix, hidden)
                    self._rmkeysfrom(path=path, prefix=prefix)
                    break
            if not self.unsaved: warnings.warn("purge failed: no such include-tuple found: ('{0}', '{1}', {2})".format(path, prefix, hidden), IncludeWarning)

        def stripinclude(self, path, prefix="", hidden=False):
            """
            This method removes all properties included from file of given path but 
            leaves include tuple (it will be stored).
            """
            self.purgeinclude(path, prefix, hidden)
            self.addinclude(path, prefix, hidden)

        def listincludes(self):
            """
            Returns list of tuples containg information about `includes` of this properties.
            """
            return self.includes

    class Hider():
        """
        Class which implements mechanisms used for hiding properties.
        """
        def __init__(self):
            self.hidden, self.origin_hidden = ([], [])
            self.properties = []

        def hide(self, key):
            """
            When property is hidden it is no longer available for modifing. 
            KeyError is raised if key is not available (not found or is hidden).
            """
            if key not in self.properties or key in self.hidden: Engine.notavailable(self, key)
            if key not in self.hidden: self.hidden.append(key)
            self.unsaved = True
            
        def hides(self, identifier):
            """
            Hides every property which key will match given identifier. 
            """
            identifier = expandidentifier(identifier)
            for key in self.keys():
                if re.match(identifier, key): self.hide(key)

        def unhide(self, key):
            """
            Remove property from `hidden` list to make it available for modifing. 
            Does not raise any errors when key is not found.
            """
            if key in self.hidden: self.hidden.remove(key)
            self.unsaved = True

        def unhides(self, identifier):
            """
            Unhides every property which key will match given identifier.
            """
            identifier = expandidentifier(identifier)
            to_unhide = []
            for i in range(len(self.hidden)):
                if re.match(identifier, self.hidden[i]): to_unhide.append(self.hidden[i])
            for key in to_unhide: self.unhide(key)

    class Commenter():
        def __init__(self):
            self.propcomment, self.origin_propcomments = ({}, {})

        def comment(self, key, comment):
            """
            Attaches comment to property. 
            Comment can be passed as a string.

                foo.comment("foo", "first\\npart")

            Multiline comments are supported by passing a string containing newline characters '\\n'.

            KeyError is raised if key is not available (not found or is hidden).
            """
            if key not in self.properties or key in self.hidden: Engine.notavailable(self, key)

            self.propcomments[key] = comment
            self.unsaved = True

        def comments(self, identifier, *comments):
            """
            Attaches comment to properties which will match the identifier. 
            Comment can be passed as a string. 
            Multiline comments are supported by passing a string containing newline characters '\\n'.

            comments('foo.*.bar', 'first comment', 'multi\\nline')
            """
            keys = self.gets(identifier)
            i = 0
            for key in keys:
                try: self.comment(key, comments[i])
                except IndexError: self.comment(key, comments[-1])
                finally: i += 1

        def rmcomment(self, key):
            """
            Removes comment of property of given key. 
            Does not raise KeyError when property is not found.
            """
            if key in self.propcomments: self.propcomments.pop(key)
            self.unsaved = True

        def getcomment(self, key, lines=False):
            """
            usage: getcomment(str key, bool lines=False) -> str
            
            Returns comment of given key. 
            Returns empty string if the property has no comment. 
            Returns empty list if the property has no comment and `lines` was passed as True. 
            KeyError is raised if key is not available (not found or is hidden).
            """
            if key not in self.properties or key in self.hidden: self._notavailable(key)
            
            if key in self.propcomments: comment = self.propcomments[key]
            else: comment = ""
            if lines and comment != "": comment = comment.split("\n")
            elif lines and comment == "": comment = []
            return comment

class Properties(Engine.Commenter, Engine.Hider, Engine.Includer):
    """
    This class provides methods for working with properties files. 
    """

    def __init__(self, path="", cast=False, no_read=False, no_includes=False, strict=True):
        """
        If you give a path as an argument it will be loaded and processed as properties file. 
        If you call Properties() without an argument created object will be "blank" - in this case you will have to call 
        foo.read(path) to load some properties or you can use the blank properties to create completly new set of properties.
        You can pass cast as True to tell pyproperties that it should guess the type of the property 
        and convert it accordingly.

        To create a blank instance with path specified you can run:
            pyproperties.Properties("/home/user/some/path/foo.properties", no_read=True)
        """
        if type(path) == Reader:
            self.blank(path=path._path, strict=strict)
            self._feed(path)
        elif path.strip() and not no_read: 
            self.read(path, cast, no_includes, strict)
        else: 
            self.blank(path, strict)
        self.save()

    def _parseline(self, value):
        """
        This method searches for every $(reference) string in given line and 
        replaces it with value of corresponding property. 
        """
        if type(value) == str:
            while "$(" in value and ")" in value:
                a = value.find("$(")
                b = value[a:].find(")")
                name = value[a+2: a+b]
                if a == -1 or b == -1: break
                value = value.replace("$({0})".format(name), str(self.get(name)))
        return value

    def _appendsrc(self, props, prefix=""):
        """
        This methods appends source of given properties to the base. 
        If `source` already contains some lines a blank line is added before actual 
        source to avoid making comments accidentaly joined.
        """
        lines = []
        for line in props.origin_source:
            if line == "": lines.append(line)
            elif line[0] in ["#", "!"] or line.isspace(): lines.append(line)
            elif linehaskey(line, strict=self.strict) and not prefix: lines.append(line)
            elif linehaskey(line, strict=self.strict) and prefix: lines.append("{0}.{1}".format(prefix, line))
            else: pass
        if self.source: self.source.append("")
        self.source.extend(lines)
        
    def _feed(self, reader):
        """
        Reads passed `Reader` object and tries to extract properties data out of it. 
        Designed to use with native `Reader` objects but will accept any properly crafted object.
        """
        self.properties = reader._properties
        self.hidden = reader._hidden
        self.propcomments = reader._comments
        self.includes = reader._included
        self.source = reader._source

    def setstrict(self, strict):
        """
        Sets parser mode to strict (True) or non-strict (False).
        """
        self.strict = bool(strict)

    def blank(self, path="", strict=True):
        """
        Creates blank properties object. 
        Can be used to erase contents of your `pyproperties` object.
        """
        try: 
            if self.path: path = self.path
        except AttributeError: path = os.path.expanduser(path.strip())
        finally: self.path = path
        
        self.name = os.path.splitext(os.path.split(self.path)[-1])[0]
        self.strict = strict
        self.source, self.origin_source = ([], [])
        self.properties, self.origin_properties = ({}, {})
        self.propcomments, self.origin_propcomments = ({}, {})
        self.hidden, self.origin_hidden = ([], [])
        self.includes, self.origin_includes = ([], [])
        self.includes_stored = ([])
        self.unsaved = False
    
    def read(self, path="", cast=False, no_includes=False, strict=True):
        """
        You can pass `cast` as True to tell pyproperties that it should guess the type of the property 
        and convert it accordingly.
        """
        self.blank(path=path, strict=strict)
        reader = Reader(path=self.path, includes=not no_includes, cast=cast, strict=strict)
        reader.read()
        self._feed(reader)
        
    def reload(self):
        """
        Reloads properties from `self.path`. Parser mode for reloading will be taken from `self.strict`.
        """
        self.read(self.path, strict=self.strict)
        self.unsaved = True

    def refresh(self, overwrite=True):
        """
        Refreshes from file. Missing values are added.
        If `overwrite` is set to True existing values are overwritten - `update()` is used.
        Values which are not found in file are not deleted.
        """
        new = Properties(self.path)
        self.complete(new, "")
        if overwrite: self.update(new)
        self.unsaved = True

    def copy(self):
        """
        Returns exact copy of a pyproperties.Properties() object.
        """
        copy = Properties(self.path, no_read=True)
        copy.merge(self)
        copy.save()
        return copy

    def join(self, path, prefix=" "):
        """
        Loads external properties and completes base. 
        You can pass `prefix` as empty string to add properties without prefix. 
        Prefix defaluts to the name of joined file. 
        Source of joined properties is appended to base source.
        """
        props = Properties(path, strict=self.strict)
        if prefix == " ": prefix = props.name
        self.complete(props, prefix)
        self._appendsrc(props, prefix)
        self.unsaved = True

    def complete(self, props, prefix=""):
        """
        This method completes base dictionary with properties of the given one. 
        If a property does not exist in base it will be added. 
        If a property exist in base it's value, comments and status (hidden/not-hidden) 
        will not be overwritten. 

        If a prefix is specified - it will be added before each key.

        Source of completed properties is not appended to the base.
        Comment information is appended to the base.

        Properties for completion are taken from `origins` of given props so 
        before you complete it's better to call `save()`.
        During completion properties are not copied directly to `origins` of the base 
        properties.
        """
        completed = []
        for key, value in props.origin_properties.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.properties:
                self.set(key, value)
                if key not in completed: completed.append(key)
        for key, value in props.origin_propcomments.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.propcomments and key in completed: self.comment(key, value)
        for key in props.origin_hidden:
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.hidden and key in completed: self.hide(key)
        self.unsaved = True

    def update(self, props, prefix=""):
        """
        This method updates base properties with the given one. 
        If a property does not exist in base it will not be added. 
        If a property exist in base it's value will be overwritten. 

        If prefix is specified only properties which are preceded with 
        this key will have their value changed.

        Source of merged properties is not appended to the base.
        Comment information is appended to the base.

        Properties for updating are taken from `origins` of given props so 
        before you merge it's better to call `save()`.
        During merging properties are not copied directly to `origins` of the base 
        properties.
        """
        updated = []
        for key, value in props.origin_properties.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in self.properties: 
                self.set(key, value)
                updated.append(key)
        for key, value in props.origin_propcomments.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in updated: self.comment(key, value)
        for key in props.origin_hidden:
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in updated: self.hide(key)
        self.unsaved = True

    def merge(self, properties):
        """
        Completes and merges properties with the base. 
        Source of merged properties is appended to base. 
        
        It's not possible to add prefix when merging.
        """
        self.complete(properties)
        self.update(properties)
        self._appendsrc(properties)
        self.unsaved = True

    def parse(self, cast=False):
        """
        This method parses and returns parsed properties.
        """
        parsed = Properties()
        parsed.merge(self)
        for key in parsed.keys(): parsed.set(key, parsed.get(key, parse=True))
        parsed.save()
        if cast: 
            for key in parsed.keys(hidden=True): parsed.set(key, parsed.get(key, cast=True))
        return parsed

    def save(self):
        """
        Saves changes made in object's variables.
        """
        saved = {}
        for key, value in self.properties.items(): saved[key] = value
        self.origin_properties = saved
        saved = {}
        for key, value in self.propcomments.items(): saved[key] = value
        self.origin_propcomments = saved
        self.origin_source = [ line for line in self.source ]
        self.origin_hidden = [ key for key in self.hidden ]
        self.origin_includes = [ key for key in self.includes ]
        self.unsaved = False

    def revert(self):
        """
        Drops changes made in properties object by reverting it's variables
        to the state in which they were during last save().
        """
        reverted = {}
        for key, value in self.origin_properties.items(): reverted[key] = value
        self.properties = reverted
        reverted = {}
        for key, value in self.origin_propcomments.items(): reverted[key] = value
        self.propcomments = reverted
        self.source = [ line for line in self.origin_source ]
        self.hidden = [ key for key in self.origin_hidden ]
        self.includes = [ key for key in self.origin_includes ]
        self.unsaved = False

    def store(self, path="", force=False, no_dump=False, drop_source=False):
        """
        Writes properties to given 'path'.
        'path' defaults to self.path

        If store will encounter some unsaved changes it will
        raise UnsavedChangesError.
        You can explicitly silence it by passing force as True.

        If 'no_dump' is passed as True lines will be generated 
        but not written to file.
        """
        writer = Writer(self)
        writer.store(path, force, no_dump, drop_source)
        
    def get(self, key, parse=False, cast=False):
        """
        Returns value of given key. 
        If parsed is set to True value will be parsed before returning.
        KeyError is raised if key is not available (not found or is hidden).
        """
        if key not in self.properties or key in self.hidden: Engine.notavailable(self, key)
        
        if parse: value = self._parseline(self.properties[key])
        else: value = self.properties[key]
        if cast and type(value) == str: value = Engine.convert(value)
        return value

    def gets(self, identifier, parse=False, cast=False, no_expand=False):
        """
        Returns list of tuples containig (key, value) of properties which names matched pattern given as identifier.
        If `parse` is set to True values will be parsed before returning.
        If `cast` is set to True values will be casted before returning.
        """
        if type(identifier) is not str: raise TypeError("key must be 'str' but was '{0}'".format(str(type(identifier))[8:-2]))
        if not no_expand: identifier = expandidentifier(identifier)
        
        matched = []
        for key in self.keys():
            if re.match(identifier, key): matched.append( (key, self.get(key, parse=parse, cast=cast)) )
        return matched

    def getre(self, identifier, parse=False, cast=False):
        """
        Returns dict of properties which names matched given pattern.
        If parsed is set to True values will be parsed before returning. 
        If cast is passed as True pyproperties will try to cast types of properties.
        """
        matched = {}
        if type(identifier) == str: identifier = re.compile(identifier)
        else: raise TypeError("identifer must be 'str' but was '{0}'".format(str(type(identifier))[8:-2]))

        warnings.warn("`getre()` will be removed in 0.2.4: use `gets()` with `no_expand` argument set to True")

        for key, value in self.properties.items():
            if re.match(identifier, key) and parse: matched[key] = self._parseline(value)
            elif re.match(identifier, key) and not parse: matched[key] = value
        if cast:
            for key, value in matched.items(): matched[key] = convert(value)
        return matched

    def set(self, key, value=""):
        """
        Sets key to value. 
        Raises TypeError if key is not if `str` type.
        """
        if type(key) is not str: raise TypeError("key must be 'str' but was '{0}'".format(str(type(key))[8:-2]))
        if " " in key: raise TypeError("key must not contain space")
        self.properties[key] = value
        if key in self.hidden:
            self.unhide(key)
            self.rmcomment(key)
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
        
        identifier = re.compile(expandidentifier(identifier))
        for key, x in self.properties.items():
            if re.match(identifier, key): keys.append(key)
        keys.sort()
        i = 0
        for key in keys:
            try: value = values[i]
            except IndexError: value = values[-1]
            finally:
                if key in kwargs: value = kwargs[key]
                else: i += 1   # increasing the counter if value wasn't taken from the kwargs
                self.set(key, value)
        self.unsaved = True

    def remove(self, key):
        """
        This method removes specified property from interal dictionary. 
        Removed property will be not saved using store(). 
        """
        if key in self.properties: self.properties.pop(key)
        if key in self.propcomments: self.propcomments.pop(key)
        if key in self.hidden: self.hidden.remove(key)
        self.unsaved = True

    def removes(self, identifier):
        """
        This method removes properties matching given pattern from interal dictionary. 
        Removed properties will be not saved using store().
        """
        to_remove = []
        identifier = re.compile(expandidentifier(identifier))
        for key in self.properties.keys():
            if re.match(identifier, key): to_remove.append(key)
        for key in to_remove: self.remove(key)

    def pop(self, key, cast=False):
        """
        This method removes specified property from interal dictionary and returns its value. 
        KeyError is raised if key is not found or property is hidden.
        """
        if key not in self.properties or key in self.hidden: self._notavailable(key)

        prop = self.properties.pop(key)
        if cast: prop = convert(prop)
        self.unsaved = True
        return prop

    def pops(self, identifier, cast=False):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        """
        popped = self.gets(identifier=identifier, cast=cast)
        self.removes(identifier=identifier)
        self.unsaved = True
        return popped

    def keys(self, hidden=False):
        """
        Returns sorted list of the non-hidden properties names. 
        If `hidden` is passed as `True` returns sorted list 
        of including names of hidden properties.
        """
        keys = []
        for key in list(self.properties.keys()):
            if key not in self.hidden: keys.append(key)
            elif key in self.hidden and hidden == True: keys.append(key)
        return sorted(keys)

    def values(self, hidden=False):
        """
        Returns list of values this object holds. 
        If `hidden` is passed as `True` returns list of values 
        including values of hidden properties.
        """
        values = []
        for key in self.keys(hidden=hidden):
            if key not in self.hidden: values.append( self.get(key) )
            elif key in self.hidden and hidden == True: 
                self.unhide(key)
                values.append( self.get(key) )
                self.hide(key)
        return values

    def getkeysof(self, value, no_hidden=True):
        """
        Returns list of keys containing given value. 
        Returns empty list if no key was matched. 
        If `no_hidden` was passed as `False` includes also 
        commented properties.
        """
        keys = []
        for propkey, propvalue in self.properties.items():
            if value == propvalue and propkey not in self.hidden and no_hidden: keys.append(propkey)
            elif value == propvalue and propkey in self.hidden and not no_hidden: keys.append(propkey)
        return keys

    def getgroups(self):
        """
        Returns list of non-hidden properties groups in the internal dictionary. 
        Group is two or more properties which can be obtained with the same `gets()` identifier.

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
        will not form a group although `gets('person.*')` will return 
        list of length greater than two.

        This is because only digits are considered 'groupers'.
        """
        names = [ key.split(".") for key in self.keys() ]
        groups = []
        for key in names:
            identifier = ""
            for word in key:
                if ishex(word) or isoct(word) or re.match(re.compile(guess_int_re), word): word = "*"
                identifier = "{}.{}".format(identifier, word)
            identifier = identifier[1:]
            if identifier not in groups and len(self.gets(identifier)) > 1: groups.append(identifier)
        return groups

    def getsingles(self):
        """
        Returns list of properties which do not belong to any group.
        """
        groups = self.getgroups()
        singles = []
        for key in self.keys():
            key = re.sub(re.compile("\.[0-9]+\."), ".*.", key)
            key = re.sub(re.compile("\.[0-9]+$"), ".*", key)
            if key not in groups: singles.append(key)
        return singles

