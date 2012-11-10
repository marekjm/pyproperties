#!/usr/bin/python3

import unittest
import re

from modules import pyproperties

foo_path = "./data/properties/foo.properties"

class ParselineTest(unittest.TestCase):
    def test_parselineInteger(self):
        foo = pyproperties.Properties()
        foo.set("two.0", 2)
        foo.set("two.1", "2")
        self.assertEqual(2, foo.get("two.0", parsed=True, cast=True))
        self.assertEqual(2, foo.get("two.0", parsed=True, cast=False))
        self.assertEqual(2, foo.get("two.1", parsed=True, cast=True))
        self.assertEqual("2", foo.get("two.1", parsed=True, cast=False))


    def test_parselineFloat(self):
        foo = pyproperties.Properties()
        foo.set("pi.0", 3.14)
        foo.set("pi.1", "3.14")
        self.assertEqual(3.14, foo.get("pi.0", parsed=True, cast=True))
        self.assertEqual(3.14, foo.get("pi.0", parsed=True, cast=False))
        self.assertEqual(3.14, foo.get("pi.1", parsed=True, cast=True))
        self.assertEqual("3.14", foo.get("pi.1", parsed=True, cast=False))


    def test_parselineString(self):
        foo = pyproperties.Properties()
        foo.set("greeting", "Hello $(name)!")
        foo.set("name", "World")
        self.assertEqual("Hello World!", foo.get("greeting", parsed=True, cast=True))
        self.assertEqual("Hello World!", foo.get("greeting", parsed=True, cast=False))


class LoadTest(unittest.TestCase):
    def testSpaces(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                }
        loaded = pyproperties.Properties("./data/properties/bar.properties")
        self.assertEqual(props, loaded.gets("*"))


    def testColonSeparated(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                }
        loaded = pyproperties.Properties("./data/properties/bar.properties")
        self.assertEqual(props, loaded.gets("*"))


    def testComments(self):
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
        self.assertEqual(comments, loaded.propcomments)
        self.assertEqual(src, loaded.source)


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
    def test_parseDict(self):
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


    def test_parseProps(self):
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
    def test_equality(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        self.assertEqual(foo.srcorigin, foo2.srcorigin)
        self.assertEqual(foo.source, foo2.source)
        self.assertEqual(foo.propsorigin, foo2.propsorigin)
        self.assertEqual(foo.properties, foo2.properties)
        self.assertEqual(foo.propcomments, foo2.propcomments)


    def test_diversity(self):
        foo = pyproperties.Properties(foo_path)
        foo2 = foo.copy()
        foo.set("test", True)
        self.assertNotEqual(foo.properties, foo2.properties)


class StoreTest(unittest.TestCase):
    def test_raisesUnsavedChangesError(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        self.assertRaises(pyproperties.UnsavedChangesError, foo.store, "")


    def test_raisesStoreErrorWhenNoPathGiven(self):
        foo = pyproperties.Properties()
        foo.set("foo", "bar")
        foo.save()
        self.assertRaises(pyproperties.StoreError, foo.store, "")


    def test_store(self):
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


    def test_storeChangedComments(self):
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


class CommentTest(unittest.TestCase):
    def test_addcomment(self):
        foo = pyproperties.Properties()
        foo.set("foo", "foo")
        foo.addcomment2("foo", "first", "part")
        self.assertEqual(["#   first", "#   part"], foo.propcomments["foo"])


if __name__ == "__main__" : unittest.main()