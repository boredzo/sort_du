#!/usr/bin/python3

"""sort_du
by Peter Hosey

Sort the output of du -h by disk usage. That is, interpret the disk usage amounts reported by du -h as intended (3.2G > 3.1G > 3.3M).

Feed du output in on sort_du's standard input. Sorted output will be written to standard output.

TODO: Properly handle hierarchical output
"""

import os
import sys
import re
import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('--human-readable', action='store_const', dest='multiple', const=1024, default=1024, help='(Default) Interpret units as powers of 1024 (kibibytes, mebibytes, gibibytes, etc.).')
parser.add_argument('--si', action='store_const', dest='multiple', const=1000, help='Interpret units as powers of 1000 (SI kilo, mega, giga, etc.).')
parser.add_argument('-r', '--ascending', action='store_false', dest='descending', default=True, help='Sort items from smallest to largest (default is largest to smallest).')
opts = parser.parse_args()

unit_multiplier_interval = opts.multiple
units = {}
multiple = 1
for ch in 'BKMGTPEZY':
	units[ch] = multiple
	multiple *= unit_multiplier_interval
units[''] = units['B']

du_exp = re.compile('\s*([0-9.]+)([BKMGTEP]?)\t(.+)')
inventory = {}
size_descs = {}

for line in sys.stdin:
	match = du_exp.match(line.rstrip('\n'))
	if not match:
		print('Match failure:', file=sys.stderr)
		print(line, file=sys.stderr)
		sys.exit(1)
		continue

	quantity = float(match.group(1))
	unit_ch = match.group(2)
	unit_multiplier = units[unit_ch]
	this_size = int(quantity * unit_multiplier)
	path = match.group(3)

	desc = line[:match.end(2)]
	size_descs.setdefault(this_size, desc)

	paths_of_this_size = inventory.setdefault(this_size, [])
	paths_of_this_size.append(path)

sizes = list(inventory)
sizes.sort(reverse=opts.descending)

for this_size in sizes:
	paths_of_this_size = inventory[this_size]
	desc = size_descs[this_size]
	for path in paths_of_this_size:
		print('{}\t{}'.format(desc, path))
