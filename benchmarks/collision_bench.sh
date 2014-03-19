#!/bin/bash

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/

	for i in 10 100 1000; do
		echo "$venv: $i sprites" >> benchmarks/collision_bench.csv

		for rep in 1 2 3; do
			python benchmarks/run_benchmark.py collision_detection -i 0.3 -r 15 $i >> benchmarks/collision_bench.csv
		done
	done
done
