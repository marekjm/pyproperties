VERSION = 0.3.0
OLD=0.2.6
TAGNAME = pyproperties-$(VERSION)

.PHONY: test release install uninstall manual

tar: DOC LICENSE README.mdown RELEASE.mdown Changelog.mdown tests/test.py modules/pyproperties.py Makefile data/* manual/*
	tar --xz -cvf ./releases/$(TAGNAME).tar.xz DOC LICENSE README.mdown RELEASE.mdown Changelog.mdown tests/test.py modules/pyproperties.py Makefile data/* manual/*.mdown

doc: ./modules/pyproperties.py
	pydoc3 ./modules/pyproperties.py > DOC

manual:
	sed -i -e s/${OLD}/${VERSION}/ manual/*.mdown
	#pandoc -o ./manual/manual.pdf ./manual/*.mdown

test:
	python3 -m unittest --catch --failfast --verbose tests/test.py

release: test doc tar
	sed -i -e s/${OLD}/${VERSION}/ RELEASE.mdown

install:
	python3 ./modules/install.py

uninstall:
	python3 ./modules/uninstall.py

clean:
	rm -rv ./modules/__pycache__/
	rm -rv ./tests/__pycache__/
