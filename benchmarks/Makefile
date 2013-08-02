all: load-graph-tinymem load-graph-smallmem load-graph-medmem \
	normalize-tinymem normalize-smallmem normalize-medmem

load-graph-tinymem:
	-mkdir tmp 2> /dev/null
	./time.sh load-graph-tinymem.time ../scripts/load-graph.py -x 1 -N 1 tmp/xxx.kh ../data/1m-filtered.fa

load-graph-smallmem:
	-mkdir tmp 2> /dev/null
	./time.sh load-graph-smallmem.time ../scripts/load-graph.py -x 1e6 -N 1 tmp/xxx.kh ../data/1m-filtered.fa

load-graph-medmem:
	-mkdir tmp 2> /dev/null
	./time.sh load-graph-medmem.time ../scripts/load-graph.py -x 1e9 -N 1 tmp/xxx.kh ../data/1m-filtered.fa

normalize-tinymem:
	-mkdir tmp 2> /dev/null
	cd tmp; ../time.sh ../normalize-tinymem.time ../../scripts/normalize-by-median.py -x 1 -N 1 ../../data/1m-filtered.fa

normalize-smallmem:
	-mkdir tmp 2> /dev/null
	cd tmp;	../time.sh ../normalize-smallmem.time ../../scripts/normalize-by-median.py -x 1e6 -N 1 ../../data/1m-filtered.fa

normalize-medmem:
	-mkdir tmp 2> /dev/null
	cd tmp;	../time.sh ../normalize-medmem.time ../../scripts/normalize-by-median.py -x 1e9 -N 1 ../../data/1m-filtered.fa

