#!/opt/local/bin/python
# encoding: utf-8

# NuclideSearch, A web application for finding nuclear data.
# Copyright (C) 2016  Jonas Nilsson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.core.management.base import BaseCommand, CommandError
import glob
from Data.management.commands._References import import_references
from Data.management.commands._AdoptedLevels import *

def parse_block(block):
    if (len(block) == 0):
        return
    lines = block.split("\n")
    first_line = lines[0]
    if ("COMMENTS" in first_line):
        print("Ignoring file comments in ensdf file.")
    elif ("REFERENCES" in first_line):
        pass
        #import_references(lines)
    elif ("ADOPTED LEVELS" in first_line):
        tst = RecordImporter(lines)
    else:
        print("Unknown ENSDF block:" + first_line)
    pass

class Command(BaseCommand):
    help = 'Import ENSDF data.'

    def add_arguments(self, parser):
        parser.add_argument('ensdf_path', nargs=1, type=str)

    def handle(self, *args, **options):
        file_names = glob.glob(options["ensdf_path"][0] + "/*")
        for c_name in file_names:
            try:
                in_file = open(c_name)
                in_data = in_file.read()
                in_file.close()
                data_blocks = None
                if (in_data.find("\n\n") >= 0):
                    data_blocks = in_data.split("\n")
                else:
                    data_blocks = in_data.split("\n" + 80 * " " + "\n")
                for block in data_blocks:
                    parse_block(block)
            except IsADirectoryError as e:
                pass
