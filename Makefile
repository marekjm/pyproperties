VERSION = 0.2.2
TAGNAME = pyproperties-$(VERSION)

.PHONY: test release install uninstall

tar: DOC LICENSE README.md RELEASE.md Changelog.md test.py modules/pyproperties.py Makefile data/* manual/*
	tar --xz -cvf ./archives/$(TAGNAME).tar.xz DOC LICENSE README.md RELEASE.md Changelog.md test.py modules/pyproperties.py Makefile data/* manual/*.mdown

doc: ./modules/pyproperties.py
	pydoc3 ./modules/pyproperties.py > DOC

manual: ./manual/*.mdown
	pandoc -o ./manual/manual.pdf ./manual/*.mdown

test:
	python3 -m unittest --catch --failfast --verbose test.py

changelog: Changelog.mdown README.mdown RELEASE.mdown
	cp Changelog.mdown Changelog.md
	cp README.mdown README.md
	cp RELEASE.mdown RELEASE.md

release: test doc changelog tar

install:
	python3 ./modules/install.py

uninstall:
	python3 ./modules/uninstall.py
