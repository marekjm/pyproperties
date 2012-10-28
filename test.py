#!/usr/bin/python3

import unittest
import re

from modules import pyproperties
properties = pyproperties.Properties


foo_path = "./data/properties/foo.properties"

class TestKeyGetter(unittest.TestCase):
    def test_getkeysof(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( ["literal.string.0", "literal.string.1"], sorted( foo.getkeysof( "Hello World!" ) ) )


class TestNameGetter(unittest.TestCase):
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
                ]
        self.assertEqual( sorted(names), foo.getnames() )


class TestGet(unittest.TestCase):
    def test_get(self):
        foo = pyproperties.Properties( foo_path )
        self.assertEqual( "Agent Smith", foo.get( "customer.1.name" ) )


    def test_get_exception(self):
        foo = pyproperties.Properties( foo_path )
        self.assertRaises( TypeError, foo.get, 0 )


class TestGets(unittest.TestCase):
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


class TestGetre(unittest.TestCase):
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


class TestGrouping( unittest.TestCase ):
    def test_getgroups(self):
        foo = properties( "./data/properties/foo.properties" )
        groups = [  "customer.*.name",
                    "customer.*.phone_number.*",
                    "customer.*.address",
                    "customer.*.postal_code",
                    "literal.string.*",
                    "numeral.float.*",
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


if __name__ == "__main__" :
    unittest.main()