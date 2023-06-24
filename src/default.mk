MISC := VERSION favicon.ico img/ downloads/ default.css
MISC += $(wildcard vendor/rewe/img/*.png)
MISC := $(MISC:%=dist/%)

VEREINSTURNIERE := $(shell python tools/vereinsturniere.py --tdir tables --list)
VEREINSTURNIERE := $(VEREINSTURNIERE:%=dist/vereinsturniere-%.html)

HTML := $(wildcard *.html)
HTML := $(HTML:%=dist/%) $(VEREINSTURNIERE)

all : $(HTML) $(MISC)

ifneq ($(VENDOR),0)
all : dist/vendor/ dist/vendor/*
endif

ifneq ($(LEARNING),0)
all : dist/learning/ dist/learning/*
endif

dist/index.php : tools/index.php ; $(call FCOPY,$<,dist)

dist/default.css : css/* dist/vendor/github.svg

$(HTML) : content/*.html


#~ dist/vereinsturniere.html : dist/pokal-22.html dist/pokal-23.html

$(VEREINSTURNIERE) : dist/vereinsturniere-%.html : build/vereinsturniere-%.html | dist
	$(RENDER) -o $@ $<

$(VEREINSTURNIERE:dist/%=build/%) : build/vereinsturniere-%.html : | build
	python tools/vereinsturniere.py --tdir tables --pdir . --year-from-path $@ --ofile $@


dist/blitz-*.html : dist/blitz-%.html : tables/blitz-%.csv tools/csv2table.py tools/tables.py
dist/schnell-*.html : dist/schnell-%.html : tables/schnell-%.csv tools/csv2table.py tools/tables.py

dist/aktuelles.html : content/news.txt tools/news.py

dist/scheinescanner.html : dist/vendor/nimiq/qr-scanner.umd.min.js
dist/scheinescanner.html : dist/vendor/nimiq/qr-scanner-worker.min.js

# HACKS

tables/schnell-23-06.csv : tables/schnell-23-06-games.csv
