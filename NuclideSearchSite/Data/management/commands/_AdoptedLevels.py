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

from Data.models import Nuclide
import re

cap_symbols = ["NN","H", "HE","LI","BE","B", "C","N", "O", "F", "NE","NA","MG","AL","SI","P", "S", "CL","AR","K", "CA","SC","TI","V", "CR","MN","FE","CO","NI","CU","ZN","GA","GE","AS","SE","BR","KR","RB","SR","Y", "ZR","NB","MO","TC","RU","RH","PD","AG","CD","IN","SN","SB","TE","I", "XE","CS","BA","LA","CE","PR","ND","PM","SM","EU","GD","TB","DY","HO","ER","TM","YB","LU","HF","TA","W", "RE","OS","IR","PT","AU","HG","TL","PB","BI","PO","AT","RN","FR","RA","AC","TH","PA","U", "NP","PU","AM","CM","BK","CF","ES","FM","MD","NO","LR","RF","DB","SG","BH","HS","MT","DS","RG", "CN", "UUT", "FL", "UUP", "LV", "UUS", "UUO"]
symbols = ["n","H", "He","Li","Be","B", "C","N", "O", "F", "Ne","Na","Mg","Al","Si","P", "S", "Cl","Ar","K", "Ca","Sc","Ti","V", "Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y", "Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I", "Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W", "Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U", "Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg", "Cn", "Uut", "Fl", "Uup", "Lv", "Uus", "Uuo"]

_ad_head_re = "^\s{0,2}(\d{1,3})([A-Z]{1,2})\s{4,5}ADOPTED LEVELS\s+([0-9A-Z]+)\s+(\d{6})$"
#_ad_head2_re = "^\s{0,2}(\d{1,3})([A-Z]{1,2})\s{4,5}ADOPTED LEVELS\s+([0-9A-Z]+)\s+(\d{6})$"
_hist_re = "^\s{0,2}(\d{1,3})([A-Z]{1,2})( |[1-9a-z]) H (.*)$"

#----------------------------------------------------------------------
def To_iZA(Z, A):
	return Z * 10000 + A
	

########################################################################
class RecordImporter(object):
	#----------------------------------------------------------------------
	def __init__(self, lines):
		self.line_ctr = 0
		self.lines = lines
		self.history = []
		self.nuc_str = ""
		self.GetIdentRec()
	
	#----------------------------------------------------------------------
	def GetIdentRec(self):
		line_one_res = re.match(_header_re, lines[0])
		if (None == line_one_res):
			raise Exception("Adopted levels header does not match.")
		self.nuc_str = line_one_res.group(1)
		self.A = int(line_one_res.group(2))
		self.Z = int(cap_symbols.index(line_one_res.group(3)))
		self.symb = symbols[self.Z]
		self.iZA = To_iZA(self.Z, self.A)
		
		

def get_history()

def import_adopted_levels(lines):
	line_one_res = re.match(_header_re, lines[0])
	if (None == line_one_res):
		raise Exception("Adopted levels header does not match.")
	