#!/usr/bin/env python3

"""Working with *.properties files.

pyproperites aim is to ease manipulation, interaction and use of *.properties files in Python 3.x programs.
"""

import os
import re


__version__ = "0.1.6"

wildcart_re = "[a-z0-9_.-]*"
guess_int_re = "^[-]?[0-9]+$"
guess_float_re = "^[-]?[0-9]*\.[0-9]+$"

class LoadError(IOError): pass
class StoreError(IOError): pass
class UnsavedChangesError(BaseException): pass


def onlyhexchars(s):
    """
    Helper function.
    Returns True if given string conatins only 
    hexadecimal characters eg. 0-9a-f
    It detects hex of form 'beef01' and '0xbeef01'
    """
    result = False
    if re.match(re.compile("^(0x)?[0-9a-f]*$"), s): result = True
    elif s == "0": result = True
    return result


class Properties():
    """
    This class provides methods for working with properties files. 

    Variables describing stored properties:
        self.path               -   path used for reading and storing properties,
        self.source             -   working copy of source file,
        self.srcorigin          -   original lines of source file,
        self.properties         -   working copy of properties dictionary,
        self.propsorigin        -   original dictionary of properties,
        self.propcomments       -   dictionary containing comments of properties,
        self.origin_propcomments-   dictionary containing comments of properties,
        self.origin_commented   -   dictionary containing commented properties,
        self.commented          -   dictionary containing commented properties,
    """

    def __init__(self, path="", cast=False, no_read=False):
        """
        If you give a path as an argument it will be loaded and processed as properties file. 
        If you call Properties() without an argument created object will be "blank" - in this case you will have to call 
        foo.read(path, cast) to load some properties or 
        you can use the blank properties to create completly new set of properties.
        You can pass cast as True to tell pyproperites that it should guess the type of the property 
        and convert it accordingly.

        This method just calls read() with arguments passed to itself or blank() when no arguments are passed.
        
        To create a blank instance with path specified you can run: 
            pyproperites.Properties("/home/user/some/path/foo.properties", no_read=True)
        """
        if path != "" and not path.isspace() and not no_read: self.read(path, cast)
        elif path == "": self.blank()
        elif path != "" and not path.isspace() and no_read: 
            self.blank()
            self.path = path


    def __loadf__(self, path):
        """
        This method loads properties file from given path to a self.source list. 
        It also strips it of any newline character and whitespace on both sides but leaves it otherwise unprocessed. 
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


    def __loadd__(self, path):
        """
        This method reads directory tree as if it was properties file.
        """
        srcorigin = []
        source = []
        proppaths = []
        propnames = []
        propvalues = {}

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


    def __isvalidline__(self, line):
        """
        Checks if the line contains valid property string. 
        Valid string is non-empty string and its first character is not '#' or '!'.
        """
        result = line != "" and line[0] not in ["#", "!"] and ("=" in line or ":" in line or line[-1] == "\\")
        return result


    def __iscommentedprop__(self, line):
        """
        Defines if commented line is commented property.
        Used to distinguish comments from commented properties during
        load.
        """
        return self.__isvalidline__(line.strip()[1:]) and not self.__isvalidline__(line.strip())


    def __extractprops__(self):
        """
        Extracts lines containing valid properties strings from loaded source to self.properties
        It parses self.source line by line.
        Lines begining with '#' or '!' are considered comments and not parsed.
        Lines containing only whitespace are also not parsed.
        """
        extracted = []
        properties = []
        for i in range(len(self.source)):
            if self.__isvalidline__(self.source[i]): extracted.append(self.source[i])
        i = 0
        while i < len(extracted):
            line = extracted[i]
            while line[-1] == "\\":    #  if line ends with backslash read next line and append it to
                i += 1
                line = line[:-1] + extracted[i].lstrip()
            properties.append(line.lstrip())
            i += 1
        self.properties = properties


    def __extractcommentedprops__(self):
        """
        Extracts commented properties from file then uncomments them and 
        saves them to self.commented dictionary.
        """
        for i in range(len(self.source)):
            if self.__iscommentedprop__(self.source[i]):
                self.commented.append(self.__getkey__(self.source[i][1:]))
                self.origin_commented.append(self.__getkey__(self.source[i][1:]))
                self.source[i] = self.source[i][1:]


    def __extractcomments__(self):
        """
        Extracts comments loaded source to self.propcomments
        It parses self.source line by line. 
        
        When it finds valid line it goes up the file and appends 
        every line which begins with '#' or '!' and stops on 
        line which is only whitespace or a valid line.
        """
        propcomments = {}
        i = 0
        while i < len(self.source):
            if self.__isvalidline__(self.source[i]):
                try:
                    if self.source[i-1][0] in ["#", "!"]:
                        n = i-1
                        comment = []
                        while n >= 0:
                            try:
                                if self.source[n][0] not in ["#", "!"]: break
                                comment.append(self.source[n][1:].strip())
                                n -= 1
                            except IndexError: break
                            finally: pass
                        comment.reverse()
                        if comment: propcomments[self.__getkey__(self.source[i])] = comment
                        self.source = self.source[:n+1] + self.source[i:]
                except IndexError: pass
                finally: pass
            i += 1
        self.propcomments.update(propcomments)


    def __split__(self):
        """
        This method converts self.properties from list containing extracted lines to a dictionary.
        """
        props = {}
        origin = {}
        for i in range(len(self.properties)):
            key = self.__getkey__(self.properties[i])
            value = self.__getvalue__(self.properties[i])
            origin[key] = props[key] = value
        self.propsorigin = origin
        self.properties = props


    def __tcast__(self, identifier):
        """
        Converts property of the given key from str (default) to int or float if needed.
        """
        ptype = self.__typeguess__(self.get(identifier))
        self.set(identifier, ptype(self.get(identifier)))


    def __tcasts__(self, identifier):
        """
        Converts properties from str (default) to int or float (if needed). 
        """
        keys = []
        identifier = re.compile(identifier.replace("*", wildcart_re))
        for key in self.properties.keys():
            if re.match(identifier, key): keys.append(key)
        for key in keys: self.__tcast__(key)


    def __typeguess__(self, prop):
        """
        Tries to guess the type of property (initially all properties are stored as strings) and 
        convert it accordingly. It can guess three types: int, float and string.
        """
        re_int = re.compile(guess_int_re)
        re_float = re.compile(guess_float_re)

        if re.match(re_int, prop): ptype = int
        elif re.match(re_float, prop): ptype = float
        else: ptype = str
        return ptype


    def __getkey__(self, line):
        """
        Extracts key from given line and returns it. 
        If the line is comment or is blank returns None.
        """
        if line == "": key = None
        elif line[0] in ["#", "!"] or line.isspace(): key = None
        elif ":" in line[:line.find("=")]: key = line.split(":", 1)[0].strip()
        else: key = line.split("=", 1)[0].strip()
        return key


    def __getvalue__(self, line):
        """
        Extracts value from given line and returns it. 
        If the line is comment or is blank returns None. 
        It is done this way to distinguish properties with empty value 
        from lines which do not carry a property.
        """
        if line[-1] == "\n": line = line[:-1]   # striping newline while preserving newlines in value and trailing whitespace
        if line == "": value = None
        elif line[0] in ["#", "!"] or line.isspace(): value = None
        elif ":" in line[:line.find("=")]: value = line.split(":", 1)[1].lstrip()
        else: value = line.split("=", 1)[1].lstrip()
        if value[0] == "\\": value = value[1:]
        return value


    def _appendsrc(self, props, prefix=""):
        """
        This methods appends source of given properties to the base.
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
        self.origin_propcomments = {}
        self.commented = []
        self.origin_commented = []
        self.unsaved = False


    def read(self, path="", cast=False):
        """
        Reads properties file and processes it to be available in Python 3 program.
        You can pass 'cast' as True to tell pyproperites that it should guess the type of the property 
        and convert it accordingly (the __tcasts__ method will be called).
        """
        if path == "": path = self.path
        else: self.path = os.path.expanduser(path).strip()
        self.name = os.path.splitext(os.path.split(self.path)[-1])[0]
        if os.path.isfile(self.path): self.__loadf__(self.path)
        elif os.path.isdir(self.path): self.__loadd__(self.path)
        else: raise LoadError("'{0}' no such file or directory".format(path))
        self.commented = []
        self.origin_commented = []
        self.__extractcommentedprops__()
        self.__extractprops__()
        self.__split__()
        if cast: self.__tcasts__("*")
        self.propcomments = {}
        self.origin_propcomments = {}
        self.__extractcomments__()
        self.unsaved = False
        self.save()


    def reload(self):
        """
        Reloads from file. Missing values are added. Existing values are overwritten. 
        Values which are not found in file are deleted.
        """
        new = Properties(self.path)
        self.source = new.source
        self.properties = new.properties


    def refresh(self, overwrite=True):
        """
        Refreshes from file. Missing values are added.
        If 'overwrite' is set to True existing values are overwritten - merge() is used.
        'overwrite' defaults to True.
        Values which are not found in file are not deleted.
        """
        new = Properties(self.path)
        self.complete(new, "")
        if overwrite: self.update(new)


    def parseline(self, value):
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


    def parse(self, cast=False, props=False):
        """
        This method parses and returns parsed self.properties

        If props argument is passed as True parse() will return
        a Properties() object with all values parsed.
        """
        if props:
            parsed = Properties()
            parsed.merge(self)
            parsed.properties = parsed.parse()
            parsed.save()
        else:
            parsed = {}
            for key in self.properties: parsed[key] = self.get(key, True, cast)
        return parsed


    def copy(self):
        """
        Returns exact copy of a Properties() object.
        """
        copy = Properties()
        copy._appendsrc(self)
        for key in self.properties: copy.set(key, self.get(key))
        for key in self.propcomments: copy.addcomment(key, self.propcomments[key])
        copy.save()
        return copy


    def join(self, path, prefix=" "):
        """
        Loads external properties and completes base. 
        You can pass 'prefix' as empty string to add properties without prefix. 
        Prefix defaluts to joined modules name. 
        Source of joined properties is appended to base source.
        """
        path = path.strip()
        new = None
        try: 
            new = Properties(path)
            if prefix == " ": prefix = new.name
        except IOError: raise
        finally:
            if new:
                self.complete(new, prefix)
                self._appendsrc(new, prefix)
            else: pass
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
        for key in props.origin_commented:
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key not in self.commented and key in completed: self.comment(key)
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

        Properties for merging are taken from `origins` of given props so 
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
        for key in props.origin_commented:
            if prefix: key = "{0}.{1}".format(prefix, key)
            if key in updated: self.comment(key)
        self.unsaved = True


    def include(self, path):
        """
        Includes one file into another. Used only when processing source
        with __include__ properties.
        """
        props = pyproperites.Properties(path)


    def save(self):
        """
        Saves changes made in properties, source and comments.
        """
        saved = {}
        for key, value in self.properties.items(): saved[key] = value
        self.propsorigin = saved
        
        saved = []
        [ saved.append(line) for line in self.source ]
        self.srcorigin = saved
        
        saved = []
        [ saved.append(key) for key in self.commented ]
        self.origin_commented = saved

        saved = {}
        for key, value in self.propcomments.items(): saved[key] = value
        self.origin_propcomments = saved
        
        self.unsaved = False


    def revert(self):
        """
        Drops changes made in properties, source and comments by reverting them 
        to the state in which they were during last save().
        """
        reverted = {}
        for key, value in self.propsorigin.items(): reverted[key] = value
        self.properties = reverted
        
        reverted = []
        [ reverted.append(line) for line in self.srcorigin ]
        self.source = reverted
        
        reverted = []
        [ reverted.append(key) for key in self.origin_commented ]
        self.commented = reverted

        reverted = {}
        for key, value in self.origin_propcomments.items(): reverted[key] = value
        self.propcomments = reverted
        
        self.unsaved = False


    def _storesrc(self):
        """
        Prepares data which came with source for storing.
        """
        for i in range(len(self.srcorigin)):
            if self.srcorigin[i] == "" or self.srcorigin[i].isspace(): self.lines.append("{0}".format(self.srcorigin[i]))
            elif self.srcorigin[i][0] == "#": self.lines.append("{0}".format(self.srcorigin[i]))
            # checks if current line has a key which is defined in self.propsorigin and has not been stored yet
            elif self.__getkey__(self.srcorigin[i]) != "" and self.__getkey__(self.srcorigin[i]) not in self.stored:
                key = self.__getkey__(self.srcorigin[i])
                if key in self.propcomments: self._storecomment(key)
                if key not in self.origin_commented: self.lines.append("{0}={1}".format(key, self.propsorigin[key]))
                else: self.lines.append("#{0}={1}".format(key, self.propsorigin[key]))
                self.stored.append(key)
            else: pass


    def _storegroups(self):
        """
        Prepares groups not found in source file.
        """
        if self.lines != []: self.lines.append("")
        groups = self.getgroups()
        for identifier in groups:
            previous_len = len(self.lines)
            props = self.gets(identifier)
            keys = []
            [keys.append(key) for key in props]
            for key in sorted(keys):
                if key not in self.stored and key in self.propsorigin:
                    if key in self.propcomments: self._storecomment(key)
                    if key not in self.origin_commented: self.lines.append("{0}={1}".format(key, props[key]))
                    else: self.lines.append("#{0}={1}".format(key, props[key]))
                    self.stored.append(key)
            if len(self.lines) > previous_len: self.lines.append("")


    def _storesingles(self):
        """
        Preprares single values not found in source.
        """
        for key, value in sorted(self.propsorigin.items()):
            if key not in self.stored:
                if key in self.propcomments: self._storecomment(key)
                if key not in self.origin_commented: self.lines.append("{0}={1}".format(key, value))
                else: self.lines.append("#{0}={1}".format(key, value))
                self.stored.append(key)


    def _storecomment(self, key):
        """
        Appends comment of a property of given key to self.lines
        """
        [ self.lines.append("#   {0}".format(line)) for line in self.getcomment(key) ]


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


    def store(self, path="", force=False, no_dump=False):
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
        self._storesrc()
        self._storegroups()
        self._storesingles()
        while self.lines[-1] == "": self.lines = self.lines[:-1]
        if not no_dump: self._dump(path)


    def get(self, identifier, parsed=False, cast=False):
        """
        Returns value of identifier. 
        KeyError is raised if identifier is not found or property is commented.
        If parsed is set to True value will be parsed before returning.
        """
        if identifier in self.commented: raise KeyError
        if type(identifier) is not str: raise TypeError("identifer must be string but '{0}' was given".format(str(type(identifier))[8:-2]))
        if parsed: value = self.parseline(self.properties[identifier])
        else: value = self.properties[identifier]
        if cast and type(value) == str: value = self.__typeguess__(value)(value)
        return value


    def gets(self, identifier, parsed=False, cast=False):
        """
        Returns dict of properties which names matched pattern given as identifier.
        If parsed is set to True values will be parsed before returning.
        """
        if type(identifier) is not str: raise TypeError("identifer must be string but '{0}' was given".format(str(type(identifier))[8:-2]))

        matched = {}
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        for key, value in self.properties.items():
            if re.match(identifier, key) and parsed: matched[key] = self.parseline(value)
            elif re.match(identifier, key) and not parsed: matched[key] = value
        if cast:
            for key, value in matched.items():
                if type(value) == str: matched[key] = self.__typeguess__(value)(value)
        return matched


    def getre(self, identifier, parsed=False, cast=False):
        """
        Returns dict of properties which names matched given pattern.
        If parsed is set to True values will be parsed before returning. 
        If cast is passed as True pyproperites will try to cast types of properties.
        """
        matched = {}
        if type(identifier) == str: identifier= re.compile(identifier)
        elif str(type(identifier)) == "<class '_sre.SRE_Pattern'>": pass
        else: raise TypeError("identifer must be either string or compiled regular expression pattern, but '{0}' type was given".format(str(type(identifier))[8:-2]))

        for key, value in self.properties.items():
            if re.match(identifier, key) and parsed: matched[key] = self.parseline(value)
            elif re.match(identifier, key) and not parsed: matched[key] = value
        if cast:
            for key, value in matched.items(): matched[key] = self.__typeguess__(value)(value)
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

        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
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


    def remove(self, identifier):
        """
        This method removes specified property from interal dictionary. 
        Removed property will be not saved using store().
        """
        self.properties.pop(identifier)
        self.unsaved = True


    def removes(self, identifier):
        """
        This method removes properties matching given pattern from interal dictionary. 
        Removed properties will be not saved using store().
        """
        to_remove = []
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        for key in self.properties.keys():
            if re.match(identifier, key): to_remove.append(key)
        for key in to_remove: self.properties.pop(key)
        self.unsaved = True


    def pop(self, identifier, cast=False):
        """
        This method removes specified property from interal dictionary and returns its value. 
        Removed property will be not saved using store().
        """
        prop = self.properties.pop(identifier)
        if cast: prop = self.__typeguess__(prop)(prop)
        self.unsaved = True
        return prop


    def pops(self, identifier, cast=False):
        """
        This method removes properties matching given pattern from interal dictionary and returns a dict created from them. 
        Removed properties will be not saved using store().
        """
        popped = {}
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        for key, value in self.properties.items():
            if re.match(identifier, key): 
                popped[key] = value
        for key in popped.keys(): self.properties.pop(key)
        if cast: 
            for key, value in popped.items():
                popped[key] = self.__typeguess__(value)(value)
        self.unsaved = True
        return popped


    def getnames(self):
        """
        Returns sorted list of the property names. 
        """
        keys = []
        for key in list(self.properties.keys()):
            if key not in self.commented: keys.append(key)
        return sorted(keys)


    def getkeysof(self, value):
        """
        Returns list of keys containing given value. 
        Returns empty list if no key was matched.
        """
        keys = []
        for propkey, propvalue in self.properties.items():
            if value == propvalue: keys.append(propkey)
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

        This is because only digits (decimal and hex) are considered as 'groupers'.
        """
        skeys = []
        [ skeys.append(key.split(".")) for key in self.getnames() ]
        groups = []
        for skey in skeys:
            identifier = ""
            for key in skey:
                #   if key.isdigit(): key = "*"
                if onlyhexchars(key): key = "*"
                identifier = "{}.{}".format(identifier, key)
            identifier = identifier[1:]
            if identifier not in groups and len(self.gets(identifier)) > 1: groups.append(identifier)
        return groups


    def getsingles(self):
        """
        Returns list of properties which do not 
        belong to any group.
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

        Raises KeyError when property is not found.
        """
        if key not in self.properties: raise KeyError
        if type(comment) == str: comment = comment.split("\n")
        elif type(comment) == list:
            _comment = []
            [_comment.extend(l.split("\n")) for l in comment]
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

        addcomments('foo.*.bar', 'first comment', 'second\ncomment', ['third', 'comment'])
        """
        keys = self.gets(identifier)
        i = 0
        for key in keys:
            try: self.addcomment(key, comments[i])
            except IndexError: self.addcomment(key, comments[-1])
            finally: i += 1
        self.unsaved = True


    def rmcomment(self, key):
        """
        Removes comment of property of given key. 
        Does not raise KeyError when property is not found.
        """
        if key in self.propcomments: self.propcomments.pop(key)
        self.unsaved = True


    def getcomment(self, key):
        """
        Returns comment of given key. 
        Returns empty list if property has no comment.
        """
        if key in self.propcomments: comment = self.propcomments[key]
        else: comment = []
        return comment


    def comment(self, key):
        """
        When property gets commented it is no longer available for modifing.
        Raises KeyError when property is not found.
        """
        if key not in self.properties: raise KeyError("'{0}' is not in properties of {1}".format(key, self))
        if key not in self.commented: self.commented.append(key)
        self.unsaved = True
        

    def comments(self, identifier):
        """
        Comments every property which key will match given identifier. 
        """
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        for key in self.getnames():
            if re.match(identifier, key): self.comment(key)
        self.unsaved = True


    def uncomment(self, key):
        """
        Uncomments property to make it available for modifing. 
        Does not raise any errors when key is not found.
        """
        if key in self.commented: self.commented.remove(key)
        self.unsaved = True


    def uncomments(self, identifier):
        """
        Uncomments every property which key will match given identifier.
        """
        identifier = re.compile("^{0}$".format(identifier.replace(".", "\.").replace("*", wildcart_re)))
        to_uncomment = []
        for i in range(len(self.commented)):
            if re.match(identifier, self.commented[i]): to_uncomment.append(self.commented[i])
        for key in to_uncomment: self.uncomment(key)
        self.unsaved = True
