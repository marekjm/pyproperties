#!/usr/bin/env python3

import unittest
import re

from modules import pyproperties

foo_path = "./data/properties/foo.properties"

class ParselineTest(unittest.TestCase):
    def testParselineInteger(self):
        foo = pyproperties.Properties()
        foo.set("two.0", 2)
        foo.set("two.1", "2")
        self.assertEqual(2, foo.get("two.0", parsed=True, cast=True))
        self.assertEqual(2, foo.get("two.0", parsed=True, cast=False))
        self.assertEqual(2, foo.get("two.1", parsed=True, cast=True))
        self.assertEqual("2", foo.get("two.1", parsed=True, cast=False))


    def testParselineFloat(self):
        foo = pyproperties.Properties()
        foo.set("pi.0", 3.14)
        foo.set("pi.1", "3.14")
        self.assertEqual(3.14, foo.get("pi.0", parsed=True, cast=True))
        self.assertEqual(3.14, foo.get("pi.0", parsed=True, cast=False))
        self.assertEqual(3.14, foo.get("pi.1", parsed=True, cast=True))
        self.assertEqual("3.14", foo.get("pi.1", parsed=True, cast=False))


    def testParselineString(self):
        foo = pyproperties.Properties()
        foo.set("greeting", "Hello $(name)!")
        foo.set("name", "World")
        self.assertEqual("Hello World!", foo.get("greeting", parsed=True, cast=True))
        self.assertEqual("Hello World!", foo.get("greeting", parsed=True, cast=False))


class LoadTest(unittest.TestCase):
    def testLoad(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                }
        comments = {"message.0":["#   This is a comment for massage.0"], 
                    "name.0":["#   This is a comment for name.0 which", "#   value is \"John the Average\""],
                    }
        src = [ "#   second simple properties file",
                "#   used for testing properties.py module",
                "",
                "message.0=Apple $(name.1).",
                "message.1=  Arr... Welcome, $(name.0)!",
                "name.0 :John the Average",
                "name.1 : Jack  ",
                "name.2 :\  William  ",
                "alert=Fire!"
                ]
        loaded = pyproperties.Properties("./data/properties/bar.properties")
        self.assertEqual(props, loaded.properties)
        self.assertEqual(comments, loaded.propcomments)
        self.assertEqual(src, loaded.source)


    def testLoadCommented(self):
        baz = pyproperties.Properties("./data/properties/baz.properties")
        src =   [
                "prop.0=Foo",
                "",
                "prop.1=Bar",
                "prop.2=Baz",
                ]
        propcomments = {"prop.0":["#   this is a comment"], "prop.1":["#   this is commented property"]}
        props = {
                "prop.0":"Foo",
                "prop.1":"Bar",
                "prop.2":"Baz",
                }
        self.assertEqual(propcomments, baz.propcomments)
        self.assertEqual(src, baz.source)
        self.assertEqual(props, baz.properties)
        self.assertEqual(["prop.1"], baz.commented)


    def testNoRead(self):
        loaded = pyproperties.Properties("./data/properties/bar.properties", no_read=True)
        self.assertEqual("./data/properties/bar.properties", loaded.path)
        self.assertEqual([], loaded.srcorigin)
        self.assertEqual([], loaded.source)
        self.assertEqual({}, loaded.propsorigin)
        self.assertEqual({}, loaded.properties)
        self.assertEqual({}, loaded.propcomments)


    def testDifferentReadCustoms(self):
        bara = pyproperties.Properties("./data/properties/bar.properties", no_read=True)
        barb = pyproperties.Properties()
        bara.read()
        barb.read("./data/properties/bar.properties")
        self.assertEqual(bara.srcorigin, barb.srcorigin)
        self.assertEqual(bara.source, barb.source)
        self.assertEqual(bara.propsorigin, barb.propsorigin)
        self.assertEqual(bara.properties, barb.properties)
        self.assertEqual(bara.propcomments, barb.propcomments)


class KeyGetterTest(unittest.TestCase):
    def testGetKeysOf(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        self.assertEqual(["literal.string.0", "literal.string.1"], sorted(foo.getkeysof("Hello World!")))


class NameGetterTest(unittest.TestCase):
    def testGetNames(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        names = ["numeral.float.0",
                "numeral.float.1",
                "numeral.pi",
                "numeral.int",
                "literal.string.0",
                "literal.string.1",
                "customer.0.name",
                "customer.0.phone_number.0",
                "customer.0.phone_number.1",
                "customer.0.address",
                "customer.0.postal_code",
                "customer.1.name",
                "customer.1.phone_number.0",
                "customer.1.address",
                "customer.1.postal_code",
                "person.name",
                "person.surname",
                "foo.0.fame",
                "foo.0.money",
                "foo.0.power",
                "foo.1.fame",
                "foo.1.money",
                "foo.1.power",
                ]
        self.assertEqual(sorted(names), foo.getnames())


class GetTest(unittest.TestCase):
    def testGet(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual("Agent Smith", foo.get("customer.1.name"))


    def testGet_exception(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.get, 0)


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


class GetsTest(unittest.TestCase):
    def testGetsCustomerNames(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual({"customer.0.name":"John the Average.", "customer.1.name":"Agent Smith"}, foo.gets("customer.*.name"))


    def testGetsCustomerPhoneNumbers(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual({ "customer.0.phone_number.0":"+48 500666101", 
                            "customer.0.phone_number.1":"+48 678992005", 
                            "customer.1.phone_number.0":"-1 000-000-000"}, 
                            foo.gets("customer.*.phone_number.*"))


    def testGetsException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.gets, 0)


class GetreTest(unittest.TestCase):
    def testGetreString(self):
        foo = pyproperties.Properties(foo_path)
        props = {   "customer.0.phone_number.0": "+48 500666101",
                    "customer.0.phone_number.1": "+48 678992005",
                    "customer.1.phone_number.0": "-1 000-000-000",
                }
        self.assertEqual(props, foo.getre("^customer\.[0-9]+\.phone_number\.[0-9]+$"))


    def testGetrePattern(self):
        foo = pyproperties.Properties(foo_path)
        props = {   "customer.0.phone_number.0": "+48 500666101",
                    "customer.0.phone_number.1": "+48 678992005",
                    "customer.1.phone_number.0": "-1 000-000-000",
                }
        self.assertEqual(props, foo.getre(re.compile("^customer\.[0-9]+\.phone_number\.[0-9]+$")))


    def testGetreException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.getre, 0)


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


    def testGetSingles(self):
        foo = pyproperties.Properties("./data/properties/foo.properties")
        singles = [ "numeral.pi",
                    "numeral.int",
                    "person.name",
                    "person.surname",
                    ]
        self.assertListEqual(sorted(singles), sorted(foo.getsingles()))


class ParseTest(unittest.TestCase):
    def testParseDict(self):
        bar = pyproperties.Properties(foo_path.replace("foo", "bar"))
        parsed =    {
                    "message.0":"Apple Jack  .",
                    "message.1":"Arr... Welcome, John the Average!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                    }
        self.assertEqual(parsed, bar.parse())


    def testParseProps(self):
        bar = pyproperties.Properties(foo_path.replace("foo", "bar"))
        parsed =    {
                    "message.0":"Apple Jack  .",
                    "message.1":"Arr... Welcome, John the Average!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                    }
        pbar = bar.parse(props=True)
        self.assertEqual(parsed, pbar.gets("*"))
        self.assertEqual(pyproperties.Properties, type(pbar))


class CopyTest(unittest.TestCase):
    def testEquality(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        self.assertEqual(foo.srcorigin, foo2.srcorigin)
        self.assertEqual(foo.source, foo2.source)
        self.assertEqual(foo.propsorigin, foo2.propsorigin)
        self.assertEqual(foo.properties, foo2.properties)
        self.assertEqual(foo.propcomments, foo2.propcomments)


    def testDiversity(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        foo.set("test", True)
        self.assertNotEqual(foo.properties, foo2.properties)


class StoreTest(unittest.TestCase):
    def testRaisesUnsavedChangesError(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        self.assertRaises(pyproperties.UnsavedChangesError, foo.store, "")


    def testRaisesStoreErrorWhenNoPathGiven(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        foo.save()
        self.assertRaises(pyproperties.StoreError, foo.store, "")


    def testStore(self):
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
                    "name.2=  William  ",
                    "alert=Fire!",
                    ]
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreChangedComments(self):
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
                    "name.2=  William  ",
                    "alert=Fire!",
                    ]
        bar.addcomment("name.0", "This is changed comment for name.0")
        bar.save()
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)

    def testStoreCommented(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.set("foo", "Foo")
        foo.set("bar", "Bar")
        foo.save()
        foo.comment("foo")
        foo.addcomment("foo", "foo's comment")
        foo.addcomment("bar", "bar's comment")
        self.assertRaises(pyproperties.UnsavedChangesError, foo.store, "")
        foo.save()
        foo.store("", no_dump=True)
        lines = [
                "#   bar's comment",
                "bar=Bar",
                "#   foo's comment",
                "#foo=Foo",
                ]
        self.assertEqual(lines, foo.lines)


    def testStoreForced(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.set("some.prop", "some value")
        foo.set("other.prop", "other value")
        foo.save()
        foo.store(no_dump=True)
        self.assertEqual(["other.prop=other value", "some.prop=some value"], foo.lines)
        foo.set("another.prop", "another value")
        foo.store(no_dump=True, force=True)
        self.assertEqual(["other.prop=other value", "some.prop=some value"], foo.lines)


class AddcommentTest(unittest.TestCase):
    def testAddcommentTestSimpleString(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", "first part")
        self.assertEqual(["#   first part"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestStringWithNewlines(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", "this\nis\na\ncomment")
        self.assertEqual(["#   this", "#   is", "#   a", "#   comment"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestSimpleList(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", ["first", "part"])
        self.assertEqual(["#   first", "#   part"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestListWithNewlines(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", ["this\nis", "a\ncomment"])
        self.assertEqual(["#   this", "#   is", "#   a", "#   comment"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")
        
        
class GetcommentTest(unittest.TestCase):
    def testGetcomment(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", ["this\nis", "a\ncomment"])
        self.assertEqual(["#   this", "#   is", "#   a", "#   comment"], foo.getcomment("foo"))
        self.assertEqual([], foo.getcomment("bar"))


class CommentTest(unittest.TestCase):
    def testComment(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.comment("foo")
        self.assertEqual(["foo"], foo.commented)
        self.assertRaises(KeyError, foo.get, "foo")
        self.assertRaises(KeyError, foo.comment, "bar")


    def testComments(self):
        foo = pyproperties.Properties()
        foo.set("foo.0", "")
        foo.set("foo.1", "")
        foo.set("bar.0", "")
        foo.comments("foo.*")
        self.assertEqual(["foo.0", "foo.1"], foo.commented)
        self.assertRaises(KeyError, foo.get, "foo.0")
        self.assertRaises(KeyError, foo.get, "foo.1")


    def testUncomment(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.comment("foo")
        self.assertEqual(["foo"], foo.commented)
        self.assertRaises(KeyError, foo.get, "foo")
        foo.uncomment("foo")
        self.assertEqual([], foo.commented)


    def testUncomments(self):
        foo = pyproperties.Properties()
        foo = pyproperties.Properties()
        foo.set("foo.0", "")
        foo.set("foo.1", "")
        foo.set("bar.0", "")
        foo.comments("foo.*")
        self.assertEqual(["foo.0", "foo.1"], foo.commented)
        self.assertRaises(KeyError, foo.get, "foo.0")
        self.assertRaises(KeyError, foo.get, "foo.1")
        foo.uncomments("foo.*")
        self.assertEqual([], foo.commented)


if __name__ == "__main__" : unittest.main()