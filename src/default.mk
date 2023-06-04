.PHONY : all

MISC := dist/VERSION dist/favicon.ico dist/img/ dist/downloads/ dist/default.css

HTML := $(wildcard *.html)
HTML := $(HTML:%=dist/%)

all : $(HTML) $(MISC)

ifneq ($(VENDOR),0)
all : dist/vendor/
endif

ifneq ($(LEARNING),0)
all : dist/learning/
endif

dist/index.php : tools/index.php ; $(call FCOPY,$<,dist)

dist/default.css : css/* dist/vendor/github.svg

$(DIST) : content/*.html

dist/vereinsturniere.html : dist/pokal-22.html

dist/blitz-*.html : dist/blitz-%.html : tables/blitz-%.csv tools/csv2table.py
