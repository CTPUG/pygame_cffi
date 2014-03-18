#!/bin/bash

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/

	for i in 10 100 1000; do
		for size in 10 20 40; do
			echo "$venv: $i surfaces, ${size}x${size} pixels" >> benchmarks/blit_bench.csv

			for rep in 1 2 3; do
				python benchmarks/run_benchmark.py blit -i 0.3 -r 15 $i $size $size >> benchmarks/blit_bench.csv
			done
		done
	done
done
