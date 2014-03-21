#!/bin/bash

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/
	echo "$venv" >> benchmarks/events_bench.csv

	for rep in 1 2 3; do
		python benchmarks/run_benchmark.py events -i 0.3 -r 30 -w 5000 >> benchmarks/events_bench.csv
	done
done