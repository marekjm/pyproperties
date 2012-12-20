#!/usr/bin/env python3

import unittest
import re

from modules import pyproperties

foo_path = "./data/properties/foo.properties"

class ValidatorsTest(unittest.TestCase):
    def testCommentlineValidator(self):
        foo = pyproperties.Properties()
        lines = [
                ("#some comment", True),
                ("#  text", True),
                ("#   string", True),
                ("#", True),
                ("# ", True),
                ("  # ", True),
                ("#maybe=property", True),
                ("not a comment", False),
                ("", False),
                ("  indent", False),
                ("  indented=property", False),
                ("  some#string", False),
                ]
        for line, result in lines: self.assertEqual(foo._iscommentline(line), result)
    
    def testHaskeyNonStrict(self):
        foo = pyproperties.Properties()
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
        for line, result in lines: self.assertEqual(foo._linehaskey(line, strict=False), result)


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
                ]
        for line, result in lines: self.assertEqual(foo._linehaskey(line), result)

    def testGetlinekeyNonStrict(self):
        foo = pyproperties.Properties()
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
        for line, result in lines: self.assertEqual(foo.getlinekey(line, strict=False), result)


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
        for line, result in lines: self.assertEqual(foo.getlinekey(line), result)

    def testGetlinevalueNonStrict(self):
        foo = pyproperties.Properties()
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
        for line, result in lines: self.assertEqual(foo.getlinevalue(line, strict=False), result)


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
        for line, result in lines: self.assertEqual(foo.getlinevalue(line, strict=True), result)


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


class LoadTest(unittest.TestCase):
    def testLoad(self):
        props = {
                    "message.0":"Apple $(name.1).",
                    "message.1":"Arr... Welcome, $(name.0)!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"\\  William  ",
                    "alert":"Fire!",
                }
        comments = {"message.0":["This is a comment for massage.0"], 
                    "name.0":["This is a comment for name.0 which", "value is \"John the Average\""],
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


    def testLoadHidden(self):
        baz = pyproperties.Properties("./data/properties/baz.properties")
        src =   [
                "prop.0=Foo",
                "",
                "prop.1=Bar",
                "prop.2=Baz",
                ]
        propcomments = {"prop.0":["this is a comment"], "prop.1":["this is commented property"]}
        props = {
                "prop.0":"Foo",
                "prop.1":"Bar",
                "prop.2":"Baz",
                }
        self.assertEqual(propcomments, baz.propcomments)
        self.assertEqual(src, baz.source)
        self.assertEqual(props, baz.properties)
        self.assertEqual(["prop.1"], baz.hidden)


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
        self.assertEqual(bara.hidden, barb.hidden)


class LoadIncludeTest(unittest.TestCase):
    def testIncludeSimple(self):
        test = pyproperties.Properties("./data/properties/include_test/test.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined.properties")

        self.assertEqual(test.source, combined.source)
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)


    def testIncludePrefixed(self):
        test = pyproperties.Properties("./data/properties/include_test/test.prefix.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined.prefix.properties")

        self.assertEqual(test.source, combined.source)
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)


    def testIncludeHidden(self):
        test = pyproperties.Properties("./data/properties/include_test/test.commented.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined.commented.properties")

        self.assertEqual(test.source, combined.source)
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)


    def testIncludeHiddenAndPrefixed(self):
        test = pyproperties.Properties("./data/properties/include_test/test.commented.prefix.properties")
        combined = pyproperties.Properties("./data/properties/include_test/combined.commented.prefix.properties")

        self.assertEqual(test.source, combined.source)
        self.assertEqual(test.properties, combined.properties)
        self.assertEqual(test.propcomments, combined.propcomments)
        self.assertEqual(test.hidden, combined.hidden)


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


class GetsTest(unittest.TestCase):
    def testGets(self):
        foo = pyproperties.Properties(foo_path)
        self.assertEqual({"customer.0.name":"John the Average.", "customer.1.name":"Agent Smith"}, foo.gets("customer.*.name"))


    def testGetsException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.gets, 0)


class GetreTest(unittest.TestCase):
    def testGetre(self):
        foo = pyproperties.Properties(foo_path)
        props = {   "customer.0.phone_number.0": "+48 500666101",
                    "customer.0.phone_number.1": "+48 678992005",
                    "customer.1.phone_number.0": "-1 000-000-000",
                }
        self.assertEqual(props, foo.getre("^customer\.[0-9]+\.phone_number\.[0-9]+$"))


    def testGetreException(self):
        foo = pyproperties.Properties(foo_path)
        self.assertRaises(TypeError, foo.getre, 0)


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
        self.assertEqual(keys, foo.getnames())


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
        self.assertEqual(["foo.1", "foo.2", "foo.3"], foo.getnames())

    def testRemoves(self):
        foo = pyproperties.Properties()
        foo.set("foo.0")
        foo.set("foo.1")
        foo.set("foo.2")
        foo.set("foo.3")
        foo.set("bar.0")
        foo.removes("foo.*")
        self.assertEqual(["bar.0"], foo.getnames())


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


class ParseTest(unittest.TestCase):
    def testParse(self):
        bar = pyproperties.Properties(foo_path.replace("foo", "bar"))
        parsed =    {
                    "message.0":"Apple Jack  .",
                    "message.1":"Arr... Welcome, John the Average!",
                    "name.0":"John the Average",
                    "name.1":"Jack  ",
                    "name.2":"\\  William  ",
                    "alert":"Fire!",
                    }
        pbar = bar.parse()
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
        self.assertNotEqual(foo_completed, foo.propsorigin)
        foo.save()
        self.assertEqual(foo_completed, foo.propsorigin)


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
        bar.addcomment("prop.2", "this is a comment")
        bar.save()
        foo.complete(bar)
        self.assertEqual(foo_completed, foo.properties)
        self.assertEqual({"prop.2":["this is a comment"]}, foo.propcomments)
        self.assertNotEqual(foo_completed, foo.propsorigin)
        self.assertNotEqual({"prop.2":["this is a comment"]}, foo.origin_propcomments)
        foo.save()
        self.assertEqual(foo_completed, foo.propsorigin)
    
    
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
        self.assertNotEqual(supposed, foo.propsorigin)
        foo.save()
        self.assertEqual(supposed, foo.propsorigin)


    def testUpdateWithComments(self):
        props = {
                "prop.0":"0",
                "prop.1":"0x1",
                }
        comments_bu =   {
                        "prop.1":["this is original comment"],
                        }
        comments_au =   {
                        "prop.1":["this is updated comment"],
                        }
        foo = pyproperties.Properties()
        bar = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.addcomment("prop.1", "this is original comment")
        bar.set("prop.1", "0x1")
        bar.set("prop.2", "0x2")
        bar.addcomment("prop.1", "this is updated comment")
        foo.save()
        bar.save()
        foo.update(bar)
        self.assertEqual(props, foo.properties)
        self.assertEqual(comments_au, foo.propcomments)
        self.assertEqual(comments_bu, foo.origin_propcomments)
        self.assertNotEqual(props, foo.propsorigin)
        self.assertNotEqual(comments_au, foo.origin_propcomments)
        foo.save()
        self.assertEqual(props, foo.propsorigin)
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
        self.assertNotEqual(props, foo.propsorigin)
        self.assertNotEqual(hidden_au, foo.origin_hidden)
        foo.save()
        self.assertEqual(props, foo.propsorigin)
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
                    "prop.0":["this is a comment"],
                    "prop.3":["this is another comment"],
                    }
        hidden = ["prop.0", "prop.3"]
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        foo.set("prop.2", "2")
        foo.addcomment("prop.0", "this is a comment")
        foo.hide("prop.0")
        foo.save()
        bar.set("prop.2", "0x2")
        bar.set("prop.3", "0x3")
        bar.addcomment("prop.3", "this is another comment")
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
        foo.store(no_dump=True)
        combined.store(no_dump=True)
        self.assertEqual(combined.lines, foo.lines)
        self.assertEqual(combined.properties, foo.properties)
        self.assertEqual(combined.propcomments, foo.propcomments)
        self.assertEqual(combined.hidden, foo.hidden)


class ReloadTest(unittest.TestCase):
    def testReload(self):
        foo0 = pyproperties.Properties(foo_path)
        foo1 = foo0.copy()
        self.assertEqual(foo0.properties, foo1.properties)
        self.assertEqual(foo0.propsorigin, foo1.propsorigin)
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
        self.assertNotEqual(foo0.propsorigin, foo1.propsorigin)
        self.assertNotEqual(foo0.propcomments, foo1.propcomments)
        self.assertNotEqual(foo0.origin_propcomments, foo1.origin_propcomments)
        self.assertNotEqual(foo0.hidden, foo1.hidden)
        self.assertNotEqual(foo0.origin_hidden, foo1.origin_hidden)
        foo1.reload()
        foo1.save()
        self.assertEqual(foo0.properties, foo1.properties)
        self.assertEqual(foo0.propsorigin, foo1.propsorigin)
        self.assertEqual(foo0.propcomments, foo1.propcomments)
        self.assertEqual(foo0.origin_propcomments, foo1.origin_propcomments)
        self.assertEqual(foo0.hidden, foo1.hidden)
        self.assertEqual(foo0.origin_hidden, foo1.origin_hidden)


class SaveTest(unittest.TestCase):
    def testSaveSimple(self):
        foo_saved = {"prop.0":"0", "prop.1":"1"}
        foo = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        self.assertEqual(foo_saved, foo.properties)
        self.assertNotEqual(foo_saved, foo.propsorigin)
        foo.save()
        self.assertEqual(foo_saved, foo.propsorigin)


class RevertTest(unittest.TestCase):
    def testRevertSimple(self):
        foo = pyproperties.Properties()
        foo.set("prop.0", "0")
        foo.set("prop.1", "1")
        self.assertEqual({"prop.0":"0", "prop.1":"1"}, foo.properties)
        foo.revert()
        self.assertEqual({}, foo.properties)


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


    def testStoreLoadedWithNoModifications(self):
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
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreLoadedSomeValuesRemoved(self):
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
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreLoadedEveryOriginalValueRemoved(self):
        bar = pyproperties.Properties("./data/properties/bar.properties")
        lines = [   "#   second simple properties file",
                    "#   used for testing properties.py module",
                    ]
        bar.removes("*")
        bar.save()
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreLoadedEveryOriginalPropertyRemovedAndNewPropertiesAdded(self):
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
        bar.addcomment("prop.1", "this is a comment for prop.1")
        bar.set("prop.2", "2")
        bar.hide("prop.2")
        bar.save()
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreLoadedAndCommented(self):
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
        bar.addcomment("name.2", "his name is William\nthat's for sure")
        bar.addcomment("name.1", "possibly Sparrow")
        bar.save()
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)


    def testStoreLoadedAndCommentsRemoved(self):
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
                    "name.2=\\  William  ",
                    "alert=Fire!",
                    ]
        bar.addcomment("name.0", "This is changed comment for name.0")
        bar.save()
        bar.store(path="./test.properties~", no_dump=True)
        self.assertEqual(lines, bar.lines)

    def testStoreCreatedFromBlankAndCommented(self):
        foo = pyproperties.Properties("foo.properties", no_read=True)
        foo.set("foo", "Foo")
        foo.set("bar", "Bar")
        foo.save()
        foo.hide("foo")
        self.assertRaises(KeyError, foo.addcomment, "foo", "foo's comment")
        foo.addcomment("bar", "bar's comment")
        self.assertRaises(pyproperties.UnsavedChangesError, foo.store, "")
        foo.save()
        foo.store(no_dump=True)
        lines = [
                "#   bar's comment",
                "bar=Bar",
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
        self.assertEqual(["first part"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestStringWithNewlines(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", "this\nis\na\ncomment")
        self.assertEqual(["this", "is", "a", "comment"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestSimpleList(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", ["first", "part"])
        self.assertEqual(["first", "part"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")


    def testAddcommentTestListWithNewlines(self):
        foo = pyproperties.Properties()
        foo.set("foo", "")
        foo.addcomment("foo", ["this\nis", "a\ncomment"])
        self.assertEqual(["this", "is", "a", "comment"], foo.propcomments["foo"])
        self.assertRaises(KeyError, foo.addcomment, "bar", "")
        
        
class GetcommentTest(unittest.TestCase):
    def testGetcomment(self):
        foo = pyproperties.Properties()
        foo.set("foo")
        foo.set("bar")
        foo.addcomment("foo", ["this\nis", "a\ncomment"])
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


class TypecastingTest(unittest.TestCase):
    def testHexadecimalConversion(self):
        examples = [("0x0", 0),
                    ("-0x1", -1),
                    ("0x16", 22),
                    ("-0xa2", -162),
                    ("0x45", 69),
                    ("29a", 666),
                    ("-0x7cb", -1995),
                    ("7dc", 2012),
                    ("0x22b8", 8888),
                    ("0x582", 1410),
                    ("-0x582", -1410),
                    ("0x75bcd15", 123456789),
                    ("-f44e", -62542),
                    ]
        foo = pyproperties.Properties()
        for hex, dec in examples:
            self.assertEqual(foo._convert(hex), dec)

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
        foo = pyproperties.Properties()
        for oct, dec in examples: 
            self.assertEqual(foo._convert(oct), dec)


if __name__ == "__main__" : unittest.main()