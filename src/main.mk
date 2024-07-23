MISC := favicon.ico img/ downloads/
MISC += vendor/github.svg
ifneq ($(LEARNING),0)
MISC += dist/learning/ dist/learning/*
endif
ifneq ($(VENDOR),0)
MISC += dist/vendor/ dist/vendor/*
endif
ifneq ($(REWE),0)
MISC += $(wildcard vendor/rewe/img/*.png)
endif
MISC := $(MISC:%=dist/%)

# VEREINSTURNIERE := dist/vereinsturniere-24.html dist/vereinsturniere-22.html dist/vereinsturniere-23.html
VEREINSTURNIERE := $(shell python tools/vereinsturniere.py --tdir tables --list)
# VEREINSTURNIERE := $(VEREINSTURNIERE:%=dist/vereinsturniere-%.html)
# VEREINSTURNIERE := $(patsubst %,dist/vereinsturniere-%.html,$(VEREINSTURNIERE))
# VEREINSTURNIERE := $(shell python tools/patsubst.py \(.+\) dist/vereinsturniere-\\1.html '22 23 24')
# VEREINSTURNIERE := 22 23 24
VEREINSTURNIERE := $(VEREINSTURNIERE:%=dist/vereinsturniere-%.html)

HTML := $(wildcard *.html) default.css
HTML := $(HTML:%=dist/%) $(VEREINSTURNIERE)

ifeq ($(REWE),0)
HTML := $(filter-out %/scheinescanner.html,$(HTML))
endif

$(info --- HTML ---)
$(info $(HTML))
$(info --- MISC ---)
$(info $(MISC))

all : $(HTML) $(MISC) dist/VERSION

.PHONY : x-html x-misc
x-html : ; @python -c 'print("\n".join("$(HTML)".split()))'
x-misc : ; @python -c 'print("\n".join("$(MISC)".split()))'

dist/VERSION : ../VERSION ; $(call NCOPY,$<,$<)

dist/index.php : tools/index.php ; $(call FCOPY,$<,dist)

$(VEREINSTURNIERE) : dist/vereinsturniere-%.html : build/vereinsturniere-%.html | dist
	$(RENDER) -o $@ $<

$(VEREINSTURNIERE:dist/%=build/%) : build/vereinsturniere-%.html : | build
	python tools/vereinsturniere.py --tdir tables --pdir . --year-from-path $@ --ofile $@
