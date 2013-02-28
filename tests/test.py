#!/usr/bin/env python3

import unittest
import re
import os
import sys

from modules import pyproperties

__version__ = "0.2.6"

foo_path = "./data/properties/foo.properties"

class ReaderTest(unittest.TestCase):
    def testRaisesReadErrorWhenFileNotFound(self):
        reader = pyproperties.Reader(path="./file_not_found.properties")
        self.assertRaises(pyproperties.ReadError, reader.read)
    
    def testReaderInit(self):
        p = pyproperties.Reader(path="./data/properties/reader_test/foo.properties", cast=True, includes=False, strict=False)
        self.assertEqual(p._path, os.path.abspath("./data/properties/reader_test/foo.properties"))
        self.assertEqual(p._includes, False)
        self.assertEqual(p._cast, True)
        self.assertEqual(p._strict, False)
        
        r = pyproperties.Reader(path="./data/properties/reader_test/foo.properties")
        self.assertEqual(r._path, os.path.abspath("./data/properties/reader_test/foo.properties"))
        self.assertEqual(r._includes, True)
        self.assertEqual(r._cast, False)
        self.assertEqual(r._strict, True)
        self.assertEqual(r._source, [])
        self.assertEqual(r._hidden, [])
        self.assertEqual(r._comments, {})
        self.assertEqual(r._properties, [])

    def testLoadSimpleFile(self):
        """
        Method tested: `Reader.loadf()`
        Test if `loadf()` correctly loads simple properties file.
        """
        lines = [
                "foo=Foo  ",
                "",
                "bar=Bar",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.simple.properties")
        reader.loadf()
        self.assertEqual(lines, reader._source)

    def testLoadFileWithSplittedProperties(self):
        """
        Method tested: `Reader.loadf()`
        Test if `loadf()` correctly loads file with splitted properties.
        """
        lines = [
                "foo=Dura Lex     Sed Lex",
                "",
                "bar=Veni  Vidi Vici",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.splitted.properties")
        reader.loadf()
        self.assertEqual(lines, reader._source)

    def testLoadFileWithComments(self):
        """
        Method tested: `Reader.loadf()`
        Test if `loadf()` correctly loads file with comments.
        """
        lines = [
                "#   this is",
                "#   a comment",
                "foo=Foo  ",
                "",
                "#  this is another comment",
                "bar=Bar",
                "",
                "baz=Baz",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.commented.properties")
        reader.loadf()
        self.assertEqual(lines, reader._source)

    def testLoadFileWithCommentsEndingWithBackslash(self):
        """
        Method tested: `Reader.loadf()`
        Test if `loadf()` correctly loads file with comments ending with backslash.
        """
        lines = [
                "#   this is \\",
                "foo=Foo",
                "",
                "#   a comment \\",
                "bar=Bar",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.comments_with_escape.properties")
        reader.loadf()
        self.assertWarns(UserWarning, reader.loadf)
        self.assertEqual(lines, reader._source)
    
    def testExtractProperties(self):
        """
        Method tested: `Reader.extractprops()`
        Test if `extractprops()` correctly extracts properties from simple file.
        """
        props = [
                "foo=Foo  ",
                "bar=Bar",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.simple.properties")
        reader.loadf()
        reader.extractprops()
        self.assertEqual(props, reader._properties)

    def testExtractComments(self):
        """
        Method tested: `Reader.extractcomments()`
        Test if `extractprops()` correctly extracts comments from file.
        """
        comments =  {
                    "foo":"this is\na comment",
                    "bar":"this is another comment",
                    }
        lines = [
                "foo=Foo  ",
                "",
                "bar=Bar",
                "",
                "baz=Baz",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.commented.properties")
        reader.loadf()
        reader.extractprops()
        reader.extractcomments()
        self.assertEqual(comments, reader._comments)
        self.assertEqual(lines, reader._source)

    def testUncoverHiddenProperties(self):
        """
        Method tested: `Reader.uncoverhidden()`
        Test if `uncoverhidden()` correctly uncovers hidden properties.
        """
        hidden = ["foo", "bar"]
        props = [
                "foo=Foo",
                "bar=Bar",
                ]
        lines = [
                "foo=Foo",
                "",
                "bar=Bar",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.hidden.properties")
        reader.loadf()
        reader.uncoverhidden()
        reader.extractprops()
        self.assertEqual(props, reader._properties)
        self.assertEqual(hidden, reader._hidden)
        self.assertEqual(lines, reader._source)

    def testUncoverHiddenPropertiesWithComments(self):
        """
        Method tested: `Reader.uncoverhidden()`
        Test if `uncoverhidden()` correctly uncovers hidden properties but leaves comments untouched.
        """
        hidden = ["foo", "bar"]
        props = [
                "foo=Foo",
                "bar=Bar",
                ]
        comments =  {
                    "foo":"this is a comment",
                    }
        lines = [
                "#   this is",
                "#   a comment",
                "foo=Foo",
                "",
                "#   this is",
                "#   another comment",
                "bar=Bar",
                ]
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.hidden.commented.properties")
        reader.loadf()
        reader.uncoverhidden()
        reader.extractprops()
        self.assertEqual(props, reader._properties)
        self.assertEqual(hidden, reader._hidden)
        self.assertEqual(lines, reader._source)

    def testSplitProperties(self):
        """
        Method tested: `Reader.splitprops()`
        Test if `splitprops()` correctly splits properties into key and value.
        """
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.simple.properties")
        reader.loadf()
        reader.extractprops()
        props = [
                "foo=Foo  ",
                "bar=Bar",
                ]
        self.assertEqual(props, reader._properties)
        
        reader.splitprops()
        props = {
                "foo":"Foo  ",
                "bar":"Bar",
                }
        self.assertEqual(props, reader._properties)

    def testReadSimple(self):
        """
        Method tested: `Reader.read()`
        Test if `read()` correctly runs the process of reading simple properties file.
        """
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.simple.properties")
        reader.read()
        lines = [
                "foo=Foo  ",
                "",
                "bar=Bar",
                ]
        props = {
                "foo":"Foo  ",
                "bar":"Bar",
                }
        hidden = []
        comments = {}
        self.assertEqual(lines, reader._source)
        self.assertEqual(props, reader._properties)
        self.assertEqual(hidden, reader._hidden)
        self.assertEqual(comments, reader._comments)
    
    def testReadHidden(self):
        """
        Method tested: `Reader.read()`
        Test if `read()` correctly runs the process of reading properties file with hidden properties.
        """
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.hidden.properties")
        reader.read()
        lines = [
                "foo=Foo",
                "",
                "bar=Bar",
                ]
        props = {
                "foo":"Foo",
                "bar":"Bar",
                }
        hidden = ["foo", "bar"]
        comments = {}
        self.assertEqual(lines, reader._source)
        self.assertEqual(props, reader._properties)
        self.assertEqual(hidden, reader._hidden)
        self.assertEqual(comments, reader._comments)

    def testReadWithComments(self):
        """
        Method tested: `Reader.read()`
        Test if `read()` correctly runs the process of reading properties file with commented properties.
        """
        reader = pyproperties.Reader(path="./data/properties/reader_test/foo.commented.properties")
        reader.read()
        lines = [
                "foo=Foo  ",
                "",
                "bar=Bar",
                "",
                "baz=Baz",
                ]
        props = {
                "foo":"Foo  ",
                "bar":"Bar",
                "baz":"Baz",
                }
        hidden = []
        comments =  {
                    "foo":"this is\na comment",
                    "bar":"this is another comment",
                    }
        self.assertEqual(lines, reader._source)
        self.assertEqual(props, reader._properties)
        self.assertEqual(hidden, reader._hidden)
        self.assertEqual(comments, reader._comments)
    

class ReaderIncludeTest(unittest.TestCase):
    def testIncludeRaisesIncludeErrorWhenFileNotFound(self):
        """
        Method tested: `Reader._include()`
        Test if raises IncludeError when file being included is not found.
        """
        reader = pyproperties.Reader(path="")
        self.assertRaises(pyproperties.IncludeError, reader._include, path="./data/properties/include_test/nonexistent.properties", line_number=0)

    def testIncludeRaisesIncludeErrorWhenPathIsEmpty(self):
        """
        Method tested: `Reader._include()`
        Test if raises IncludeError when path is empty.
        """
        reader = pyproperties.Reader(path="")
        self.assertRaises(pyproperties.IncludeError, reader._include, path="", line_number=0)

    def testIncludeSimple(self):
        """
        Method tested: `Reader.read()`
        Tests if correctly includes files.
        """
        test = pyproperties.Reader(path="./data/properties/include_test/test.properties")
        combined = pyproperties.Reader(path="./data/properties/include_test/combined.properties")
        
        test.read()
        combined.read()

        self.assertEqual(test._source, combined._source)
        self.assertEqual(test._properties, combined._properties)
        self.assertEqual(test._comments, combined._comments)
        self.assertListEqual(sorted(test._hidden), sorted(combined._hidden))

    def testIncludePrefixed(self):
        """
        Method tested: `Reader.read()`
        Tests if correctly includes files with prefix.
        """
        test = pyproperties.Reader(path="./data/properties/include_test/test.prefix.properties")
        combined = pyproperties.Reader(path="./data/properties/include_test/combined.prefix.properties")

        test.read()
        combined.read()

        self.assertEqual(test._source, combined._source)
        self.assertEqual(test._properties, combined._properties)
        self.assertEqual(test._comments, combined._comments)
        self.assertEqual(test._hidden, combined._hidden)

    def testIncludeHidden(self):
        """
        Method tested: `Reader.read()`
        Tests if correctly includes files with prefix.
        """
        test = pyproperties.Reader("./data/properties/include_test/test.commented.properties")
        combined = pyproperties.Reader("./data/properties/include_test/combined.commented.properties")

        test.read()
        combined.read()

        self.assertEqual(test._source, combined._source)
        self.assertEqual(test._properties, combined._properties)
        self.assertEqual(test._comments, combined._comments)
        self.assertEqual(test._hidden, combined._hidden)

    def testIncludeHiddenAndPrefixed(self):
        test = pyproperties.Reader("./data/properties/include_test/test.commented.prefix.properties")
        combined = pyproperties.Reader("./data/properties/include_test/combined.commented.prefix.properties")

        test.read()
        combined.read()

        self.assertEqual(test._source, combined._source)
        self.assertEqual(test._properties, combined._properties)
        self.assertEqual(test._comments, combined._comments)
        self.assertEqual(test._hidden, combined._hidden)


class PropertiesIncludeTests(unittest.TestCase):
    def testSetIncludeRaisesIncludeErrorWhenPathEmpty(self):
        p = pyproperties.Properties()
        self.assertRaises(pyproperties.IncludeError, p.addinclude, "")

    def testSetIncludeWarnsWhenFileNotFound(self):
        p = pyproperties.Properties()
        self.assertWarns(pyproperties.IncludeWarning, p.addinclude, "./data/properties/include_test/no.properties")

    def testSetIncludeSimple(self):
        p = pyproperties.Properties()
        p.addinclude("./data/properties/include_test/test.properties")
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "", False)])

    def testSetIncludePrefixed(self):
        p = pyproperties.Properties()
        p.addinclude("./data/properties/include_test/test.properties", prefix="foo")
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "foo", False)])

    def testSetIncludeHidden(self):
        p = pyproperties.Properties()
        p.addinclude("./data/properties/include_test/test.properties", hidden=True)
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "", True)])

    def testSetIncludePrefixedAndHidden(self):
        p = pyproperties.Properties()
        p.addinclude("./data/properties/include_test/test.properties", prefix="foo", hidden=True)
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "foo", True)])

    def testRmIncludeSimple(self):
        p = pyproperties.Properties() 
        p.addinclude("./data/properties/include_test/test.properties")
        p.rminclude("./data/properties/include_test/test.properties")
        
        self.assertEqual(p._includes, [])

    def testRmIncludePrefixed(self):
        p = pyproperties.Properties() 
        p.addinclude("./data/properties/include_test/test.properties", prefix="foo")
        p.addinclude("./data/properties/include_test/test.properties", prefix="bar")
        p.rminclude("./data/properties/include_test/test.properties", prefix="foo")
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "bar", False)])

    def testRmIncludeHidden(self):
        p = pyproperties.Properties() 
        p.addinclude("./data/properties/include_test/test.properties", hidden=True)
        p.addinclude("./data/properties/include_test/test.properties")
        p.rminclude("./data/properties/include_test/test.properties", hidden=True)
        
        self.assertEqual(p._includes, [("./data/properties/include_test/test.properties", "", False)])

    def testRmIncludePrefixedAndHidden(self):
        p = pyproperties.Properties() 
        p.addinclude("./data/properties/include_test/test.properties", prefix="foo", hidden=True)
        p.addinclude("./data/properties/include_test/test.properties", prefix="bar", hidden=True)
        p.addinclude("./data/properties/include_test/test.properties", prefix="foo", hidden=False)
        p.addinclude("./data/properties/include_test/test.properties", prefix="bar", hidden=False)
        includes =  [
                    ("./data/properties/include_test/test.properties", "foo", False),
                    ("./data/properties/include_test/test.properties", "bar", False),
                    ]
        p.rminclude("./data/properties/include_test/test.properties", prefix="foo", hidden=True)
        p.rminclude("./data/properties/include_test/test.properties", prefix="bar", hidden=True)
        self.assertEqual(p._includes, includes)

    def testPurgeIncludeWarnsWhenNothingWasRemoved(self):
        p = pyproperties.Properties() 
        self.assertWarns(pyproperties.IncludeWarning, p.purgeinclude, "./data/properties/include_test/test.properties")

    def testPurgeIncludeSimple(self):
        test = pyproperties.Properties("./data/properties/include_test/test.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.purgeinclude("./../../../data/properties/include_test/bar.properties")
        
        self.assertEqual(test._includes, [("foo.properties", "", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testPurgeIncludePrefixed(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.prefixed.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.purgeinclude("./../../../data/properties/include_test/bar.properties", prefix="bar")
        
        self.assertEqual(test._includes, [("foo.properties", "", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testPurgeIncludeHidden(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.hidden.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.purgeinclude("./../../../data/properties/include_test/bar.properties", hidden=True)

        self.assertEqual(test._includes, [("foo.properties", "", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testPurgeIncludePrefixedAndHidden(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.hidden.prefixed.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.purgeinclude("./../../../data/properties/include_test/bar.properties", prefix="bar", hidden=True)
        
        self.assertEqual(test._includes, [("foo.properties", "", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testStripIncludeSimple(self):
        test = pyproperties.Properties("./data/properties/include_test/test.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.stripinclude("./../../../data/properties/include_test/bar.properties")
        
        self.assertEqual(test._includes, [("foo.properties", "", False), ("./../../../data/properties/include_test/bar.properties", "", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testStripIncludePrefixed(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.prefixed.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.stripinclude("./../../../data/properties/include_test/bar.properties", prefix="bar")
        
        self.assertEqual(test._includes, [("foo.properties", "", False), ("./../../../data/properties/include_test/bar.properties", "bar", False)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testStripIncludeHidden(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.hidden.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.stripinclude("./../../../data/properties/include_test/bar.properties", hidden=True)
        
        self.assertEqual(test._includes, [("foo.properties", "", False), ("./../../../data/properties/include_test/bar.properties", "", True)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)

    def testStripIncludePrefixedAndHidden(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.hidden.prefixed.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined_purge.properties")
        test.stripinclude("./../../../data/properties/include_test/bar.properties", prefix="bar", hidden=True)
        
        self.assertEqual(test._includes, [("foo.properties", "", False), ("./../../../data/properties/include_test/bar.properties", "bar", True)])
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)
    
    def testListinlcudes(self):
        test = pyproperties.Properties("./data/properties/include_test/test_purge.hidden.prefixed.properties")
        self.assertEqual( test.listincludes(), test._includes )
    
    def testRemovingKeysOfFile(self):
        test = pyproperties.Properties()
        test.set("prop.0")
        test.set("prop.1")
        test.set("prop.2")
        test.set("foo")
        test._rmkeysfrom("./data/properties/baz.properties")
        self.assertEqual({"foo":""}, test.properties)


class WriterTest(unittest.TestCase):
    def testRaisesUnsavedChangesError(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        writer = pyproperties.Writer(foo)
        self.assertRaises(pyproperties.UnsavedChangesError, writer.store, "")

    def testRaisesStoreErrorWhenNoPathGiven(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        foo.save()
        writer = pyproperties.Writer(foo)
        self.assertRaises(pyproperties.StoreError, writer.store, "")

    def testWriteLoadedWithNoModifications(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "#   This is a comment for massage.0",
                    "message.0=Apple $(name.1).",
                    "message.1=Arr... Welcome, $(name.0)!",
                    "#   This is a comment for name.0 which",
                    "#   value is \"John the Average\"",
                    "name.0=John the Average",
                    "name.1=Jack  ",
                    "name.2=\\  William  ",
                    "alert=Fire!",
                    ]
        writer = pyproperties.Writer(bar)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteLoadedSomeValuesRemoved(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "message.1=Arr... Welcome, $(name.0)!",
                    "#   This is a comment for name.0 which",
                    "#   value is \"John the Average\"",
                    "name.0=John the Average",
                    "name.2=\\  William  ",
                    "alert=Fire!",
                    ]
        bar.remove("message.0")
        bar.remove("name.1")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteLoadedEveryOriginalValueRemoved(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    ]
        bar.removes("*")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteLoadedEveryOriginalPropertyRemovedAndNewPropertiesAdded(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "prop.0=0",
                    "#   this is a comment for prop.1",
                    "prop.1=1",
                    "#prop.2=2",
                    ]
        bar.removes("*")
        bar.set("prop.0", "0")
        bar.set("prop.1", "1")
        bar.comment("prop.1", "this is a comment for prop.1")
        bar.set("prop.2", "2")
        bar.hide("prop.2")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteLoadedAndCommented(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "#   This is a comment for massage.0",
                    "message.0=Apple $(name.1).",
                    "message.1=Arr... Welcome, $(name.0)!",
                    "#   This is a comment for name.0 which",
                    "#   value is \"John the Average\"",
                    "name.0=John the Average",
                    "#   possibly Sparrow",
                    "name.1=Jack  ",
                    "#   his name is William",
                    "#   that's for sure",
                    "name.2=\\  William  ",
                    "#alert=Fire!",
                    ]
        bar.hide("alert")
        bar.comment("name.2", "his name is William\nthat's for sure")
        bar.comment("name.1", "possibly Sparrow")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteLoadedAndCommentsRemoved(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "message.0=Apple $(name.1).",
                    "message.1=Arr... Welcome, $(name.0)!",
                    "#   This is a comment for name.0 which",
                    "#   value is \"John the Average\"",
                    "name.0=John the Average",
                    "name.1=Jack  ",
                    "name.2=\\  William  ",
                    "alert=Fire!",
                    ]
        bar.rmcomment("message.0")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteChangedComments(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    "",
                    "#   This is a comment for massage.0",
                    "message.0=Apple $(name.1).",
                    "message.1=Arr... Welcome, $(name.0)!",
                    "#   This is changed comment for name.0",
                    "name.0=John the Average",
                    "name.1=Jack  ",
                    "name.2=\\  William  ",
                    "alert=Fire!",
                    ]
        bar.comment("name.0", "This is changed comment for name.0")
        bar.save()
        writer = pyproperties.Writer(bar)
        writer.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteCreatedFromBlankAndCommented(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.set("foo", "Foo")
        foo.set("bar", "Bar")
        foo.save()
        foo.hide("foo")
        self.assertRaises(KeyError, foo.comment, "foo", "foo's comment")
        foo.comment("bar", "bar's comment")
        self.assertRaises(pyproperties.UnsavedChangesError, foo.store, "")
        foo.save()
        lines = [
                "#   bar's comment",
                "bar=Bar",
                "#foo=Foo",
                ]
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteIncludesAdded(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.addinclude(path="foo.properties", prefix="", hidden=False)
        foo.addinclude(path="bar.properties", prefix="", hidden=False)
        foo.save()
        lines = [
                "__include__=foo.properties",
                "",
                "__include__=bar.properties",
                ]
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteIncludesAddedHidden(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.addinclude(path="foo.properties", prefix="", hidden=True)
        foo.addinclude(path="bar.properties", prefix="", hidden=False)
        foo.save()
        lines = [
                "__include__.hidden=foo.properties",
                "",
                "__include__=bar.properties",
                ]
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteIncludesAddedPrefixed(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.addinclude(path="foo.properties", prefix="foo", hidden=False)
        foo.addinclude(path="bar.properties", prefix="", hidden=False)
        foo.save()
        lines = [
                "__include__.as.foo=foo.properties",
                "",
                "__include__=bar.properties",
                ]
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteIncludesAddedPrefixedAndHidden(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.addinclude(path="foo.properties", prefix="foo", hidden=False)
        foo.addinclude(path="bar.properties", prefix="", hidden=True)
        foo.addinclude(path="baz.properties", prefix="baz", hidden=True)
        foo.save()
        lines = [
                "__include__.as.foo=foo.properties",
                "",
                "__include__.hidden=bar.properties",
                "",
                "__include__.hidden.as.baz=baz.properties",
                ]
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(lines, writer.lines)

    def testWriteForced(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.set("some.prop", "some value")
        foo.set("other.prop", "other value")
        foo.save()
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True)
        self.assertEqual(["other.prop=other value", "some.prop=some value"], writer.lines)
        foo.set("another.prop", "another value")
        writer = pyproperties.Writer(foo)
        writer.store(no_dump=True, force=True)
        self.assertEqual(["other.prop=other value", "some.prop=some value"], writer.lines)


class JSONExporterTests(unittest.TestCase):
    def testExporterInit(self):
        foo = pyproperties.Properties(path="foo.properties", no_read=True)
        writer = pyproperties.Exporter.JSON(foo)
        self.assertEqual("foo.json", writer._path)

        bar = pyproperties.Properties(path="/home/user/bar.properties", no_read=True)
        writer = pyproperties.Exporter.JSON(bar)
        self.assertEqual("/home/user/bar.json", writer._path)
    
    def testRaisesUnsavedChangesError(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        writer = pyproperties.Exporter.JSON(foo)
        self.assertRaises(pyproperties.UnsavedChangesError, writer.store, "")

    def testRaisesStoreErrorWhenNoPathGiven(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        foo.save()
        writer = pyproperties.Exporter.JSON(foo)
        self.assertRaises(pyproperties.StoreError, writer.store, "")
    
    def testStoreProperty(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.save()
        writer = pyproperties.Exporter.JSON(foo)
        writer.storeprop("foo")
        writer.encode()
        self.assertEqual({'foo':''}, writer._json)
        self.assertEqual('{"foo": ""}', writer.json)


class ValidatorsTest(unittest.TestCase):
    def testCommentlineValidator(self):
        lines = [
                ("#some comment", True),
                ("!  text", True),
                ("#   string", True),
                ("!", True),
                ("# ", True),
                ("  ! ", True),
                ("#maybe=property", True),
                ("not a comment", False),
                ("", False),
                ("  indent", False),
                ("  indented=property", False),
                ("  some#string", False),
                ]
        for line, result in lines: self.assertEqual(pyproperties.iscomment(line), result)
    
    def testHaskeyNonStrict(self):
        lines = [
                ("#some comment", False),
                ("#maybe=property", False),
                ("not a property", False),
                ("", False),
                ("  indent", False),
                ("    ", False),
                ("some thing = not valid", True),
                ("  indented=property", True),
                ("valid  = property", True),
                ("valid:property", True),
                ("valid      : property", True),
                ("   valid  : property", True),
                ]
        for line, result in lines: self.assertEqual(pyproperties.linehaskey(line, strict=False), result)

    def testHaskeyStrict(self):
        foo = pyproperties.Properties()
        lines = [
                ("#some comment", False),
                ("#maybe=property", False),
                ("not a property", False),
                ("", False),
                ("  indent", False),
                ("    ", False),
                ("some thing = not valid", False),
                ("  indented=property", True),
                ("valid  = property", True),
                ("valid:property", True),
                ("valid      : property", True),
                ("   valid  : property", True),
                ("__include__=./foo.properties", True),
                ("__include__.as.bar : ./foo.properties", True),
                ("__include__.hidden.as.bar=./foo.properties", True),
                ]
        for line, result in lines: self.assertEqual(pyproperties.linehaskey(line, strict=True), result)

    def testGetlinekeyNonStrict(self):
        foo = pyproperties.Properties(strict=False)
        lines = [
                ("#some comment", None),
                ("#maybe=property", None),
                ("not a property", None),
                ("", None),
                ("  indent", None),
                ("    ", None),
                ("some thing = not valid", "some thing"),
                ("  indented=property", "indented"),
                ("valid  = property", "valid"),
                ("valid:property", "valid"),
                ("valid      : property", "valid"),
                ("   valid  : property", "valid"),
                ]
        for line, result in lines: self.assertEqual(pyproperties.getlinekey(line, strict=foo.strict), result)


    def testGetlinekeyStrict(self):
        foo = pyproperties.Properties()
        lines = [
                ("#some comment", None),
                ("#maybe=property", None),
                ("not a property", None),
                ("", None),
                ("  indent", None),
                ("    ", None),
                ("some thing = not valid", None),
                ("  indented=property", "indented"),
                ("valid  = property", "valid"),
                ("valid:property", "valid"),
                ("valid      : property", "valid"),
                ("   valid  : property", "valid"),
                ]
        for line, result in lines: self.assertEqual(pyproperties.getlinekey(line, strict=foo.strict), result)

    def testGetlinevalueNonStrict(self):
        foo = pyproperties.Properties(strict=False)
        lines = [
                ("#some comment", None),
                ("#maybe=property", None),
                ("not a property", None),
                ("", None),
                ("  indent", None),
                ("    ", None),
                ("some thing = not valid", "not valid"),
                ("  indented=property", "property"),
                ("valid  = property", "property"),
                ("valid:property", "property"),
                ("valid      : property", "property"),
                ("   valid  : property", "property"),
                ]
        for line, result in lines: self.assertEqual(pyproperties.getlinevalue(line, strict=foo.strict), result)


    def testGetlinevalueStrict(self):
        foo = pyproperties.Properties()
        lines = [
                ("#some comment", None),
                ("#maybe=property", None),
                ("not a property", None),
                ("", None),
                ("  indent", None),
                ("    ", None),
                ("some thing = not valid", None),
                ("  indented=property", "property"),
                ("valid  = property", "property"),
                ("valid:property", "property"),
                ("valid      : property", "property"),
                ("   valid  : property", "property"),
                ]
        for line, result in lines: self.assertEqual(pyproperties.getlinevalue(line, strict=foo.strict), result)

    def testHiddenPropertiesDetectionWhenStrict(self):
        r = pyproperties.Reader(path="")
        lines = [
                ("#some.key=0", True),
                ("#some key=0", False),
                ("# some.key=0", False),
                ]
        for line, result in lines: self.assertEqual(result, r._islinehiddenprop(line))

    def testHiddenPropertiesDetectionWhenNonStrict(self):
        foo = pyproperties.Reader(path="", strict=False)
        lines = [
                ("#some.key=0", True),
                ("#some key=0", True),
                ("# some.key=0", False),
                ("# some key=0", False),
                ]
        for line, result in lines: self.assertEqual(result, foo._islinehiddenprop(line))


class ParselineTest(unittest.TestCase):
    def testParselineInteger(self):
        foo = pyproperties.Properties()
        foo.set("two.0", 2)
        foo.set("two.1", "2")
        self.assertEqual(2, foo.get("two.0", parse=True, cast=True))
        self.assertEqual(2, foo.get("two.0", parse=True, cast=False))
        self.assertEqual(2, foo.get("two.1", parse=True, cast=True))
        self.assertEqual("2", foo.get("two.1", parse=True, cast=False))


    def testParselineFloat(self):
        foo = pyproperties.Properties()
        foo.set("pi.0", 3.14)
        foo.set("pi.1", "3.14")
        self.assertEqual(3.14, foo.get("pi.0", parse=True, cast=True))
        self.assertEqual(3.14, foo.get("pi.0", parse=True, cast=False))
        self.assertEqual(3.14, foo.get("pi.1", parse=True, cast=True))
        self.assertEqual("3.14", foo.get("pi.1", parse=True, cast=False))


    def testParselineString(self):
        foo = pyproperties.Properties()
        foo.set("greeting", "Hello $(name)!")
        foo.set("name", "World")
        self.assertEqual("Hello World!", foo.get("greeting", parse=True, cast=True))
        self.assertEqual("Hello World!", foo.get("greeting", parse=True, cast=False))


    def testParselineComplex(self):
        foo = pyproperties.Properties()
        foo.set("greeting", "Hello $(name)! Happy $(number)th day of week! Did you know that Pi is $(pi.value)?")
        foo.set("name", "World")
        foo.set("number", 7)
        foo.set("pi.value", 3.14159)
        self.assertEqual("Hello World! Happy 7th day of week! Did you know that Pi is 3.14159?", foo.get("greeting", parse=True, cast=True))
        self.assertEqual("Hello World! Happy 7th day of week! Did you know that Pi is 3.14159?", foo.get("greeting", parse=True, cast=False))


class ParseTest(unittest.TestCase):
    def testParse(self):
        bar = pyproperties.Properties(foo_path.replace("foo", "bar"))
        parsed =    [
                    ("alert", "Fire!"),
                    ("message.0", "Apple Jack  ."),
                    ("message.1", "Arr... Welcome, John the Average!"),
                    ("name.0", "John the Average"),
                    ("name.1", "Jack  "),
                    ("name.2", "\\  William  "),
                    ]
        pbar = pyproperties.Engine.parse(bar)
        self.assertEqual(parsed, sorted(pbar.gets("*")))
        self.assertEqual(pyproperties.Properties, type(pbar))

    def testParseCasted(self):
        bar = pyproperties.Properties()
        bar.set("pi.part.0", "3")
        bar.set("pi.part.1", "14")
        bar.set("pi", "$(pi.part.0).$(pi.part.1)")
        bar.set("true.part.0", "Tr")
        bar.set("true.part.1", "ue")
        bar.set("true", "$(true.part.0)$(true.part.1)")
        bar.set("none.part.0", "No")
        bar.set("none.part.1", "ne")
        bar.set("none", "$(none.part.0)$(none.part.1)")
        bar.save()
        props = [
                ("none", None),
                ("none.part.0", "No"),
                ("none.part.1", "ne"),
                ("pi", 3.14),
                ("pi.part.0", 3),
                ("pi.part.1", 14),
                ("true", True),
                ("true.part.0", "Tr"),
                ("true.part.1", "ue"),
                ]
        pbar = pyproperties.Engine.parse(bar, cast=True)
        self.assertEqual(props, sorted(pbar.gets("*")))
        self.assertEqual(pyproperties.Properties, type(pbar))


class ConvertTest(unittest.TestCase):
    def testIntegerConversion(self):
        examples = [("3", 3),
                    ("-1", -1),
                    ("16", 16),
                    ("-12648", -12648),
                    ("-666324992", -666324992),
                    ("666324992", 666324992),
                    ]
        for s, n in examples: self.assertEqual(pyproperties.Engine.convert(s), n)

    def testBinaryConversion(self):
        examples = [("0b0", 0),
                    ("-0b1", -1),
                    ("0b10", 2),
                    ("0b11", 3),
                    ("-0b110101001", -425),
                    ("0b1010011010", 666),
                    ]
        for s, n in examples: self.assertEqual(pyproperties.Engine.convert(s), n)

    def testOctalConversion(self):
        examples = [("0o0", 0),
                    ("-0o1", -1),
                    ("0o26", 22),
                    ("-0o242", -162),
                    ("0o105", 69),
                    ("0o1232", 666),
                    ("-0o3713", -1995),
                    ("0o3734", 2012),
                    ("0o21270", 8888),
                    ("0o2602", 1410),
                    ("-0o2602", -1410),
                    ("0o726746425", 123456789),
                    ("-0o172116", -62542),
                    ]
        for oct, dec in examples: self.assertEqual(pyproperties.Engine.convert(oct), dec)
    
    def testHexadecimalConversion(self):
        examples = [("0x0", 0),
                    ("-0x1", -1),
                    ("0x16", 22),
                    ("-0xa2", -162),
                    ("0x45", 69),
                    ("0x29a", 666),
                    ("-0x7cb", -1995),
                    ("0x7dc", 2012),
                    ("0x22b8", 8888),
                    ("0x582", 1410),
                    ("-0x582", -1410),
                    ("0x75bcd15", 123456789),
                    ("-0xf44e", -62542),
                    ]
        for hex, dec in examples: self.assertEqual(pyproperties.Engine.convert(hex), dec)

    def testFloatConversion(self):
        examples = [("3.14", 3.14),
                    ("-1.43", -1.43),
                    ("6.02e+23", 6.02e+23),
                    ("6.02e-23", 6.02e-23),
                    ("6.02e23", 6.02e+23),
                    ]
        for s, n in examples: self.assertEqual(pyproperties.Engine.convert(s), n)

    def testBooleanConversion(self):
        self.assertEqual(pyproperties.Engine.convert("True"), True)
        self.assertEqual(pyproperties.Engine.convert("False"), False)
    
    def testNoneConversion(self):
        self.assertEqual(pyproperties.Engine.convert("None"), None)


class BlankTest(unittest.TestCase):
    def testBlank(self):
        test = pyproperties.Properties("./foo.properties", no_read=True)
        test.set("foo", "Foo")
        test.set("boo", "Bar")
        test.save()
        test.blank()
        self.assertEqual("./foo.properties", test.path)


class ReadFromPropertiesTest(unittest.TestCase):
    def testNoRead(self):
        loaded = pyproperties.Properties("./data/properties/bar.properties", no_read=True)
        self.assertEqual("./data/properties/bar.properties", loaded.path)
        self.assertEqual([], loaded.origin_source)
        self.assertEqual([], loaded.source)
        self.assertEqual({}, loaded.origin_properties)
        self.assertEqual({}, loaded.properties)
        self.assertEqual({}, loaded.propcomments)

    def testDifferentReadCustoms(self):
        bara = pyproperties.Properties("./data/properties/bar.properties", no_read=True)
        barb = pyproperties.Properties()
        bara.read()
        barb.read("./data/properties/bar.properties")

        print()
        print( bara.path )
        print( barb.path )

        self.assertEqual(bara.path, barb.path)
        self.assertEqual(bara.origin_source, barb.origin_source)
        self.assertEqual(bara.source, barb.source)
        self.assertEqual(bara.origin_properties, barb.origin_properties)
        self.assertEqual(bara.properties, barb.properties)
        self.assertEqual(bara.propcomments, barb.propcomments)
        self.assertEqual(bara.hidden, barb.hidden)

    def testReadOnStartup(self):
        test = pyproperties.Properties("./data/properties/bar.properties")
        keys =  [
                "alert",
                "message.0",
                "message.1",
                "name.0",
                "name.1",
                "name.2",
                ]
        self.assertEqual(test.path, "./data/properties/bar.properties")
        self.assertEqual(test.keys(), keys)

    def testReadAfterStartupWithPathGivenAtStartup(self):
        test = pyproperties.Properties("./data/properties/bar.properties", no_read=True)
        keys =  [
                "alert",
                "message.0",
                "message.1",
                "name.0",
                "name.1",
                "name.2",
                ]
        test.read()
        self.assertEqual(test.path, "./data/properties/bar.properties")
        self.assertEqual(test.keys(), keys)

    def testReadAfterStartupWithPathGivenAtRead(self):
        test = pyproperties.Properties()
        keys =  [
                "alert",
                "message.0",
                "message.1",
                "name.0",
                "name.1",
                "name.2",
                ]
        test.read("./data/properties/bar.properties")
        self.assertEqual(test.path, "./data/properties/bar.properties")
        self.assertEqual(test.keys(), keys)
    
    def testReadFromPassedReader(self):
        reader = pyproperties.Reader("./data/properties/bar.properties")
        reader.read()
        test = pyproperties.Properties(reader)
        keys =  [
                "alert",
                "message.0",
                "message.1",
                "name.0",
                "name.1",
                "name.2",
                ]
        self.assertEqual(test.path, os.path.abspath("./data/properties/bar.properties"))
        self.assertEqual(test.keys(), keys)


class KeyAndValuesGetterTest(unittest.TestCase):
    def testGetKeysOf(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        self.assertEqual(["literal.string.0", "literal.string.1"], sorted(foo.getkeysof("Hello World!")))
    
    def testKeys(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")        
        self.assertEqual(["bar", "foo"], foo.keys())

    def testKeysHidden(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        foo.hide("foo")
        
        self.assertEqual(["bar"], foo.keys())
        self.assertEqual(["bar", "foo"], foo.keys(hidden=True))
    
    def testValuesGetter(self):
        foo = pyproperties.Properties()
        foo.set("foo", "Foo")
        foo.set("bar", "Bar")
        self.assertListEqual(["Bar", "Foo"], foo.values())

    def testValuesGetterWithHiddenProperties(self):
        foo = pyproperties.Properties()
        foo.set("foo", "Foo")
        foo.set("bar", "Bar")
        foo.hide("foo")
        
        self.assertEqual(["Bar"], foo.values())
        self.assertListEqual(["Bar", "Foo"], foo.values(hidden=True))


class GetterTest(unittest.TestCase):
    def testGet(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual("Agent Smith", foo.get("customer.1.name"))

    def testGetException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(KeyError, foo.get, "foo")

    def testGetCastedInteger(self):
        foo = pyproperties.Properties()
        foo.set("two", "2")
        self.assertEqual(2, foo.get("two", cast=True))

    def testGetCastedFloat(self):
        foo = pyproperties.Properties()
        foo.set("pi", "3.14")
        self.assertEqual(3.14, foo.get("pi", cast=True))

    def testGetCastedNegativeInteger(self):
        foo = pyproperties.Properties()
        foo.set("two", "-2")
        self.assertEqual(-2, foo.get("two", cast=True))

    def testGetCastedNegativeFloat(self):
        foo = pyproperties.Properties()
        foo.set("neg_pi", "-3.14")
        self.assertEqual(-3.14, foo.get("neg_pi", cast=True))

    def testGetCastedNone(self):
        foo = pyproperties.Properties()
        foo.set("foo", "None")
        self.assertEqual(None, foo.get("foo", cast=True))

    def testGetCastedBooleanTrue(self):
        foo = pyproperties.Properties()
        foo.set("foo", "True")
        self.assertEqual(True, foo.get("foo", cast=True))

    def testGetCastedBooleanFalse(self):
        foo = pyproperties.Properties()
        foo.set("foo", "False")
        self.assertEqual(False, foo.get("foo", cast=True))

    def testGets(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual([("customer.0.name", "John the Average."), ("customer.1.name", "Agent Smith")], sorted(foo.gets("customer.*.name")))

    def testGetsCasted(self):
        foo = pyproperties.Properties()
        foo.set("stuff.0", "6.02e+23")
        foo.set("stuff.1", "5")
        foo.set("stuff.2", "None")
        foo.set("stuff.3", "True")
        props = [
                ("stuff.0", 6.02e+23), 
                ("stuff.1", 5),
                ("stuff.2", None),
                ("stuff.3", True),
                ]
        self.assertEqual(props, sorted(foo.gets("stuff.*", cast=True)))

    def testGetsParsed(self):
        foo = pyproperties.Properties()
        foo.set("hello", "Hello")
        foo.set("world", "World")
        foo.set("greeting.0", "$(hello) $(world)!")
        foo.set("greeting.1", "$(hello) cruel $(world)!")
        props = [
                ("greeting.0", "Hello World!"), 
                ("greeting.1", "Hello cruel World!"),
                ]
        self.assertEqual(props, sorted(foo.gets("greeting.*", parse=True)))

    def testGetsException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.gets, 0)


class SetterTest(unittest.TestCase):
    def testSet(self):
        keys =  [
                "foo.0",
                "foo.1",
                "foo.2",
                "foo.3",
                ]
        foo = pyproperties.Properties()
        for i in range(4): foo.set("foo.{0}".format(i))
        self.assertEqual(keys, foo.keys())

    def testSetRaisesErrorWhenKeyContainsSpace(self):
        foo = pyproperties.Properties()
        self.assertRaises(TypeError, foo.set, "some key")

    def testSets(self):
        contents =  [
                    ("foo.0", "0"),
                    ("foo.1", "1"),
                    ("foo.2", "2"),
                    ("foo.3", "3"),
                    ]
        foo = pyproperties.Properties()
        for i in range(4): foo.set("foo.{0}".format(i))
        foo.sets("foo.*", "0", "1", "2", "3")
        for key, value in contents:
            self.assertEqual(value, foo.get(key))


class RemoverTest(unittest.TestCase):
    def testRemove(self):
        foo = pyproperties.Properties()
        foo.set("foo.0")
        foo.set("foo.1")
        foo.set("foo.2")
        foo.set("foo.3")
        foo.remove("foo.0")
        self.assertEqual(["foo.1", "foo.2", "foo.3"], foo.keys())

    def testRemoves(self):
        foo = pyproperties.Properties()
        foo.set("foo.0")
        foo.set("foo.1")
        foo.set("foo.2")
        foo.set("foo.3")
        foo.set("bar.0")
        foo.removes("foo.*")
        self.assertEqual(["bar.0"], foo.keys())


class PopperTest(unittest.TestCase):
    def testPop(self):
        foo = pyproperties.Properties()
        foo.set("foo.0")
        foo.set("foo.1")
        foo.set("foo.2")
        foo.set("foo.3")
        self.assertEqual("", foo.pop("foo.0"))
        self.assertEqual(["foo.1", "foo.2", "foo.3"], foo.keys())

    def testPops(self):
        foo = pyproperties.Properties()
        foo.set("foo.0")
        foo.set("foo.1")
        foo.set("foo.2")
        foo.set("foo.3")
        foo.set("bar.0")
        props = [
                ("foo.0", ""),
                ("foo.1", ""),
                ("foo.2", ""),
                ("foo.3", ""),
                ]
        self.assertEqual(props, sorted(foo.pops("foo.*")))
        self.assertEqual(["bar.0"], foo.keys())

    def testPopsCasted(self):
        foo = pyproperties.Properties()
        foo.set("foo.0", "0")
        foo.set("foo.1", "3.14")
        foo.set("foo.2", "None")
        foo.set("foo.3", "True")
        foo.set("bar.0")
        props = [
                ("foo.0", 0),
                ("foo.1", 3.14),
                ("foo.2", None),
                ("foo.3", True),
                ]
        self.assertEqual(props, sorted(foo.pops("foo.*", cast=True)))
        self.assertEqual(["bar.0"], foo.keys())


class GroupingTest(unittest.TestCase):
    def testGetGroups(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        groups = [  "customer.*.name",
                    "customer.*.phone_number.*",
                    "customer.*.address",
                    "customer.*.postal_code",
                    "literal.string.*",
                    "numeral.float.*",
                    "foo.*.fame",
                    "foo.*.money",
                    "foo.*.power",
                    ]
        self.assertListEqual(sorted(groups), sorted(foo.getgroups()))


    def testGetGroupsHexadecimalSeprated(self):
        foo = pyproperties.Properties()
        groups =    [
                    "customer.*.name",
                    "customer.*.phone_number",
                    "customer.*.address",
                    "customer.*.postal_code",
                    ]
        for i in range(9, 20):
            foo.set("customer.{0}.name".format(hex(i)), ""),
            foo.set("customer.{0}.phone_number".format(hex(i)), "")
            foo.set("customer.{0}.address".format(hex(i)), "")
            foo.set("customer.{0}.postal_code".format(hex(i)), "")
        self.assertListEqual(sorted(groups), sorted(foo.getgroups()))


    def testGetSingles(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        singles = [ "numeral.pi",
                    "numeral.int",
                    "person.name",
                    "person.surname",
                    ]
        self.assertListEqual(sorted(singles), sorted(foo.getsingles()))


class CopyTest(unittest.TestCase):
    def testEquality(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        self.assertEqual(foo.origin_source, foo2.origin_source)
        self.assertEqual(foo.source, foo2.source)
        self.assertEqual(foo.origin_properties, foo2.origin_properties)
        self.assertEqual(foo.properties, foo2.properties)
        self.assertEqual(foo.propcomments, foo2.propcomments)


    def testDiversity(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        foo.set("test", True)
        self.assertNotEqual(foo.properties, foo2.properties)


class CompleteTest(unittest.TestCase):
    def testCompleteSimple(self):
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo_completed = {
                        "prop.0":"0",
                        "prop.1":"1",
                        "prop.2":"2",
                        "prop.3":"0x3",
                        "prop.4":"0x4",
                        }
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.set("prop.2", "2")
        foo.save()
        bar.set("prop.2", "0x2")
        bar.set("prop.3", "0x3")
        bar.set("prop.4", "0x4")
        bar.save()
        foo.complete(bar)
        self.assertEqual(foo_completed, foo.properties)
        self.assertNotEqual(foo_completed, foo.origin_properties)
        foo.save()
        self.assertEqual(foo_completed, foo.origin_properties)


    def testCompleteWithComments(self):
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo_completed = {
                        "prop.0":"0",
                        "prop.1":"1",
                        "prop.2":"0x2",
                        }
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.save()
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.comment("prop.2", "this is a comment")
        bar.save()
        foo.complete(bar)
        self.assertEqual(foo_completed, foo.properties)
        self.assertEqual({"prop.2":"this is a comment"}, foo.propcomments)
        self.assertNotEqual(foo_completed, foo.origin_properties)
        self.assertNotEqual({"prop.2":"this is a comment"}, foo.origin_propcomments)
        foo.save()
        self.assertEqual(foo_completed, foo.origin_properties)
    
    
    def testCompleteWithCommentedNotAppend(self):
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo_completed = {
                        "prop.0":"0",
                        "prop.1":"1",
                        "prop.2":"0x2",
                        }
        foo_hidden = []
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.save()
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.hide("prop.1")
        bar.save()
        foo.complete(bar)
        self.assertEqual(foo_completed, foo.properties)
        self.assertEqual(foo_hidden, foo.hidden)


    def testCompleteWithCommentedAppend(self):
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo_completed = {
                        "prop.0":"0",
                        "prop.1":"1",
                        "prop.2":"0x2",
                        }
        foo_hidden = ["prop.2"]
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.save()
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.hide("prop.2")
        bar.save()
        foo.complete(bar)
        self.assertEqual(foo_completed, foo.properties)
        self.assertEqual(foo_hidden, foo.hidden)


class UpdateTest(unittest.TestCase):
    def testUpdateSimple(self):
        supposed =  {
                    "prop.0":"0",
                    "prop.1":"0x1",
                    "prop.2":"0x2",
                    }
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.set("prop.2", "2")
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        foo.save()
        bar.save()
        foo.update(bar)
        self.assertEqual(supposed, foo.properties)
        self.assertNotEqual(supposed, foo.origin_properties)
        foo.save()
        self.assertEqual(supposed, foo.origin_properties)


    def testUpdateWithComments(self):
        props = {
                "prop.0":"0",
                "prop.1":"0x1",
                }
        comments_bu =   {
                        "prop.1":"this is original comment",
                        }
        comments_au =   {
                        "prop.1":"this is updated comment",
                        }
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.comment("prop.1", "this is original comment")
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.comment("prop.1", "this is updated comment")
        foo.save()
        bar.save()
        foo.update(bar)
        self.assertEqual(props, foo.properties)
        self.assertEqual(comments_au, foo.propcomments)
        self.assertEqual(comments_bu, foo.origin_propcomments)
        self.assertNotEqual(props, foo.origin_properties)
        self.assertNotEqual(comments_au, foo.origin_propcomments)
        foo.save()
        self.assertEqual(props, foo.origin_properties)
        self.assertEqual(comments_au, foo.origin_propcomments)


    def testUpdateWithCommented(self):
        props = {
                "prop.0":"0",
                "prop.1":"0x1",
                }
        hidden_bu = []
        hidden_au = ["prop.1"]
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.hide("prop.1")
        foo.save()
        bar.save()
        foo.update(bar)
        self.assertEqual(props, foo.properties)
        self.assertEqual(hidden_au, foo.hidden)
        self.assertEqual(hidden_bu, foo.origin_hidden)
        self.assertNotEqual(props, foo.origin_properties)
        self.assertNotEqual(hidden_au, foo.origin_hidden)
        foo.save()
        self.assertEqual(props, foo.origin_properties)
        self.assertEqual(hidden_au, foo.origin_hidden)


class MergeTest(unittest.TestCase):
    def testMergeSimple(self):
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        props = {
                "prop.0":"0",
                "prop.1":"1",
                "prop.2":"0x2",
                "prop.3":"0x3",
                }
        comments =  {
                    "prop.0":"this is a comment",
                    "prop.3":"this is another comment",
                    }
        hidden = ["prop.0", "prop.3"]
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.set("prop.2", "2")
        foo.comment("prop.0", "this is a comment")
        foo.hide("prop.0")
        foo.save()
        bar.set("prop.2", "0x2")
        bar.set("prop.3", "0x3")
        bar.comment("prop.3", "this is another comment")
        bar.hide("prop.3")
        bar.save()
        foo.merge(bar)
        foo.save()
        self.assertEqual(props, foo.properties)
        self.assertEqual(comments, foo.propcomments)
        self.assertEqual(hidden, foo.hidden)


class JoinTest(unittest.TestCase):
    def testJoinSimple(self):
        foo = pyproperties.Properties("./data/properties/include_test/foo.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined.properties")
        foo.join("./data/properties/include_test/bar.properties", prefix="")
        foo.save()
        self.assertEqual(combined.properties, foo.properties)
        self.assertEqual(combined.propcomments, foo.propcomments)
        self.assertEqual(combined.hidden, foo.hidden)
        fwriter = pyproperties.Writer(foo)
        cwriter = pyproperties.Writer(combined)
        fwriter.store(no_dump=True)
        cwriter.store(no_dump=True)
        self.assertEqual(cwriter.lines, fwriter.lines)


class ReloadTest(unittest.TestCase):
    def testReload(self):
        foo0 = pyproperties.Properties(foo_path)
        foo1 = foo0.copy()
        self.assertEqual(foo0.properties, foo1.properties)
        self.assertEqual(foo0.origin_properties, foo1.origin_properties)
        self.assertEqual(foo0.propcomments, foo1.propcomments)
        self.assertEqual(foo0.origin_propcomments, foo1.origin_propcomments)
        self.assertEqual(foo0.hidden, foo1.hidden)
        self.assertEqual(foo0.origin_hidden, foo1.origin_hidden)
        foo1.set("some.key", "value")
        foo1.removes("customer.0.*")
        foo1.hides("customer.1.*")
        foo1.unhide("customer.1.name")
        foo1.unhide("customer.1.address")
        foo1.save()
        self.assertNotEqual(foo0.properties, foo1.properties)
        self.assertNotEqual(foo0.origin_properties, foo1.origin_properties)
        self.assertNotEqual(foo0.propcomments, foo1.propcomments)
        self.assertNotEqual(foo0.origin_propcomments, foo1.origin_propcomments)
        self.assertNotEqual(foo0.hidden, foo1.hidden)
        self.assertNotEqual(foo0.origin_hidden, foo1.origin_hidden)
        foo1.reload()
        foo1.save()
        self.assertEqual(foo0.properties, foo1.properties)
        self.assertEqual(foo0.origin_properties, foo1.origin_properties)
        self.assertEqual(foo0.propcomments, foo1.propcomments)
        self.assertEqual(foo0.origin_propcomments, foo1.origin_propcomments)
        self.assertEqual(foo0.hidden, foo1.hidden)
        self.assertEqual(foo0.origin_hidden, foo1.origin_hidden)


class SaveTest(unittest.TestCase):
    def testSaveProperties(self):
        foo_saved = {"prop.0":"0", "prop.1":"1"}
        foo = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        self.assertEqual(foo_saved, foo.properties)
        self.assertNotEqual(foo_saved, foo.origin_properties)
        foo.save()
        self.assertEqual(foo_saved, foo.origin_properties)

    def testSaveComments(self):
        comments = {"foo":"comment"}
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.comment("foo", "comment")
        self.assertEqual(comments, foo.propcomments)
        self.assertNotEqual(comments, foo.origin_propcomments)
        foo.save()
        self.assertEqual(comments, foo.origin_propcomments)

    def testSaveHidden(self):
        hidden = ["foo"]
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        foo.hide("foo")
        self.assertEqual(hidden, foo.hidden)
        self.assertNotEqual(hidden, foo.origin_hidden)
        foo.save()
        self.assertEqual(hidden, foo.origin_hidden)

    def testSaveIncludes(self):
        includes =  [
                    ("./data/properties/include_test/test.properties", "", False),
                    ("./data/properties/include_test/test.properties", "foo", False),
                    ("./data/properties/include_test/test.properties", "", True),
                    ("./data/properties/include_test/test.properties", "foo", True),
                    ]
        foo = pyproperties.Properties()
        foo.addinclude("./data/properties/include_test/test.properties")
        foo.addinclude("./data/properties/include_test/test.properties", prefix="foo")
        foo.addinclude("./data/properties/include_test/test.properties", hidden=True)
        foo.addinclude("./data/properties/include_test/test.properties", prefix="foo", hidden=True)
        self.assertEqual(includes, foo._includes)
        self.assertNotEqual(includes, foo._origin_includes)
        foo.save()
        self.assertEqual(includes, foo._origin_includes)


class RevertTest(unittest.TestCase):
    def testRevertProperties(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        self.assertEqual({"foo":"", "bar":""}, foo.properties)
        foo.revert()
        self.assertEqual({}, foo.properties)

    def testRevertComments(self):
        comments = {"foo":"test"}
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.comment("foo", "test")
        self.assertEqual(comments, foo.propcomments)
        foo.revert()
        self.assertEqual({}, foo.propcomments)

    def testRevertHidden(self):
        hidden = ["foo"]
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        foo.hide("foo")
        self.assertEqual(hidden, foo.hidden)
        foo.revert()
        self.assertEqual([], foo.hidden)

    def testRevertIncludes(self):
        includes =  [
                    ("./data/properties/include_test/test.properties", "", False),
                    ("./data/properties/include_test/test.properties", "foo", False),
                    ("./data/properties/include_test/test.properties", "", True),
                    ("./data/properties/include_test/test.properties", "foo", True),
                    ]
        foo = pyproperties.Properties()
        foo.addinclude("./data/properties/include_test/test.properties")
        foo.addinclude("./data/properties/include_test/test.properties", prefix="foo")
        foo.addinclude("./data/properties/include_test/test.properties", hidden=True)
        foo.addinclude("./data/properties/include_test/test.properties", prefix="foo", hidden=True)
        self.assertEqual(includes, foo._includes)
        foo.revert()
        self.assertEqual([], foo._includes)


class CommentTest(unittest.TestCase):
    def testAddcommentTestSimpleString(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.comment("foo", "first part")
        self.assertEqual("first part", foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.comment, "bar", "")

    def testAddcommentTestStringWithNewlines(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.comment("foo", "this\nis\na\ncomment")
        self.assertEqual("this\nis\na\ncomment", foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.comment, "bar", "")

    def testGetcomment(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        foo.comment("foo", "this\nis\na\ncomment")
        self.assertEqual(["this", "is", "a", "comment"], foo.getcomment("foo", lines=True))
        self.assertEqual("this\nis\na\ncomment", foo.getcomment("foo"))
        self.assertEqual([], foo.getcomment("bar", lines=True))
        self.assertEqual("", foo.getcomment("bar"))


class HideTest(unittest.TestCase):
    def testHide(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.hide("foo")
        self.assertEqual(["foo"], foo.hidden)
        self.assertRaises(KeyError, foo.get, "foo")
        self.assertRaises(KeyError, foo.hide, "bar")


    def testHides(self):
        foo = pyproperties.Properties()
        foo.set("foo.0", "")
        foo.set("foo.1", "")
        foo.set("bar.0", "")
        foo.hides("foo.*")
        self.assertEqual(["foo.0", "foo.1"], foo.hidden)
        self.assertRaises(KeyError, foo.get, "foo.0")
        self.assertRaises(KeyError, foo.get, "foo.1")


    def testUnhide(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.hide("foo")
        self.assertEqual(["foo"], foo.hidden)
        self.assertRaises(KeyError, foo.get, "foo")
        foo.unhide("foo")
        self.assertEqual([], foo.hidden)


    def testUnhides(self):
        foo = pyproperties.Properties()
        foo.set("foo.0", "")
        foo.set("foo.1", "")
        foo.set("bar.0", "")
        foo.hides("foo.*")
        self.assertEqual(["foo.0", "foo.1"], foo.hidden)
        self.assertRaises(KeyError, foo.get, "foo.0")
        self.assertRaises(KeyError, foo.get, "foo.1")
        foo.unhides("foo.*")
        self.assertEqual([], foo.hidden)


if __name__ == "__main__" : unittest.main()
