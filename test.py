#!/usr/bin/python3

import unittest
import re

from modules import pyproperties
properties = pyproperties.Properties


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
    def test_spaces(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                }
        loaded = pyproperties.Properties("./data/properties/bar.properties")
        self.assertEqual( props, loaded.gets("*") )

    def test_colonSeparated(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                }
        loaded = pyproperties.Properties("./data/properties/bar.properties")
        self.assertEqual( props, loaded.gets("*") )


class KeyGetterTest(unittest.TestCase):
    def test_getkeysof(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( ["literal.string.0", "literal.string.1"], sorted( foo.getkeysof( "Hello World!" ) ) )


class NameGetterTest(unittest.TestCase):
    def test_getnames(self):
        foo = properties( "./data/properties/foo.properties" )
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
        self.assertEqual( sorted(names), foo.getnames() )


class GetTest(unittest.TestCase):
    def test_get(self):
        foo = pyproperties.Properties( foo_path )
        self.assertEqual( "Agent Smith", foo.get( "customer.1.name" ) )


    def test_get_exception(self):
        foo = pyproperties.Properties( foo_path )
        self.assertRaises( TypeError, foo.get, 0 )


    def test_getCastedInteger(self):
        foo = pyproperties.Properties()
        foo.set("two", "2")
        self.assertEqual(2, foo.get("two", cast=True))


    def test_getCastedFloat(self):
        foo = pyproperties.Properties()
        foo.set("pi", "3.14")
        self.assertEqual(3.14, foo.get("pi", cast=True))


    def test_getCastedNegativeInteger(self):
        foo = pyproperties.Properties()
        foo.set("two", "-2")
        self.assertEqual(-2, foo.get("two", cast=True))


    def test_getCastedNegativeFloat(self):
        foo = pyproperties.Properties()
        foo.set("neg_pi", "-3.14")
        self.assertEqual(-3.14, foo.get("neg_pi", cast=True))


class GetsTest(unittest.TestCase):
    def test_gets_customerNames(self):
        foo = pyproperties.Properties( foo_path )
        self.assertEqual( {"customer.0.name":"John the Average.", "customer.1.name":"Agent Smith"}, foo.gets( "customer.*.name" ) )


    def test_gets_customerPhoneNumbers(self):
        foo = pyproperties.Properties( foo_path )
        self.assertEqual( { "customer.0.phone_number.0":"+48 500666101", 
                            "customer.0.phone_number.1":"+48 678992005", 
                            "customer.1.phone_number.0":"-1 000-000-000"}, 
                            foo.gets( "customer.*.phone_number.*" ) )


    def test_gets_exception(self):
        foo = pyproperties.Properties( foo_path )
        self.assertRaises( TypeError, foo.gets, 0 )


class GetreTest(unittest.TestCase):
    def test_getre_string(self):
        foo = pyproperties.Properties( foo_path )
        props = {   "customer.0.phone_number.0": "+48 500666101",
                    "customer.0.phone_number.1": "+48 678992005",
                    "customer.1.phone_number.0": "-1 000-000-000",
                }
        self.assertEqual( props, foo.getre( "^customer\.[0-9]+\.phone_number\.[0-9]+$" ) )


    def test_getre_pattern(self):
        foo = pyproperties.Properties( foo_path )
        props = {   "customer.0.phone_number.0": "+48 500666101",
                    "customer.0.phone_number.1": "+48 678992005",
                    "customer.1.phone_number.0": "-1 000-000-000",
                }
        self.assertEqual( props, foo.getre( re.compile("^customer\.[0-9]+\.phone_number\.[0-9]+$") ) )


    def test_getre_exception(self):
        foo = pyproperties.Properties( foo_path )
        self.assertRaises( TypeError, foo.getre, 0 )


class GroupingTest(unittest.TestCase):
    def test_getgroups(self):
        foo = properties( "./data/properties/foo.properties" )
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
        self.assertListEqual( sorted(groups), sorted(foo.getgroups()) )


    def test_getsingles(self):
        foo = properties( "./data/properties/foo.properties" )
        singles = [ "numeral.pi",
                    "numeral.int",
                    "person.name",
                    "person.surname",
                    ]
        self.assertListEqual( sorted(singles), sorted(foo.getsingles()) )


class ParseTest(unittest.TestCase):
    def test_parseDict(self):
        bar = pyproperties.Properties( foo_path.replace("foo", "bar") )
        parsed =    {
                    "message.0":"Apple Jack  .",
                    "message.1":"Arr... Welcome, John the Average!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                    }
        self.assertEqual( parsed, bar.parse() )


    def test_parseProps(self):
        bar = pyproperties.Properties( foo_path.replace("foo", "bar") )
        parsed =    {
                    "message.0":"Apple Jack  .",
                    "message.1":"Arr... Welcome, John the Average!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"  William  ",
                    "alert":"Fire!",
                    }
        pbar = bar.parse(props=True)
        self.assertEqual( parsed, pbar.gets("*") )
        self.assertEqual( pyproperties.Properties, type(pbar) )


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


if __name__ == "__main__" : unittest.main()