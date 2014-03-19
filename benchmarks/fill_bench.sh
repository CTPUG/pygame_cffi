#!/bin/bash

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/

	for i in 10 100 1000; do
		for size in 10 20 40; do
			echo "$venv: $i rectangles, ${size}x${size} pixels" >> benchmarks/fill_bench.csv

			for rep in 1 2 3; do
				python benchmarks/run_benchmark.py fill -i 0.3 -r 15 $i $size $size >> benchmarks/fill_bench.csv
			done
		done
	done
done
