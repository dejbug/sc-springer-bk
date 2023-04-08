.PHONY : all clean serve run ls inc incpat incmaj incmin

VENDOR := 0
LEARNING := 0

MAJOR := $(shell cut -d. -f1 VERSION)
MINOR := $(shell cut -d. -f2 VERSION)
PATCH := $(shell cut -d. -f3 VERSION)

MKDIR := mkdir -p
RMDIR := rm -rf
FCOPY = $(MKDIR) dist/$(dir $2) && cp -t dist/$(dir $2) $1
DCOPY = $(MKDIR) dist/$2 && cp -t dist/ -r $1

SERVE := php -S 0.0.0.0:8000
RENDER := python tools/render.py

include default.mk

all : ;

dist/%.html : %.html | dist ; $(RENDER) -o dist/$< $<
dist/%.css : %.css | dist ; $(RENDER) -o dist/$< $<

dist/% : % | dist ; $(call FCOPY,$<,$<)
dist/%/ : % | dist ; $(call DCOPY,$<,$<)

dist : ; $(MKDIR) dist/


clean : ; $(RMDIR) dist/

serve : all ; cd dist && rm -f index.php && $(SERVE)
run : all dist/index.php ; cd dist && $(SERVE)

ls : all ; @find dist/ -type f | sort

incmaj : ; @echo -n $(shell echo $(MAJOR)+1 | bc).$(MINOR).$(PATCH) > VERSION
incmin : ; @echo -n $(MAJOR).$(shell echo $(MINOR)+1 | bc).$(PATCH) > VERSION
incpat : ; @echo -n $(MAJOR).$(MINOR).$(shell echo $(PATCH)+1 | bc) > VERSION
inc : incpat
