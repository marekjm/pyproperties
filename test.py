#!/usr/bin/python3

import unittest
from modules import pyproperties
properties = pyproperties.Properties


class TestKeyGetter( unittest.TestCase ):
    def test_getkeysof(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( ["literal.string.0", "literal.string.1"], sorted( foo.getkeysof( "Hello World!" ) ) )

class TestNameGetter( unittest.TestCase ):
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
        self.assertEqual( sorted(groups), foo.getgroups() )

    def test_getsingles(self):
        foo = properties( "./data/properties/foo.properties" )
        singles = [ "numeral.pi",
                    "numeral.int",
                    "person.name",
                    "person.surname",
                    ]
        self.assertEqual( sorted(singles), sorted(foo.getsingles()) )


class TestStore(unittest.TestCase):
    def test_store(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( 1, 0 )


if __name__ == "__main__" :
    unittest.main()