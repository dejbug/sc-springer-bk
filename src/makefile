.PHONY : all clean run inc incpat incmaj incmin

VENDOR := 0
LEARNING := 0

MAJOR := $(shell cut -d. -f1 VERSION)
MINOR := $(shell cut -d. -f2 VERSION)
PATCH := $(shell cut -d. -f3 VERSION)

FILES := $(wildcard *.html *.css *.ico)

DIST :=
DIST += $(FILES:%=dist/%)
DIST += dist/img/ dist/downloads/
ifneq ($(VENDOR),0)
	DIST += dist/vendor/
endif
ifneq ($(LEARNING),0)
	DIST += dist/learning/
endif

all : $(DIST)

dist : ; mkdir -p ./dist/
dist/%/ : % | dist ; cp -rt ./dist/ ./$</
dist/% : % | dist ; cp -t ./dist/ ./$<

dist/index.html : index.html tools/gen.py | dist ; python tools/gen.py -fo dist/index.html

clean : ; rm -rf ./dist/
run : all ; cd dist && php -S 0.0.0.0:8000

incmaj : ; @echo -n $(shell echo $(MAJOR)+1 | bc).$(MINOR).$(PATCH) > VERSION
incmin : ; @echo -n $(MAJOR).$(shell echo $(MINOR)+1 | bc).$(PATCH) > VERSION
incpat : ; @echo -n $(MAJOR).$(MINOR).$(shell echo $(PATCH)+1 | bc) > VERSION
inc : incpat ;
