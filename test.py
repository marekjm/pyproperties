#!/usr/bin/python3

import unittest
from modules import pyproperties
properties = pyproperties.Properties


foo = properties( "./data/properties/foo.properties" )
bar = properties( "./data/properties/bar.properties" )

class GetterTest( unittest.TestCase ):
    def test_get_parsed(self):
        self.assertEqual( "Yellow Jack.", foo.get( "message.0", True ) )


    def test_get_not_parsed(self):
        self.assertEqual( "Yellow $(name.1).", foo.get( "message.0" ) )


    def test_gets_parsed(self):
        self.assertEqual( {"message.0":"Yellow Jack.", "message.1":"Hello, John the Average!"}, foo.gets( "message.*", True ) )


    def test_gets_not_parsed(self):
        self.assertEqual( {"message.0":"Yellow $(name.1).", "message.1":"Hello, $(name.0)!"}, foo.gets( "message.*" ) )


class SetterTest( unittest.TestCase ):
    def test_set(self):
        foo.set( "message.0", "Yellow $(name.0)." )
        self.assertEqual( "Yellow $(name.0).", foo.get( "message.0" ) )


    def test_sets(self):
        foo.sets( "message.*", "Yellow $(name.0)." )
        self.assertEqual( {"message.0":"Yellow $(name.0).", "message.1":"Yellow $(name.0)."}, foo.gets( "message.*" ) )


class RemoverTest( unittest.TestCase ):
    def test_remove(self):
        foo.remove( "message.0" )
        self.assertRaises( KeyError, foo.get, "message.0" )
        foo.set( "message.0", "Yellow $(name.0)." )


    def test_removes(self):
        foo.removes( "message.*" )
        self.assertEqual( {}, foo.gets( "message.*" ) )
        foo.set( "message.0", "Yellow $(name.0)." )
        foo.set( "message.1", "Yellow $(name.0)." )


class PopperTest( unittest.TestCase ):
    def test_pop(self):
        self.assertEqual( "Yellow $(name.1).", foo.pop( "message.0" ) )
        foo.set( "message.0", "Yellow $(name.1)." )


    def test_pops(self):
        self.assertEqual( {"message.0":"Yellow $(name.1).", "message.1":"Hello, $(name.0)!"}, foo.pops( "message.*" ) )
        foo.set( "message.0", "Yellow $(name.0)." )
        foo.set( "message.1", "Hello, $(name.0)!" )


class ReloadTest( unittest.TestCase ):
    def test_reload(self):
        old_src = foo.source
        n = len( foo.source )
        foo.melt( bar )
        foo.reload()
        self.assertEqual( old_src[:n], foo.source )


if __name__ == "__main__" :
    unittest.main()