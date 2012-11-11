VERSION = 0.1.5
TAGNAME = pyproperties-$(VERSION)

.PHONY: doc release test tar

doc:
	pydoc3 ./modules/pyproperties.py > DOC

tar:
	tar --xz -cvf ./archives/$(TAGNAME).tar.xz DOC LICENSE README RELEASE Changelog.md test.py modules/pyproperties.py data/* manual/*

release: test doc tar

test:
	python3 ./test.py -v
