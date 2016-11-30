#!/Library/Frameworks/Python.framework/Versions/2.7/bin/python
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

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.conf import settings
from Data.models import Alphas, Betas, Gammas, XRays, XIntensities, Parents, Parents2, Status, Production, References, EvaluationCitation, Augers
import StringIO
import subprocess
import csv
import timeit
from django.db.models import Max

def import_alphas():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "alphas"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Alphas.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		new_objects.append(Alphas(iZA = int(values[0]), Foot = str(values[1][1:-1]), Ea = float(values[2]), EaStr = str(values[3][1:-1]), Ia = float(values[4]), IaStr = str(values[5][1:-1])))
		c_line += 1
	Alphas.objects.bulk_create(new_objects)

def import_betas():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "betas"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Betas.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		new_objects.append(Betas(iZA = int(values[0]), Mode = str(values[1][1:-1]), Eb = float(values[2]), Ib = float(values[3]), IbStr = str(values[4][1:-1])))
		c_line += 1
	Betas.objects.bulk_create(new_objects)

def import_gammas():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "gammas"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Gammas.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		Ig_temp = None
		try:
			Ig_temp = float(values[4])
		except ValueError:
			pass
		new_objects.append(Gammas(iZA = int(values[0]), Foot = str(values[1][1:-1]), Eg = float(values[2]), EgStr = str(values[3][1:-1]), Ig = Ig_temp, IgStr = str(values[5][1:-1]), Mode = str(values[6][1:-1])))
		c_line += 1
	Gammas.objects.bulk_create(new_objects)

def import_xrays_part1():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "XRays"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	XRays.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		L1Int_temp = None
		L2Int_temp = None
		L3Int_temp = None
		Kint_temp = None
		try:
			L1Int_temp = float(values[7])
			L2Int_temp = float(values[9])
			L3Int_temp = float(values[1])
		except ValueError:
			pass
		try:
			Kint_temp = float(values[5])
		except ValueError:
			pass
		
		try:
			new_objects.append(XRays(XCode = int(values[0]), Z = int(values[1]), Energy = float(values[2]), Element = str(values[3][1:-1]), Assignment = str(values[4][1:-1]), Kint = Kint_temp, KintStr = str(values[6][1:-1]), L1Int = L1Int_temp, L1IntStr = str(values[8][1:-1]), L2Int = L2Int_temp, L2IntStr = str(values[10][1:-1]), L3Int = L3Int_temp, L3IntStr = str(values[12][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	XRays.objects.bulk_create(new_objects)

def import_xrays_part2():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "XIntensities"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	XIntensities.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		try:
			new_objects.append(XIntensities(iZA = int(values[0]), XCode = int(values[1]), Int = float(values[2]), IntStr = str(values[3][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	XIntensities.objects.bulk_create(new_objects)

def import_production():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "production"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Production.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		try:
			new_objects.append(Production(iZA = int(values[0]), GenShort = str(values[1][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	Production.objects.bulk_create(new_objects)

def import_parents_part1():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "parents"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Parents.objects.all().delete()
	new_objects = []
	for line in lines:
		values = fix_values(line.split(","))
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		El_temp = None
		TSek_temp = None
		Abund_temp = None
		try:
			El_temp = float(values[4])
			TSek_temp = float(values[6])
			Abund_temp = float(values[9])
		except ValueError:
			pass
		try:
			new_objects.append(Parents(A = int(values[0]), Z = int(values[1]), Symb = str(values[2][1:-1]), iZA = int(values[3]), El = El_temp, ElStr = str(values[5][1:-1]), TSek = TSek_temp, TStr = str(values[7][1:-1]), JPi = str(values[8][1:-1]), Abund = Abund_temp, AbundStr = str(values[10][1:-1]), SnStr = str(values[11][1:-1]), SpStr = str(values[12][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	Parents.objects.bulk_create(new_objects)

def import_parents_part2():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "parents2"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Parents2.objects.all().delete()
	new_objects = []
	for line in lines:
		values = fix_values(line.split(","))
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		DSID_temp = None
		try:
			DSID_temp = str(values[2][1:-1])
		except ValueError:
			pass
		
		Spec_temp = None
		try:
			Spec_temp = str(values[3][1:-1])
		except ValueError:
			pass
		
		Perc_temp = None
		try:
			Perc_temp = float(values[5])
		except ValueError:
			pass
		try:
			new_objects.append(Parents2(iZA = int(values[0]), nMode = int(values[1]), DSID = DSID_temp, Spec = Spec_temp, Mode = str(values[4][1:-1]), Perc = Perc_temp, PercStr = str(values[6][1:-1]), QStr = str(values[7][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	Parents2.objects.bulk_create(new_objects)

def import_status():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "Status"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Status.objects.all().delete()
	new_objects = []
	from datetime import datetime
	for line in lines:
		if (len(line) == 0):
			break
		temp_values = line.split(",")
		values = fix_values(temp_values)
		try:
			new_objects.append(Status(DatabaseID = str(values[0][1:-1]), BuildDate = datetime.strptime(values[1][1:-1], "%m/%d/%y %H:%M:%S"), Remarks = values[2]))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	Status.objects.bulk_create(new_objects)

def fix_values(value_list):
	target_list = []
	temp_value = ""
	working_on_string = False
	for value in value_list:
		if (working_on_string):
			if (value[-1] == "\""):
				temp_value = temp_value + value[0:-1]
				target_list.append(temp_value)
				working_on_string = False
			else:
				temp_value = temp_value + value
		else:
			if (len(value) < 2):
				target_list.append(value)
			elif (value[0] == "\"" and value[-1] == "\""):
				target_list.append(value)
			elif (value[0] == "\""):
				working_on_string = True
				temp_value = value[1:]
			else:
				target_list.append(value)
	return target_list

def import_references():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "references"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	References.objects.all().delete()
	new_objects = []
	for line in lines:
		values = fix_values(line.split(","))
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		try:
			new_objects.append(References(iZA = int(values[0]), KeyNo = str(values[1])[1:-1], Mode = int(values[2])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	References.objects.bulk_create(new_objects)

def import_eval_cit():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "EvaluationCitation"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	EvaluationCitation.objects.all().delete()
	new_objects = []
	for line in lines:
		values = fix_values(line.split(","))
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		try:
			temp_cit = str(values[3])
			if (temp_cit[0] == "\""):
				temp_cit = temp_cit[1:]
			if (temp_cit[-1] == "\""):
				temp_cit = temp_cit[0:-1]
			temp_auth = str(values[5])
			if (len(temp_auth) > 0):
				if (temp_auth[0] == "\""):
					temp_auth = temp_auth[1:]
				if (temp_auth[-1] == "\""):
					temp_auth = temp_auth[0:-1]
			new_objects.append(EvaluationCitation(A = int(values[0]), Symb = str(values[1])[1:-1], Update = int(values[2]), Citation = temp_cit, PubDate = str(values[4])[1:-1], Authors = temp_auth))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	EvaluationCitation.objects.bulk_create(new_objects)

def import_augers():
	result = subprocess.check_output(["mdb-export", "-H", "legacy_db.mdb", "Augers"])
	lines = result.split("\n")
	columns = -1
	c_line = 0
	Augers.objects.all().delete()
	new_objects = []
	for line in lines:
		values = line.split(",")
		if (columns == -1):
			columns = len(values)
		elif (columns != len(values)):
			print "Incorrect number of columns encountered. Is it a misplaced \",\"? Exiting at row " + str(c_line) + " of " + str(len(lines))
			break
		L1Int_temp = None
		L2Int_temp = None
		L3Int_temp = None
		Kint_temp = None
		try:
			L1Int_temp = float(values[7])
			L2Int_temp = float(values[9])
			L3Int_temp = float(values[1])
		except ValueError:
			pass
		try:
			Kint_temp = float(values[5])
		except ValueError:
			pass
		
		try:
			new_objects.append(Augers(ACode = int(values[0]), Z = int(values[1]), Energy = float(values[2]), Element = str(values[3][1:-1]), Assignment = str(values[4][1:-1]), Kint = Kint_temp, KintStr = str(values[6][1:-1]), L1Int = L1Int_temp, L1IntStr = str(values[8][1:-1]), L2Int = L2Int_temp, L2IntStr = str(values[10][1:-1]), L3Int = L3Int_temp, L3IntStr = str(values[12][1:-1])))
		except ValueError:
			print "Failed with line: ", line
		c_line += 1
	Augers.objects.bulk_create(new_objects)

def fix_rel_gammas():
	all_iZAs = Parents.objects.all().values("iZA")
	total = len(all_iZAs)
	ctr = 0
	for iza in all_iZAs:
		c_iZA = iza["iZA"]
		c_gammas = Gammas.objects.filter(iZA = c_iZA)
		max_value = c_gammas.aggregate(Max('Ig'))
		try:
			for gm in c_gammas:
				gm.IgRel = (gm.Ig / max_value["Ig__max"]) * 100.0
				gm.save()
		except:
			print "Failed with iZA: ", c_iZA
		
		if (ctr % 100 == 0):
			print str(ctr) + " items of" + str(total) + " done."
		ctr += 1
		

def main():
	# import_alphas()
	# import_betas()
	# import_gammas()
	# import_xrays_part1()
	# import_xrays_part2()
	# import_parents_part1()
	# import_parents_part2()
	# import_status()
	# import_production()
	# import_references()
	# import_eval_cit()
	# import_augers()
	fix_rel_gammas()
	
	
if __name__ == '__main__':
	main()
