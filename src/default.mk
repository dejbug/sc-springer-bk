MISC := VERSION favicon.ico img/ downloads/ default.css
MISC += $(wildcard vendor/rewe/img/*.png)
MISC := $(MISC:%=dist/%)


HTML := $(wildcard *.html)
HTML := $(HTML:%=dist/%)

all :
	@echo $(SHELL)
	@ls -l /bin/sh
	@$(SHELL) --version | head -n 1
	@python --version
	@[[ -a makefile ]] && echo OK

#~ all : $(HTML) $(MISC)

ifneq ($(VENDOR),0)
all : dist/vendor/
endif

ifneq ($(LEARNING),0)
all : dist/learning/
endif

dist/index.php : tools/index.php ; $(call FCOPY,$<,dist)

dist/default.css : css/* dist/vendor/github.svg

$(HTML) : content/*.html

dist/vereinsturniere.html : dist/pokal-22.html

dist/blitz-*.html : dist/blitz-%.html : tables/blitz-%.csv tools/csv2table.py
