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

from Data.models import Nuclide, History, Q_Record
import re
from datetime import date, datetime

cap_symbols = ["NN","H", "HE","LI","BE","B", "C","N", "O", "F", "NE","NA","MG","AL","SI","P", "S", "CL","AR","K", "CA","SC","TI","V", "CR","MN","FE","CO","NI","CU","ZN","GA","GE","AS","SE","BR","KR","RB","SR","Y", "ZR","NB","MO","TC","RU","RH","PD","AG","CD","IN","SN","SB","TE","I", "XE","CS","BA","LA","CE","PR","ND","PM","SM","EU","GD","TB","DY","HO","ER","TM","YB","LU","HF","TA","W", "RE","OS","IR","PT","AU","HG","TL","PB","BI","PO","AT","RN","FR","RA","AC","TH","PA","U", "NP","PU","AM","CM","BK","CF","ES","FM","MD","NO","LR","RF","DB","SG","BH","HS","MT","DS","RG", "CN", "UUT", "FL", "UUP", "LV", "UUS", "UUO"]
symbols = ["n","H", "He","Li","Be","B", "C","N", "O", "F", "Ne","Na","Mg","Al","Si","P", "S", "Cl","Ar","K", "Ca","Sc","Ti","V", "Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y", "Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I", "Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W", "Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U", "Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg", "Cn", "Uut", "Fl", "Uup", "Lv", "Uus", "Uuo"]

_ad_head_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))\s{4,5}ADOPTED LEVELS\s+([0-9A-Z]+)\s+(\d{6})$"
#_ad_head2_re = "^\s{0,2}(\d{1,3})([A-Z]{1,2})\s{4,5}ADOPTED LEVELS\s+([0-9A-Z]+)\s+(\d{6})$"
_hist_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))( |[2-9A-Z]) H (.*)$"
_q_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))( |[2-9A-Z]) H (.*)$"

#----------------------------------------------------------------------
def To_iZA(Z, A):
	return Z * 10000 + A

#----------------------------------------------------------------------
def ToFloat(string):
	string = string.strip()
	if (len(string) == 0):
		return None
	return float(string)

def LineNr(char):
	comp_str = " 23456789ABCDEFGHIJKLMNOPQR"
	if (len(char) != 1):
		raise Exception("LineNr(): This function only takes a single character.")
	pos = comp_str.find(char)
	if (-1 == pos):
		raise Exception("LineNr(): Unable to find character in line number list.")
	return pos

########################################################################
class RecordImporter(object):
	#----------------------------------------------------------------------
	def __init__(self, lines):
		self.line_ctr = 0
		self.lines = lines
		self.history = []
		self.q_records = []
		self.levels = []
		self.nuc_str = ""
		self.comments = ""
		self.ReadIdentRec()
		self.ReadHistory()
		self.ReadLevelsComments()
		self.ReadQRecords()
		self.ReadCrossReferences()
	
	#----------------------------------------------------------------------
	def MakeErrStr(self, error_str):
		ret_str = "In record with head: \"" + self.lines[0].strip() + "\", line #" + str(self.line_ctr)
		return ret_str + "\n-----" + error_str
		
	
	#----------------------------------------------------------------------
	def ReadIdentRec(self):
		line_one_res = re.match(_ad_head_re, self.lines[0])
		if (None == line_one_res):
			raise Exception(self.MakeErrStr("ReadIdentRec(): Adopted levels header does not match."))
		self.nuc_str = line_one_res.group(1)
		self.A = int(line_one_res.group(2))
		self.Z = int(cap_symbols.index(line_one_res.group(3)))
		self.symb = symbols[self.Z]
		self.iZA = To_iZA(self.Z, self.A)
		self.line_ctr += 1
	
	#----------------------------------------------------------------------
	def ParseHistory(self, hist_str):
		hist_parts = hist_str.split("$")
		h_type = None
		h_auth = None
		h_date = None
		h_cutoff = None
		h_com = ""
		h_cit = ""
		for part in hist_parts:
			p1 = part[0:3]
			p2 = part[4:]
			if ("TYP" == p1):
				h_type = p2
			elif ("AUT" == p1):
				h_auth = p2
			elif ("CIT" == p1):
				h_cit = p2
			elif ("COM" == p1):
				h_com = p2
			elif ("CUT" == p1):
				h_cutoff = datetime.strptime(p2, "%d-%b-%Y").date()
			elif ("DAT" == p1):
				h_date = datetime.strptime(p2, "%d-%b-%Y").date()
			elif (len(p1) == 0):
				pass
			else:
				raise Exception(self.MakeErrStr("ParseHistory(): Unknown history tag."))
		c_hist = History(HistoryType = h_type, Author = h_auth, Citation = h_cit, Date = h_date, CutOff = h_cutoff, Comments = h_com)
		c_hist.save()
		self.history.append(c_hist)
		
	#----------------------------------------------------------------------
	def ReadHistory(self):
		c_str = self.GetContRecord(" H ")
		while (None != c_str):
			self.ParseHistory(c_str)
			c_str = self.GetContRecord(" H ")

	#----------------------------------------------------------------------
	def GetContRecord(self, rec_type):
		c_str = None
		c_ctr = 0
		c_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))( |[2-9A-Z])" + rec_type + "(.*)$"
		while (True):
			re_res = re.match(c_re, self.lines[self.line_ctr])
			if (None == re_res):
				if (c_str != None):
					return c_str
				else:
					return None
			if (re_res.group(1) != self.nuc_str):
				raise Exception(self.MakeErrStr("GetConfRecord(): Nuclide string does not match header."))			
			c_line_nr = LineNr(re_res.group(4))
			if (c_line_nr == c_ctr):
				if (c_ctr != 0):
					c_str += (" " + re_res.group(5).rstrip())
				else:
					c_str = re_res.group(5).rstrip()
				self.line_ctr += 1
				c_ctr += 1
			elif (c_line_nr == 0):
				return c_str
			else:
				raise Exception(self.MakeErrStr("GetConfRecord(): Incorrect line number."))
	
	#----------------------------------------------------------------------
	def GetSingleRecord(self, rec_type):
		c_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2})) " + rec_type + "(.*)$"
		re_res = re.match(c_re, self.lines[self.line_ctr])
		if (None == re_res):
			return None
		if (re_res.group(1) != self.nuc_str):
			raise Exception(self.MakeErrStr("GetConfRecord(): Nuclide string does not match header."))
		self.line_ctr += 1
		return re_res.groups()[-1]
		
	
	#----------------------------------------------------------------------
	def ReadLevelsComments(self):
		self.comments = self.GetCommentLines("c  ")
	
	#----------------------------------------------------------------------
	def GetCommentLines(self, rec_type):
		all_comments = ""
		c_str = self.GetContRecord(rec_type)
		while (None != c_str):
			if (len(all_comments) > 0):
				all_comments += "\n"
			all_comments += c_str
			c_str = self.GetContRecord(rec_type)		
		return all_comments
	
	#----------------------------------------------------------------------
	def GetSeveralLines(self, rec_type):
		rec_line = 0
		c_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))( |[2-9A-Z])" + rec_type + "(.*)$"
		ret_lines = []
		re_res = re.match(c_re, self.lines[self.line_ctr])
		if (re_res != None):
			if (LineNr(re_res.group(4)) == 0):
				ret_lines.append(re_res.group(5))
				self.line_ctr += 1
				rec_line += 1
		else:
			return None
		re_res = re.match(c_re, self.lines[self.line_ctr])
		while (None != re_res):
			if (re_res.group(4) == " "):
				return ret_lines			
			if (LineNr(re_res.group(4)) != rec_line):
				print(self.MakeErrStr("GetSeveralLines(): Got incorrect record line number."))
			rec_line += 1
			self.line_ctr += 1
			ret_lines.append(re_res.group(5))
		return ret_lines
	
	#----------------------------------------------------------------------
	def CreateQRecord(self, line, comments):
		Q = ToFloat(line[0:10])
		DQ = ToFloat(line[10:12])
		SN = ToFloat(line[12:20])
		DSN = ToFloat(line[20:22])
		SP = ToFloat(line[22:30])
		DSP = ToFloat(line[30:32])
		QA = ToFloat(line[32:40])
		DQA = ToFloat(line[40:46])
		REF = line[46:].strip()
		c_rec = Q_Record(Qb = Q, QbSA = DQ, Sn = SN, SnSA = DSN, Sp = SP, SpSA = DSP, Qa = QA, QaSA = DQA, Reference = REF, Comments = comments)
		c_rec.save()
		return c_rec
	
	#----------------------------------------------------------------------
	def ReadQRecords(self):
		q_line = self.GetSingleRecord(" Q ")
		c_com = self.GetCommentLines("[cC]Q ")
		while (q_line != None):
			self.q_records.append(self.CreateQRecord(q_line, c_com))
			q_line = self.GetSingleRecord(" Q ")
			c_com = self.GetCommentLines("[cC]Q ")
	
	#----------------------------------------------------------------------
	def ReadCrossReferences(self):
		print(self.MakeErrStr("ReadCrossReferences(): Skipping cross references."))
		while(True):
			c_line = self.lines[self.line_ctr]
			if (c_line[6:9] == "  X"):
				self.line_ctr += 1
			else:
				break
	#----------------------------------------------------------------------
	def ParseLevelData(self, lvl_lines, lvl_com):
		pass
		
	
	#----------------------------------------------------------------------
	def ReadLevels(self):
		lvl_lines = self.GetSeveralLines(" L ")
		lvl_com = self.GetCommentLines("[cC]L ")
		
		while (lvl_lines != None):
			lvl_lines = self.GetSeveralLines(" L ")
			lvl_com = self.GetCommentLines("[cC]L ")			
		

