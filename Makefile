VERSION = 0.2.3.1
TAGNAME = pyproperties-$(VERSION)

.PHONY: test release install uninstall

tar: DOC LICENSE README.mdown RELEASE.mdown Changelog.mdown test.py modules/pyproperties.py Makefile data/* manual/*
	tar --xz -cvf ./releases/$(TAGNAME).tar.xz DOC LICENSE README.mdown RELEASE.mdown Changelog.mdown test.py modules/pyproperties.py Makefile data/* manual/*.mdown

doc: ./modules/pyproperties.py
	pydoc3 ./modules/pyproperties.py > DOC

manual: ./manual/*.mdown
	pandoc -o ./manual/manual.pdf ./manual/*.mdown

test:
	python3 -m unittest --catch --failfast --verbose test.py

release: test doc tar

install:
	python3 ./modules/install.py

uninstall:
	python3 ./modules/uninstall.py
