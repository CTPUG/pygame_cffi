#!/bin/bash

use_hw_surface=$1
if [[ -z $1 || $use_hw_surface == 0 ]]; then
	use_hw_surface=0
	suffix=""
else
	use_hw_surface=1
	suffix="_hw"
fi

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/

	for i in 10 100 1000; do
		for size in 10 20 40; do
			echo "$venv: $i rectangles, ${size}x${size} pixels" >> benchmarks/fill_bench${suffix}.csv

			for rep in 1 2 3; do
				python benchmarks/run_benchmark.py fill -i 0.3 -r 30 -w 5000 $i $size $size $use_hw_surface >> benchmarks/fill_bench${suffix}.csv
			done
		done
	done
done
