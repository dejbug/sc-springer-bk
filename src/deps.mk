SOURCES := $(wildcard *.html) default.css

build/%.d : % | build ; python tools/deps.py -o $@ -TDa $<

include $(SOURCES:%=build/%.d)

dist/aktuelles.html : content/news.txt
dist/scheinescanner.html : dist/vendor/nimiq/qr-scanner.umd.min.js
dist/scheinescanner.html : dist/vendor/nimiq/qr-scanner-worker.min.js

# HACKS

tables/schnell-23-06.csv : tables/schnell-23-06-games.csv

dist/default.css : vendor/github.svg
