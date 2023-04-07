.PHONY : all

all : dist/index.html

ifneq ($(VENDOR),0)
all : dist/vendor/
endif

ifneq ($(LEARNING),0)
all : dist/learning/
endif

dist/index.html : dist/default.css
dist/index.html : dist/img/ dist/downloads/
dist/index.html : dist/VERSION dist/favicon.ico

dist/default.css : $(wildcard css/*)
dist/default.css : dist/vendor/github.svg

dist/index.php : tools/index.php ; $(call FCOPY,$<,dist)
