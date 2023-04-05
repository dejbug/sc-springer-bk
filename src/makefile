.PHONY : all clean run inc incpat incmaj incmin

RELEASE := 0

MAJOR := $(shell cut -d. -f1 VERSION)
MINOR := $(shell cut -d. -f2 VERSION)
PATCH := $(shell cut -d. -f3 VERSION)

DIST :=
DIST += dist/*.html dist/*.css
DIST += dist/img/ dist/vendor/ dist/downloads/
ifneq ($(RELEASE),1)
DIST += dist/learning/
endif

all : $(DIST)
dist : ; mkdir -p ./dist/
dist/%/ : % | dist ; cp -rt ./dist/ ./$</
dist/% : % | dist ; cp -t ./dist/ ./$<

clean : ; rm -rf ./dist/
run : ; php -S 0.0.0.0:8000

incmaj : ; @echo -n $(shell echo $(MAJOR)+1 | bc).$(MINOR).$(PATCH) > VERSION
incmin : ; @echo -n $(MAJOR).$(shell echo $(MINOR)+1 | bc).$(PATCH) > VERSION
incpat : ; @echo -n $(MAJOR).$(MINOR).$(shell echo $(PATCH)+1 | bc) > VERSION
inc : incpat ;
