m3:
	CFLAGS=-O3 python setup.py build_ext --inplace
	python bench.py m3