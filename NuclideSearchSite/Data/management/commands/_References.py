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

from Data.models import References
import re

_header_re = re.compile("\s{0,2}(\d{1,3})\s{6}REFERENCES\s{46}(\s{5}|[A-Z0-9]{5})\s{4}(\d{4})(\d{2})$")
_ref_re = re.compile("^\s{0,2}(\d{1,3})\s{4}R\s(\d{4}[A-Z]{2}(\d{2}|[A-Z]{2}))\s(CONF|JOUR)\s(.*)$")

#----------------------------------------------------------------------
def import_references(lines):
	choices = {"JOUR":"JR", "BOOK":"BK"}
	
	line_one_res = re.match(_header_re, lines[0], flags=0)
	if (None == line_one_res):
		raise Exception("References header does not match.")
	block_nr = int(line_one_res.group(1))
	
	new_references_list = []
	for c_line in lines[1:]:
		c_res = re.match(_ref_re, c_line)
		if (None == c_res):
				raise Exception("Reference line does not match.")
		c_nr = int(c_res.group(1))
		if (c_nr != block_nr):
			raise Exception("Reference atomic number does not match header.")
		c_ref = References(RefKey = c_res.group(2), Publication = c_res.group(5).strip(), PublicationType = choices[c_res.group(4)])
		new_references_list.append(c_ref)
	References.objects.bulk_create(new_references_list)
	