#!/usr/bin/python3

from modules import pyproperties
import unittest

#
#   this module is used for testing
#

print( pyproperties.__version__ )

foo = pyproperties.Properties( "./data/properties/foo.properties" )
bar = pyproperties.Properties( "./data/properties/bar.properties" )
foo.complete( bar )
foo.merge( bar )

foo_parsed = {  "message.0":"Apple Jack.",
                "message.1":"Arr... Hello, John the Average!",
                "name.0":"John the Average",
                "name.1":"Jack"}

foo_names = ["message.0", "message.1", "name.0", "name.1"]


class ParseTest( unittest.TestCase ):
    def test_parse(self):
        """
        parse should return properly parsed dict.
        """
        self.assertEqual( foo_parsed, foo.parse() )


class MergeTest( unittest.TestCase ):
    def test_merge(self):
        """
        merge should replace properties values, but not add any new value. 
        """
        #  TODO


class GetterTest( unittest.TestCase ):
    def test_get_parsed(self):
        """
        should return properly parsed line containg reference
        """
        self.assertEqual( "Apple Jack.", foo.get( "message.0", True ) )


    def test_get_not_parsed(self):
        """
        should return a not-parsed line
        """
        self.assertEqual( "Apple $(name.1).", foo.get( "message.0", False ) )


    def test_gets_parsed(self):
        """
        gets should return a dict of properly parsed values
        """
        self.assertEqual( {"message.0":"Apple Jack.", "message.1":"Arr... Hello, John the Average!"}, foo.gets( "message.*", True ) )


    def test_gets_not_parsed(self):
        """
        gets should return a dict of not-parsed values
        """
        self.assertEqual( {"message.0":"Apple $(name.1).", "message.1":"Arr... Hello, $(name.0)!"}, foo.gets( "message.*" ) )


    def test_getnames(self):
        """
        getnames should return list of all names in dict.
        """
        self.assertEqual( foo_names, foo.getnames() )


if __name__ == '__main__':
    unittest.main()
