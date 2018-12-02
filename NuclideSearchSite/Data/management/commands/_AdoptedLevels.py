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

from Data.models import Nuclide, History, Q_Record, Level, ContinuationField, AdoptedLevels
import re
from datetime import date, datetime

cap_symbols = ["NN","H", "HE","LI","BE","B", "C","N", "O", "F", "NE","NA","MG","AL","SI","P", "S", "CL","AR","K", "CA","SC","TI","V", "CR","MN","FE","CO","NI","CU","ZN","GA","GE","AS","SE","BR","KR","RB","SR","Y", "ZR","NB","MO","TC","RU","RH","PD","AG","CD","IN","SN","SB","TE","I", "XE","CS","BA","LA","CE","PR","ND","PM","SM","EU","GD","TB","DY","HO","ER","TM","YB","LU","HF","TA","W", "RE","OS","IR","PT","AU","HG","TL","PB","BI","PO","AT","RN","FR","RA","AC","TH","PA","U", "NP","PU","AM","CM","BK","CF","ES","FM","MD","NO","LR","RF","DB","SG","BH","HS","MT","DS","RG", "CN", "UUT", "FL", "UUP", "LV", "UUS", "UUO"]
symbols = ["n","H", "He","Li","Be","B", "C","N", "O", "F", "Ne","Na","Mg","Al","Si","P", "S", "Cl","Ar","K", "Ca","Sc","Ti","V", "Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y", "Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I", "Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W", "Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U", "Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg", "Cn", "Uut", "Fl", "Uup", "Lv", "Uus", "Uuo"]

#----------------------------------------------------------------------
def To_iZA(Z, A):
    return Z * 10000 + A

#----------------------------------------------------------------------
def ToFloat(string):
    string = string.strip()
    if (len(string) == 0):
        return None
    return float(string)

#----------------------------------------------------------------------
def ToStr(string):
    string = string.strip()
    if (len(string) == 0):
        return None
    return string


def LineNr(char):
    comp_str = " 23456789ABCDEFGHIJKLMNOPQR"
    if (len(char) != 1):
        raise Exception("LineNr(): This function only takes a single character.")
    pos = comp_str.find(char)
    if (-1 == pos):
        print("LineNr(): Unable to find character in line number list.")
    return pos

#----------------------------------------------------------------------
def CalcUncValue(valueStr, uncStr):
    value_re = "\d*(?:.(\d+))?([eE][+-]?\d+)?"
    res = re.match(value_re, valueStr)
    mod1 = 1.0
    mod2 = 1.0
    if (res.group(1) != None):
        mod1 = (10.0)**len(res.group(1))
    if (res.group(2) != None):
        mod2 = float("1" + res.group(2))
    return (float(valueStr) / mod1) * mod2


#----------------------------------------------------------------------
def ParseHalfLife(hl_part, unc_part):
    hl_part = hl_part.strip()
    if (len(hl_part )== 0):
        return None, None, False
    hl_re = "((?:STABLE)|\d+(?:.\d+)?(?:[eE][+-]?\d+)?)(?: ([a-zA-Z]+))?"
    value_mod = {"Y":3600*24*365.25, "D":3600*24, "H":3600, "M":60, "S":1, "MS":1e-3, "US":1e-6, "NS":1e-9, "PS":1e-12, "FS":1e-15, "AS":1e-18, "EV":1, "KEV":1e3, "MEV":1e6}
    res = re.match(hl_re, hl_part)
    if (res.group(1) == "STABLE"):
        return 0, None, False
    hl_value = float(res.group(1)) * value_mod[res.group(2)]
    SA = CalcUncValue(res.group(1), unc_part)
    if (SA != None):
        SA *= value_mod[res.group(2)]
    isEV = False
    if (res.group(2) in ["EV", "KEV", "MEV"]):
        isEV = True
    return hl_value, SA, isEV

class LineInfo(object):
    def __init__(self, String):
        if (len(String) == 0):
            self.RecordType = None
            return
        self.MassNumber = int(String[0:3].strip())
        self.Symbol = String[3:5].strip()
        self.ContNr = String[5]
        self.A = self.MassNumber
        self.CommentChar = String[6]
        self.IsComment = self.CommentChar is "C" or self.CommentChar is "c"
        self.RecordType = String[7]
        self.Data = String[9:].rstrip()
        self.NucLine = str(self.MassNumber) + self.Symbol

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
        while (self.line_ctr < len(self.lines)):
            Line = LineInfo(self.GetLine())
            if ("H" is Line.RecordType):
                self.ReadHistory()
            elif ("Q" is Line.RecordType):
                self.ReadQRecords()
            elif (" " is Line.RecordType):
                self.comments = self.ReadComments(" ")
            elif ("L" is Line.RecordType):
                self.ReadLevels()
            elif ("X" is Line.RecordType):
                self.ReadCrossReferences()
            else:
                raise Exception(self.MakeErrStr("Unknown record type (\"{}\") encountered.".format(RecordType)))
        self.AssembleRecord()

    #----------------------------------------------------------------------
    def GetLine(self):
        if (self.line_ctr >= len(self.lines)):
            return ""
        return self.lines[self.line_ctr]

    #----------------------------------------------------------------------
    def IncLineCtr(self):
        self.line_ctr += 1

    #----------------------------------------------------------------------
    def MakeErrStr(self, error_str):
        ret_str = "In record with head: \"" + self.lines[0].strip() + "\", line #" + str(self.line_ctr)
        return ret_str + "\n-----" + error_str

    #----------------------------------------------------------------------
    def AssembleRecord(self):
        if (self.line_ctr != len(self.lines)):
            raise Exception(self.MakeErrStr("AssembleRecord(): Did not read all lines in record ({}/{}).".format(self.line_ctr, len(self.lines))))
        rec = AdoptedLevels(A = self.A, Z = self.Z, iZA = self.iZA, symbol = self.symb, comments = self.comments)
        rec.save()
        rec.history.add(*self.history)
        rec.Q.add(*self.q_records)
        rec.levels.add(*self.levels)
        rec.save()

    #----------------------------------------------------------------------
    def ReadIdentRec(self):
        CLine = LineInfo(self.GetLine())
        self.nuc_str = CLine.NucLine
        self.A = CLine.MassNumber
        self.Z = int(cap_symbols.index(CLine.Symbol))
        self.symb = symbols[self.Z]
        self.iZA = To_iZA(self.Z, self.A)
        self.line_ctr += 1

    #----------------------------------------------------------------------
    def ParseHistory(self, hist_str):
        hist_parts = hist_str.strip().split("$")
        h_type = None
        h_auth = None
        h_date = None
        h_cutoff = None
        h_com = ""
        h_cit = ""
        for part in hist_parts:
            CurrentPart = part.strip()
            p1 = CurrentPart[0:3]
            p2 = CurrentPart[4:]
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

    def GetNextRecordType(self):
        return self.lines[self.line_ctr][7]

    #----------------------------------------------------------------------
    def ReadHistory(self):
        c_str = self.GetContRecord("H")
        while (None != c_str):
            self.ParseHistory(c_str)
            c_str = self.GetContRecord("H")

    #----------------------------------------------------------------------
    def GetContRecord(self, rec_type, AsList = False, IsComment = False):
        ReturnValue = None
        if (AsList):
            ReturnValue = []
        c_ctr = 0
        while (True):
            if (self.line_ctr == len(self.lines)):
                return ReturnValue
            c_line = LineInfo(self.GetLine())
            if ("X" is c_line.ContNr and not c_line.IsComment):
                print("Skipping XREF in continuation")
                self.IncLineCtr()
                continue

            if (c_line.RecordType != rec_type or (c_line.IsComment and not IsComment)):
                return ReturnValue
            if (c_line.NucLine != self.nuc_str):
                raise Exception(self.MakeErrStr("GetContRecord(): Nuclide string does not match header."))
            c_line_nr = LineNr(c_line.ContNr)
            if (c_line.ContNr == " " and c_ctr > 0):
                return ReturnValue
            else:
                if (c_ctr != 0 and not AsList):
                    ReturnValue += (" " + c_line.Data)
                elif (not AsList):
                    ReturnValue = c_line.Data
                else:
                    ReturnValue.append(c_line.Data)
                if (c_line_nr != c_ctr):
                    print(self.MakeErrStr("GetContRecord(): Incorrect line number."))
                self.IncLineCtr()
                c_ctr += 1


    #----------------------------------------------------------------------
    def GetSingleRecord(self, rec_type):
        Line = LineInfo(self.GetLine())
        if (Line.RecordType != rec_type):
            raise Exception(self.MakeErrStr("GetSingleRecord(): Incorrect record type ({}/{}).".format(rec_type, Line.RecordType)))
        if (Line.NucLine != self.nuc_str):
            raise Exception(self.MakeErrStr("GetConfRecord(): Nuclide string does not match header."))
        self.line_ctr += 1
        return Line

    #----------------------------------------------------------------------
    def ReadComments(self, RecordType):
        return self.GetCommentLines(RecordType)

    #----------------------------------------------------------------------
    def GetCommentLines(self, RecordType):
        all_comments = ""
        c_str = self.GetContRecord(RecordType, IsComment=True)
        while (None != c_str):
            if (len(all_comments) > 0):
                all_comments += "\n"
            all_comments += c_str
            c_str = self.GetContRecord(RecordType, IsComment=True)
        return all_comments

    #----------------------------------------------------------------------
    def GetCommentLinesList(self, rec_type):
        ret_list = []
        c_str = self.GetContRecord(rec_type)
        while (None != c_str):
            ret_list.append(c_str)
            c_str = self.GetContRecord(rec_type)
        return ret_list

    #----------------------------------------------------------------------
    def GetSeveralLines(self, rec_type):
        rec_line = 0
        c_re = "^\s{0,2}((\d{1,3})([A-Z]{1,2}))( |[2-9A-Z])" + rec_type + "(.*)$"
        ret_lines = []
        re_res = re.match(c_re, self.GetLine())
        if (re_res != None):
            if (LineNr(re_res.group(4)) == 0):
                ret_lines.append(re_res.group(5))
                self.IncLineCtr()
                rec_line += 1
        else:
            return None
        re_res = re.match(c_re, self.GetLine())
        while (None != re_res):
            if (re_res.group(4) == " "):
                return ret_lines
            if (LineNr(re_res.group(4)) != rec_line):
                print(self.MakeErrStr("GetSeveralLines(): Got incorrect record line number."))
            rec_line += 1
            self.IncLineCtr()
            ret_lines.append(re_res.group(5))
            re_res = re.match(c_re, self.GetLine())
        return ret_lines

    #----------------------------------------------------------------------
    def CreateQRecord(self, line, comments):
        Q = ToFloat(line.Data[0:10])
        DQ = ToFloat(line.Data[10:12])
        SN = ToFloat(line.Data[12:20])
        DSN = ToFloat(line.Data[20:22])
        SP = ToFloat(line.Data[22:30])
        DSP = ToFloat(line.Data[30:32])
        QA = ToFloat(line.Data[32:40])
        DQA = ToFloat(line.Data[40:46])
        REF = line.Data[46:].strip()
        c_rec = Q_Record(Qb = Q, QbSA = DQ, Sn = SN, SnSA = DSN, Sp = SP, SpSA = DSP, Qa = QA, QaSA = DQA, Reference = REF, Comments = comments)
        c_rec.save()
        return c_rec

    #----------------------------------------------------------------------
    def ReadQRecords(self):
        while (LineInfo(self.GetLine()).RecordType is "Q"):
            q_line = self.GetSingleRecord("Q")
            c_com = self.GetCommentLines("Q")            
            self.q_records.append(self.CreateQRecord(q_line, c_com))

    #----------------------------------------------------------------------
    def ReadCrossReferences(self):
        print(self.MakeErrStr("ReadCrossReferences(): Skipping cross references."))
        while(LineInfo(self.GetLine()).RecordType is "X"):
            self.IncLineCtr()

    #----------------------------------------------------------------------
    def SortComments(self, comment_list):
        if (comment_list == None):
            return {}
        ret_dict = {}
        for com in comment_list:
            dollar_pos = com.find("$")
            if (dollar_pos > 0):
                com_var = com[:dollar_pos]
                used_comment = com[dollar_pos + 1:].strip()
            else:
                com_var = "other"
                used_comment = com
            if com_var in ret_dict:
                ret_dict[com_var] += ("\n" + used_comment)
            else:
                ret_dict[com_var] = used_comment
        return ret_dict

    #----------------------------------------------------------------------
    def ParseContinuationField(self, fieldStr):
        cont_re = "([%A-Z0-9+-]+)=([+-]?\d+.\d+(?:[eE][+-]?\d+)?)(?: (\d+))?(?: \(([A-Z0-9,?]+)\))?"
        strParts = fieldStr.split("$")
        ret_list = []
        for part in strParts:
            part = part.strip()
            if (len(part) == 0):
                continue
            res = re.match(cont_re, part)
            if (res == None):
                raise Exception(self.MakeErrStr("ParseContinuationField(): Unable to match regular expression."))
            SA = None
            if (res.group(3) != None):
                SA = float(res.group(3))
            extraField = ContinuationField(TYPE = res.group(1), VAL = float(res.group(2)), VAL_SA = SA, Ref = res.group(4))
            extraField.save()
            print("ParseContinuationField(): Uncertainty in extra fields are not calculated correctly.")
            ret_list.append(extraField)
        return ret_list

    #----------------------------------------------------------------------
    def ParseLevelData(self, lvl_lines, lvl_com):
        lvl = lvl_lines[0].ljust(71)
        E = ToFloat(lvl[0:10])
        DE = ToFloat(lvl[10:12])
        J = ToStr(lvl[12:30])
        T, DT, isEV = ParseHalfLife(lvl[30:40], lvl[40:46])
        L = ToStr(lvl[46:55])
        S = ToStr(lvl[55:65])
        DS = ToStr(lvl[65:67])
        C = ToStr(lvl[67])
        MS = ToStr(lvl[68:70])
        if (L != None or S != None or DS != None or C != None or MS != None):
            raise Exception(self.MakeErrStr("ParseLevelData(): This part needs to be implemented."))
        Q = ToStr(lvl[70])

        extra_fields = []
        for i in range (1, len(lvl_lines)):
            extra_fields += self.ParseContinuationField(lvl_lines[i])

        cLevel = Level(E = E, ESA = DE, J = J, HalfLife = T, HalfLifeSA = DT, HalfLife_EV = isEV, L = L, S = S, SSA = DS, Uncertain = Q)
        cLevel.save()
        cLevel.ExtraFields.add(*extra_fields)
        sorted_comments = self.SortComments(lvl_com)
        for com_key in sorted_comments:
            if (com_key == "E"):
                cLevel.E_Com = sorted_comments[com_key]
            elif (com_key == "J"):
                cLevel.J_Com = sorted_comments[com_key]
            elif (com_key == "T"):
                cLevel.HalfLife_Com = sorted_comments[com_key]
            elif (com_key == "L"):
                cLevel.L_Com = sorted_comments[com_key]
            elif (com_key == "S"):
                cLevel.S_Com = sorted_comments[com_key]
            elif (com_key == "other"):
                cLevel.Comments = sorted_comments[com_key]
            else:
                found = False
                for extr in extra_fields:
                    if (extr.TYPE == com_key):
                        extr.Comments = sorted_comments[com_key]
                        extr.save()
                        found = True
                        break
                if (not found):
                    raise Exception(self.MakeErrStr("ParseLevelData(): Unable to determine comment type."))
        cLevel.save()


    #----------------------------------------------------------------------
    def ReadLevels(self):
        BaseComments = ""
        if (LineInfo(self.GetLine()).IsComment):
            BaseComments = "\n" + self.GetCommentLines("L")
        while (LineInfo(self.GetLine()).RecordType is "L"):
            lvl_lines = self.GetContRecord("L", AsList=True)
            lvl_com = self.GetCommentLines("L")
            self.ParseLevelData(lvl_lines, lvl_com + BaseComments)


