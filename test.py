#!/usr/bin/python3

import unittest
from modules import pyproperties
properties = pyproperties.Properties


class Test_getkeysof( unittest.TestCase ):
    def test_getkeysof_0(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( ["literal.string.0", "literal.string.1"], sorted( foo.getkeysof( "Hello World!" ) ) )

    def test_getkeysof_1(self):
        foo = properties( "./data/properties/foo.properties" )
        self.assertEqual( ["numeral.float.1"], sorted( foo.getkeysof( ".14" ) ) )


class Test_getnames( unittest.TestCase ):
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

class Test_getgroups( unittest.TestCase ):
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


class Test_getsingles( unittest.TestCase ):
    def test_getsingles(self):
        foo = properties( "./data/properties/foo.properties" )
        singles = [ "numeral.pi",
                    "numeral.int",
                    "person.name",
                    "person.surname",
                    ]
        self.assertEqual( sorted(singles), sorted(foo.getsingles()) )


if __name__ == "__main__" :
    unittest.main()