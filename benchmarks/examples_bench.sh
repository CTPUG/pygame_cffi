#!/bin/bash

for venv in pygame_cffi pygame pygame_cffi_cpython; do
	source ~/.virtualenvs/$venv/bin/activate
	cd ~/pygame_cffi/

	for example in "moveit" "stars" "testsprite" "sprite_collide_blocks"; do
		echo "$venv: $example" >> benchmarks/examples_bench.csv

		for rep in 1 2 3; do
			python benchmarks/run_benchmark.py $example -i 0.3 -r 30 -w 5000 >> benchmarks/examples_bench.csv
		done
	done
done
