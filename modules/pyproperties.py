#!/usr/bin/env python3

"""Working with *.properties files."""

import os
import re
import warnings

__version__ = "0.2.1"
__vertuple__ = tuple( int(n) for n in __version__.split(".") )

wildcart_re = "[a-z0-9_.-]*"
guess_int_re = "^-?[0-9]+$"
guess_hex_re = "^-?(0x)?[0-9a-fA-F]+$"
guess_oct_re = "^-?(0o)?[0-7]+$"
guess_float_re = "^-?[0-9]*\.[0-9]+$"

class LoadError(IOError): pass
class StoreError(IOError): pass
class UnsavedChangesError(BaseException): pass

def ishex(s):
    """
    Helper function.
    Returns True if given string conatins only hexadecimal numbers.
    It detects hex of form 'beef01' and '0xbEEf01'
    """
    result = False
    if re.match(re.compile(guess_hex_re), s): result = True
    return result


def isoct(s):
    """
    Helper function.
    Returns True if given string conatins only octal numbers.
    """
    result = False
    if re.match(re.compile(guess_oct_re), s): result = True
    return result


class Properties():
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
        if path != "" and not path.isspace() and not no_read: self.read(path, cast, no_includes, strict)
        else: self.blank(path, strict)

    def _loadf(self, path):
        """
        This method loads properties file from given path to a ```self.source```. 
        It also strips it of newline characters at the end and preceding whitespace and but leaves it unprocessed in any different way. 
        """
        srcorigin = []
        source = []
        src = open(path, "rt")
        source = src.readlines()
        src.close()
        for i in range(len(source)):
            source[i] = source[i].lstrip()
            if source[i][-1:] == "\n": source[i] = source[i][:-1]
            srcorigin.append(source[i])
        self.source = source
        self.srcorigin = srcorigin

    def _loadd(self, path):
        """
        This method reads directory tree as if it was properties file.
        """
        srcorigin = []
        source = []
        proppaths = []
        propnames = []
        propvalues = {}

        warnings.warn("this feature is experimental and might not behave as expected")

        for root, dirs, files in os.walk(self.path):
            for file in files:
                proppaths.append(os.path.normpath(os.path.abspath("{0}{1}{2}".format(root, os.path.sep, file))))

        for i in range(len(proppaths)):
            propnames.append(proppaths[i].replace("{0}{1}".format(self.path, os.path.sep), "").replace(os.path.sep, "."))

        for i in range(len(proppaths)):
            value = open(proppaths[i]).read()
            if value[-2:] == "\\n": value = value[:-2]
            propvalues[ propnames[i] ] = value

        for key, value in propvalues.items():
            source.append("{0}={1}".format(key, value))

        self.source = source
        self.srcorigin = srcorigin


    def _notavailable(self, key):
        """
        Raises KeyError which will tell user that the property is not available eg. 
        is not in currently used set of properties or is hidden.
        """
        if key in self.hidden: message = "'{0}' is not available in {1}: hidden property".format(key, self)
        else: message = "'{0}' is not available in {1}".format(key, self)
        raise KeyError(message)

    def _tcast(self, key):
        """
        Converts property of the given key from str (default) to int, float, bool or None if needed.
        """
        self.set(key, self._convert(self.get(key)))


    def _tcasts(self, identifier):
        """
        Converts properties type from str (default) to int or float if pattern match. 
        """
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        for key in self.properties.keys():
            if re.match(identifier, key): self._tcast(key)


    def _convert(self, value, from_key=False):
        """
        Returns value with it's type casted. 
        Can convert from str to: int, float, True/False and None.
        If `from_key` is passed as True then `value` is treated as a key and used to obtain value of this key.
        Be aware that this can cause a KeyError to be raised.
        """
        if from_key: value = self.get(value)
        
        if value == "True": value = True
        elif value == "False": value = False
        elif value == "None": value = None
        elif ishex(value): value = int(value, 16)
        elif isoct(value): value = int(value, 8)
        else: value = self.typeguess(value)(value)
        return value

    def typeguess(self, prop):
        """
        Tries to guess the type of property (initially all properties are stored as strings) and 
        convert it accordingly. It can guess three types: int, float and str. 
        It returns guessed ```type``` of property.
        """
        re_int = re.compile(guess_int_re)
        re_float = re.compile(guess_float_re)

        if re.match(re_int, prop): ptype = int
        elif re.match(re_float, prop): ptype = float
        else: ptype = str
        return ptype


    def _linehaskey(self, line, strict=None):
        """
        Checks if the line contains a key. 
        """
        result = False
        if ":" in line[:line.find("=")]: key = line.split(":", 1)[0].strip()
        elif "=" in line[:line.find(":")]: key = line.split("=", 1)[0].strip()
        else: key = None

        if strict == None: strict = self.strict
        if key != None and key[0] not in ["#", "!"]:
            if strict and " " in key:
                warnings.warn("space found in key '{0}'".format(key))
                key = False
            elif not strict and " " in key:
                warnings.warn("space found in key: '{0}'".format(key))
                result = True
            else: 
                result = True
        return result

    def _isvalidline(self, line, strict=None):
        """
        Checks if the line contains valid property string. 
        Valid string is non-empty string and its first character is not '#' or '!'.
        """
        warnings.warn("_isvalidline() is deprecated (it is proxying _linehaskey() functionality) and will be removed in 0.2.2, use _linehaskey() instead", DeprecationWarning)
        return self._linehaskey(line, strict)

    def _iscommentline(self, line):
        """
        Checks if the line contains a comment string. 
        Valid string is non-empty string and its first character is '#' or '!'.
        """
        line = line.strip()
        result = line != "" and line[0] in ["#", "!"]
        return result


    def _islinehiddenprop(self, line, strict=None):
        """
        Defines if commented line is commented property.
        Used to distinguish comments from commented properties during
        load.
        """
        return self._linehaskey(line.strip()[1:], strict) and not self._linehaskey(line.strip(), strict)


    def getlinekey(self, line, strict=None):
        """
        Extracts key from given line and returns it. 
        If the line does not contain a key returns None. 
        
        If in strict mode (default) and find a whitespace in key it will 
        complain with a warning and return None. 
        If in non-strict mode (strict passed as `False`) it will only complain and 
        do nothing else.
        """
        if not self._linehaskey(line, strict): key = None
        elif ":" in line[:line.find("=")]: key = line.split(":", 1)[0].strip()
        else: key = line.split("=", 1)[0].strip()

        return key


    def getlinevalue(self, line, strict=None):
        """
        Extracts value from given line and returns it. 
        If the line does not have a value returns None (remeber: empty string is returned when line has it as a value). 
        It is done this way to distinguish properties with empty value 
        from lines which do not carry a property.
        """
        if not self._linehaskey(line, strict): value = None
        elif ":" in line[:line.find("=")]: value = line.split(":", 1)[1].lstrip()
        else: value = line.split("=", 1)[1].lstrip()

        if line != "" and line[-1] == "\n": line = line[:-1]   # striping newline while preserving newlines in value and trailing whitespace
        
        return value


    def _extracthidden(self):
        """
        Show hidden properties so they can be read by ```_extractprops()``` and 
        saves them to ```commented``` and ```origin_hidden``` dictionaries.
        """
        for i, line in enumerate(self.source):
            if self._islinehiddenprop(line):
                key = self.getlinekey(line[1:])
                if key not in self.hidden: self.hidden.append(key)
                if key not in self.origin_hidden: self.origin_hidden.append(key)
                self.source[i] = line[1:]


    def _extractprops(self):
        """
        Extracts lines containing valid properties strings from loaded source to self.properties
        It parses self.source line by line.
        Lines begining with '#' or '!' are considered comments and not parsed.
        Lines containing only whitespace are also not parsed.
        """
        extracted = []
        properties = []
        for i in range(len(self.source)):
            if self._linehaskey(self.source[i]): extracted.append(self.source[i])
        for i, line in enumerate(extracted):
            while line[-1] == "\\":    #  if line ends with backslash read next line and append it
                i += 1
                line = "".join(line[:-1], extracted[i]).lstrip()
            properties.append(line.lstrip())
        self.properties = properties


    def _extractcomments(self):
        """
        Extracts comments loaded source to self.propcomments
        It parses self.source line by line. 
        
        When it finds valid property line it goes up the file and appends 
        every line which begins with '#' or '!' and stops on 
        line which is only whitespace or a valid line.
        """
        propcomments = {}
        i = 0
        while i < len(self.source):
            if self._linehaskey(self.source[i]) and i > 0:
                if self._iscommentline(self.source[i-1]):
                    n = i-1
                    comment = []
                    while n >= 0:
                        if not self._iscommentline(self.source[n]): break
                        comment.append(self.source[n][1:].strip())
                        n -= 1
                    comment.reverse()
                    if comment: propcomments[self.getlinekey(self.source[i])] = comment
                    self.source = self.source[:n+1] + self.source[i:]
            i += 1
        self.propcomments.update(propcomments)


    def _split(self):
        """
        This method converts self.properties from list containing extracted lines to a dictionary.
        """
        props = {}
        origin = {}
        for i, line in enumerate(self.properties):
            key = self.getlinekey(line)
            if key in props: warnings.warn("multiple declarations for property '{0}' in file '{1}'".format(key, self.path))
            origin[key] = props[key] = self.getlinevalue(line)
        self.propsorigin = origin
        self.properties = props


    def _appendsrc(self, props, prefix=""):
        """
        This methods appends source of given properties to the base. 
        If ```source``` already contains some lines a blank line is added before actual 
        source to avoid making comments accidentaly joined.
        """
        lines = []
        for line in props.srcorigin:
            if line == "": lines.append(line)
            elif line[0] in ["#", "!"] or line.isspace(): lines.append(line)
            elif self._linehaskey(line) and not prefix: lines.append(line)
            elif self._linehaskey(line) and prefix: lines.append("{0}.{1}".format(prefix, line))
            else: pass
        if self.source: self.source.append("")
        self.source.extend(lines)


    def _include(self, line_number, path, prefix="", hidden=False):
        """
        This method is only run when a property file is being read. 
        It will dump another file in place specified by ```__include__``` directive.
        """
        if os.path.isabs(path): pass
        else: path = os.path.join(os.path.split(self.path)[0], path)
        
        path = open(path)
        file = path.readlines()
        path.close()
        for i, line in enumerate(file):
            if self._linehaskey(line) and prefix: line = "{0}.{1}".format(prefix, line.lstrip())
            elif self._islinehiddenprop(line) and prefix: line = "#{0}.{1}".format(prefix, line[1:])
            if self._linehaskey(line) and hidden: line = "#{0}".format(line.lstrip())
            if line[-1] == "\n": line = line[:-1]
            file[i] = line

        new_source = [ line for line in file ]
        self.source = self.source[:line_number] + new_source + self.source[line_number+1:]
        

    def _makeincludes(self):
        """
        This method runs during load and is kind of preprocessor. It will replace 
        every line which key begins with ```__include__``` with lines of file 
        it will try to read from the path specified in the value of the mentioned line.
        """
        i = 0
        while i < len(self.source):
            key = self.getlinekey(self.source[i])
            value = self.getlinevalue(self.source[i])
            if key == "__include__": self._include(i, value)
            elif key == "__include__.hidden": self._include(i, value, hidden=True)
            elif key != None and key[:15] == "__include__.as.": self._include(i, value, prefix=key[15:])
            elif key != None and key[:22] == "__include__.hidden.as.": self._include(i, value, prefix=key[22:], hidden=True)
            i += 1


    def _expandidentifier(self, identifier):
        """
        Applies needed changes to identifier and compiles regular expression pattern. 
        Returns compiled pattern.
        """
        return "^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re))
        
    def blank(self, path="", strict=True):
        """
        Creates blank properties object. 
        Can be used to erase contents of your ```pyproperties``` object.
        """
        self.path = os.path.expanduser(path.strip())
        self.name = os.path.splitext(os.path.split(self.path)[-1])[0]
        self.strict = True
        self.srcorigin = []
        self.source = []
        self.properties = {}
        self.propsorigin = {}
        self.propcomments = {}
        self.origin_propcomments = {}
        self.hidden = []
        self.origin_hidden = []
        self.strict = strict
        self.unsaved = False


    def read(self, path="", cast=False, no_includes=False, strict=True):
        """
        Reads properties file and processes it to be available in Python 3 program.
        You can pass 'cast' as True to tell pyproperties that it should guess the type of the property 
        and convert it accordingly (the _tcasts method will be called).
        """
        try:
            if self.path != "": path = self.path
        except AttributeError: pass
        finally: self.blank(path, strict)

        if os.path.isfile(self.path): self._loadf(self.path)
        elif os.path.isdir(self.path): self._loadd(self.path)
        else: raise LoadError("'{0}' no such file or directory".format(self.path))

        if not no_includes: self._makeincludes()
        self._extracthidden()
        self._extractprops()
        self._split()
        if cast: self._tcasts("*")
        self._extractcomments()
        self.save()


    def reload(self):
        """
        Reloads properties from `self.path`.
        """
        self.read(self.path)
        self.unsaved = True


    def refresh(self, overwrite=True):
        """
        Refreshes from file. Missing values are added.
        If ```overwrite``` is set to True existing values are overwritten - ```update()``` is used.
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
        You can pass ```prefix``` as empty string to add properties without prefix. 
        Prefix defaluts to the name of joined file. 
        Source of joined properties is appended to base source.
        """
        props = Properties(path)
        if prefix == " ": prefix = props.name
        self.complete(props, prefix)
        self._appendsrc(props, prefix)
        self.unsaved = True


    def complete(self, props, prefix=""):
        """
        This method completes base dictionary with properties of the given one. 
        If a property does not exist in base it will be added. 
        If a property exist in base it's value, comments and status (un/commented) 
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
        for key, value in props.propsorigin.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.properties:
                self.set(key, value)
                if key not in completed: completed.append(key)
        for key, value in props.origin_propcomments.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.propcomments and key in completed: self.addcomment(key, value)
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
        for key, value in props.propsorigin.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in self.properties: 
                self.set(key, value)
                updated.append(key)
        for key, value in props.origin_propcomments.items():
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in updated: self.addcomment(key, value)
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
                value = value.replace("$({0})".format(name), str(self.properties[name]))
        return value

    def parse(self, cast=False):
        """
        This method parses and returns parsed properties.
        """
        parsed = Properties()
        parsed.merge(self)
        for key in parsed.getnames(): parsed.set(key, parsed.get(key, parse=True))
        parsed.save()
        if cast: parsed._tcasts("*")
        return parsed

    def save(self):
        """
        Saves changes made in object's variables.
        """
        saved = {}
        for key, value in self.properties.items(): saved[key] = value
        self.propsorigin = saved
        saved = {}
        for key, value in self.propcomments.items(): saved[key] = value
        self.origin_propcomments = saved
        self.srcorigin = [ line for line in self.source ]
        self.origin_hidden = [ key for key in self.hidden ]
        self.unsaved = False


    def revert(self):
        """
        Drops changes made in properties object by reverting it's variables
        to the state in which they were during last save().
        """
        reverted = {}
        for key, value in self.propsorigin.items(): reverted[key] = value
        self.properties = reverted
        reverted = {}
        for key, value in self.origin_propcomments.items(): reverted[key] = value
        self.propcomments = reverted
        self.source = [ line for line in self.srcorigin ]
        self.hidden = [ key for key in self.origin_hidden ]
        self.unsaved = False


    def _storeprop(self, key):
        """
        This method stores single property and takes responsibility of storing it's comment and 
        possibly commenting the property itself. 
        This method looks at the ```stored``` list and checks if the given key has already 
        been stored to prevent storing it two times.
        It will also check if the key is in ```propsorigin``` dict to ensure that unsaved properties 
        would not be stored.
        """
        if key not in self.stored and key in self.propsorigin:
            if key in self.origin_propcomments: self._storecomment(key)
            if key not in self.origin_hidden: self.lines.append("{0}={1}".format(key, self.propsorigin[key]))
            else: self.lines.append("#{0}={1}".format(key, self.propsorigin[key]))
            self.stored.append(key)


    def _storesrc(self):
        """
        Prepares data which came with source for storing.
        """
        for i in range(len(self.srcorigin)):
            if self.srcorigin[i] == "" or self.srcorigin[i].isspace(): self.lines.append("{0}".format(self.srcorigin[i]))
            elif self.srcorigin[i][0] == "#": self.lines.append("{0}".format(self.srcorigin[i]))
            elif self.getlinekey(self.srcorigin[i]) != "": self._storeprop(self.getlinekey(self.srcorigin[i]))


    def _storegroups(self):
        """
        Generates lines for groups not found in source.
        """
        if self.lines != [] and self.lines[-1] != "": self.lines.append("")
        for identifier in self.getgroups():
            previous_len = len(self.lines)
            keys = []
            [keys.append(key) for key in self.gets(identifier)]
            for key in sorted(keys): self._storeprop(key)
            if len(self.lines) > previous_len: self.lines.append("")


    def _storesingles(self):
        """
        Generates lines for single properties not found in source.
        """
        for key in sorted(self.propsorigin.keys()): self._storeprop(key)


    def _storecomment(self, key):
        """
        Appends comment of a property of given key to self.lines
        """
        [ self.lines.append("#   {0}".format(line)) for line in self.origin_propcomments[key] ]


    def _dump(self, path):
        """
        Dumps generated lines to file given in path and clears 
        variables defined by store() and its subemthods.
        """
        file = open(path, "w")
        for line in self.lines: file.write("{0}\n".format(line))
        file.close()
        self.stored = []
        self.lines = []


    def store(self, path="", force=False, no_dump=False, drop_source=False):
        """
        Writes properties to given 'path'.
        'path' defaults to self.path

        If store will encounter some unsaved changes it will
        raise UnsavedChangesError.
        You can explicitly silence it by passing force as True.

        If self.path is empty it will be set to given path.

        If 'no_dump' is passed as True lines will be generated 
        but not written to file.
        """
        if self.unsaved and not force: raise UnsavedChangesError("trying to store with unsaved changes")
        if path == "": path = self.path    # this line defaults the value
        if path == "" or path.isspace(): raise StoreError("no path specified")
        if path and not self.path: self.path = path
        self.lines = []
        self.stored = []
        if not drop_source: self._storesrc()
        self._storegroups()
        self._storesingles()
        try:
            while self.lines[-1] == "": self.lines = self.lines[:-1]
        except IndexError: pass
        finally:
            if not no_dump: self._dump(path)


    def get(self, key, parse=False, cast=False):
        """
        Returns value of given key. 
        If parsed is set to True value will be parsed before returning.
        KeyError is raised if key is not available (not found or is hidden).
        """
        if key not in self.properties or key in self.hidden: self._notavailable(key)
        
        if parse: value = self._parseline(self.properties[key])
        else: value = self.properties[key]
        if cast and type(value) == str: value = self._convert(value)
        return value


    def gets(self, identifier, parse=False, cast=False):
        """
        Returns dict of properties which names matched pattern given as identifier.
        If parsed is set to True values will be parsed before returning.
        """
        if type(identifier) is not str: raise TypeError("key must be 'str' but was '{0}'".format(str(type(identifier))[8:-2]))
        identifier = self._expandidentifier(identifier)
        return self.getre(identifier)


    def getre(self, identifier, parse=False, cast=False):
        """
        Returns dict of properties which names matched given pattern.
        If parsed is set to True values will be parsed before returning. 
        If cast is passed as True pyproperties will try to cast types of properties.
        """
        matched = {}
        if type(identifier) == str: identifier = re.compile(identifier)
        elif str(type(identifier)) == "<class '_sre.SRE_Pattern'>":  warnings.warn("passing compiled regular expressions patterns is deprecated and support for it will be removed in 0.2.2")
        else: raise TypeError("identifer must be 'str' but was '{0}'".format(str(type(identifier))[8:-2]))

        for key, value in self.properties.items():
            if re.match(identifier, key) and parse: matched[key] = self._parseline(value)
            elif re.match(identifier, key) and not parse: matched[key] = value
        if cast:
            for key, value in matched.items(): matched[key] = self.typeguess(value)(value)
        return matched


    def set(self, key, value=""):
        """
        Sets key to value. 
        Raises TypeError if key is not if ```str``` type.
        """
        if type(key) is not str: raise TypeError("key must be 'str' but was '{0}'".format(str(type(key))[8:-2]))
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
        
        identifier = re.compile(self._expandidentifier(identifier))
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
        identifier = re.compile(self._expandidentifier(identifier))
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
        if cast: prop = self._convert(prop)
        self.unsaved = True
        return prop

    def pops(self, identifier, cast=False):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        """
        popped = {}
        identifier = re.compile(self._expandidentifier(identifier))
        for key, value in self.properties.items():
            if re.match(identifier, key): popped[key] = value
        for key in popped.keys(): self.properties.pop(key)
        if cast:
            for key, value in popped.items(): popped[key] = self.typeguess(value)(value)
        self.unsaved = True
        return popped

    def getnames(self, hidden=False):
        """
        Returns sorted list of the non-commented properties names. 
        If ```commented``` arg was passed as ```True``` returns sorted list 
        of commented properties names.
        """
        keys = []
        for key in list(self.properties.keys()):
            if key not in self.hidden and not hidden: keys.append(key)
            else: keys.append(key)
        return sorted(keys)

    def getkeysof(self, value, no_hidden=True):
        """
        Returns list of keys containing given value. 
        Returns empty list if no key was matched. 
        If ```no_hidden``` was passed as ```False``` includes also 
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
        skeys = [ key.split(".") for key in self.getnames() ]
        groups = []
        for skey in skeys:
            identifier = ""
            for key in skey:
                if ishex(key): key = "*"
                identifier = "{}.{}".format(identifier, key)
            identifier = identifier[1:]
            if identifier not in groups and len(self.gets(identifier)) > 1: groups.append(identifier)
        return groups

    def getsingles(self):
        """
        Returns list of properties which do not belong to any group.
        """
        groups = self.getgroups()
        singles = []
        for key in self.getnames():
            key = re.sub(re.compile("\.[0-9]+\."), ".*.", key)
            key = re.sub(re.compile("\.[0-9]+$"), ".*", key)
            if key not in groups: singles.append(key)
        return singles

    def addcomment(self, key, comment):
        """
        Attaches comment to property. 
        Comment can be passed as a string or list of strings.

            foo.addcomment("foo", ["first", "part"])
            foo.addcomment("foo", "first\\npart")

        Multiline comments are supported - either by passing a list of lines or
        by passing a string containing newline characters '\\n'.

        KeyError is raised if key is not available (not found or is hidden).
        """
        if key not in self.properties or key in self.hidden: self._notavailable(key)

        if type(comment) == str: comment = comment.split("\n")
        elif type(comment) == list:
            _comment = []
            [ _comment.extend(l.split("\n")) for l in comment ]
            comment = _comment
        else: comment = [comment]
        for i in range(len(comment)): comment[i] = "{0}".format(comment[i])
        self.propcomments[key] = comment
        self.unsaved = True

    def addcomments(self, identifier, *comments):
        """
        Attaches comment to properties which will match the identifier. 
        Comment can be passed as a string or a list. 
        Multiline comments are supported - either by passing a list of lines or
        by passing a string containing newline characters '\\n'.

        comments('foo.*.bar', 'first comment', 'second\ncomment', ['third', 'comment'])
        """
        keys = self.gets(identifier)
        i = 0
        for key in keys:
            try: self.addcomment(key, comments[i])
            except IndexError: self.addcomment(key, comments[-1])
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
        Returns empty list if the property has no comment and ```lines``` was passed as True. 
        KeyError is raised if key is not available (not found or is hidden).
        """
        if key not in self.properties or key in self.hidden: self._notavailable(key)
        
        if key in self.propcomments: comment = "\n".join(self.propcomments[key])
        else: comment = ""
        if lines and comment != "": comment = comment.split("\n")
        elif lines and comment == "": comment = []
        return comment

    def hide(self, key):
        """
        When property is hidden it is no longer available for modifing. 
        KeyError is raised if key is not available (not found or is hidden).
        """
        if key not in self.properties or key in self.hidden: self._notavailable(key)
        if key not in self.hidden: self.hidden.append(key)
        self.unsaved = True
        
    def hides(self, identifier):
        """
        Hides every property which key will match given identifier. 
        """
        identifier = self._expandidentifier(identifier)
        for key in self.getnames():
            if re.match(identifier, key): self.hide(key)

    def unhide(self, key):
        """
        Remove property from ```hidden``` list to make it available for modifing. 
        Does not raise any errors when key is not found.
        """
        if key in self.hidden: self.hidden.remove(key)
        self.unsaved = True

    def unhides(self, identifier):
        """
        Unhides every property which key will match given identifier.
        """
        identifier = self._expandidentifier(identifier)
        to_unhide = []
        for i in range(len(self.hidden)):
            if re.match(identifier, self.hidden[i]): to_unhide.append(self.hidden[i])
        for key in to_unhide: self.unhide(key)
