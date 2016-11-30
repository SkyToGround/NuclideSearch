# -*- coding: utf-8 -*-

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

from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, Http404
import sys
from Data.models import *
from NucStringConv import *
from numpy import array, empty, arange
from django.db.models import Max

def search(request):
	t = loader.get_template("adv_search.html")
	c = Context()
	return HttpResponse(t.render(c))

def time_multiplier(unit):
	time_dict = {"s":1.0, "m":60.0, "h":3600.0, "d":24*3600.0, "y":365.25*24*3600.0}
	if (time_dict.has_key(unit)):
		return time_dict[unit]
	raise ValueError("Time unit unknown: " + str(unit))

def get_value_from_dict(dictionary, key, default):
	if (dictionary.has_key(key)):
		return dictionary[key]
	return default

def assemble_hl_query(c_obj, GET):
	hl_start_unit = get_value_from_dict(GET, "hl_start_unit", "s")
	hl_stop_unit = get_value_from_dict(GET, "hl_stop_unit", "s")
	hl_start = float(get_value_from_dict(GET, "hl_start", 0))
	hl_stop = float(get_value_from_dict(GET, "hl_stop", sys.float_info.max))
	
	hl_start = hl_start * time_multiplier(hl_start_unit)
	hl_stop = hl_stop * time_multiplier(hl_stop_unit)
	return c_obj.filter(TSek__gt = hl_start, TSek__lt = hl_stop)

def assemble_mass_query(c_obj, GET):
	if (GET.has_key("mass_low") and GET.has_key("mass_high")):
		return c_obj.filter(A__gte = int(GET["mass_low"]), A__lte = int(GET["mass_high"]))
	elif (GET.has_key("mass_low")):
		return c_obj.filter(A = int(GET["mass_low"]))
	return c_obj.filter(A = int(GET["mass_high"]))

def assemble_elem_query(c_obj, GET):
	start_z = -1
	stop_z = -1
	if (GET.has_key("strt_symb")):
		t_res = Parents.objects.filter(Symb__iexact = GET["strt_symb"])[0]
		start_z = int(t_res.Z)
	if (GET.has_key("strt_z")):
		start_z = int(GET["strt_z"])
	if (GET.has_key("stop_symb")):
		t_res = Parents.objects.filter(Symb__iexact = GET["stop_symb"])[0]
		stop_z = int(t_res.Z)
	if (GET.has_key("stop_z")):
		stop_z = int(GET["stop_z"])
	if (start_z != -1 and stop_z != -1 and start_z <= stop_z):
		return c_obj.filter(Z__lte = stop_z, Z_gte = start_z)
	elif (start_z != -1 and stop_z == -1):
		return c_obj.filter(Z = start_z)
	elif (stop_z == -1 and stop_z != -1):
		return c_obj.filter(Z = stop_z)
	return c_obj.none()

def filter_rad(query_res, iza_list):
	return (item for item in query_res if item.iZA in iza_list)

def do_alpha_query(iZA_list, en):
	low_en = en["en"] - en["pm"]
	high_en = en["en"] + en["pm"]
	table_en_list = []
	table_en_str_list = []
	table_int_list = []
	table_int_str_list = []
	iza_list = []
	if (en["int_type"] == "abs"):
		res = None
		if (en["int_dir"] == "gt"):
			res = Alphas.objects.filter(Ea__gte = low_en, Ea__lte = high_en, Ia__gte = en["int"])
		else:
			res = Alphas.objects.filter(Ea__gte = low_en, Ea__lte = high_en, Ia__lte = en["int"])
		res = filter_rad(res, iZA_list)
		for nuc in res:
			if(iza_list.count(nuc.iZA) > 0):
				c_index = iza_list.index(nuc.iZA)
				if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Ea - en["en"])):
					table_en_list[c_index] = nuc.Ea
					table_en_str_list[c_index] = nuc.EaStr
					table_int_list[c_index] = nuc.Ia
					table_int_str_list[c_index] = nuc.IaStr
				else:
					pass
			else:
				iza_list.append(nuc.iZA)
				table_en_list.append(nuc.Ea)
				table_en_str_list.append(nuc.EaStr)
				table_int_list.append(nuc.Ia)
				table_int_str_list.append(nuc.IaStr)
	else:
		res = Alphas.objects.filter(Ea__gte = low_en, Ea__lte = high_en)
		res = filter_rad(res, iZA_list)
		for nuc in res:
			res2 = Alphas.objects.filter(iZA = nuc.iZA).aggregate(Max('Ia'))
			comp_int = (nuc.Ia / res2["Ia__max"]) * 100.0
			if ((en["int_dir"] == "gt" and en["int"] <= comp_int) or (en["int_dir"] == "lt" and en["int"] >= comp_int)):
				if(iza_list.count(nuc.iZA) > 0):
					c_index = iza_list.index(nuc.iZA)
					if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Ea - en["en"])):
						table_en_list[c_index] = nuc.Ea
						table_en_str_list[c_index] = nuc.EaStr
						table_int_list[c_index] = comp_int
						table_int_str_list[c_index] = "%.1f" % comp_int
					else:
						pass
				else:
					iza_list.append(nuc.iZA)
					table_en_list.append(nuc.Ea)
					table_en_str_list.append(nuc.EaStr)
					table_int_list.append(comp_int)
					table_int_str_list.append("%.1f" % comp_int)
	ret_table_data = {"iza":iza_list, "en":table_en_list, "en_str":table_en_str_list, "int":table_int_list, "int_str":table_int_str_list}
	return iza_list, ret_table_data

def do_gamma_query(iZA_list, en):
	low_en = en["en"] - en["pm"]
	high_en = en["en"] + en["pm"]
	table_en_list = []
	table_en_str_list = []
	table_int_list = []
	table_int_str_list = []
	iza_list = []
	if (en["int_type"] == "abs"):
		res = None
		if (en["int_dir"] == "gt"):
			res = Gammas.objects.filter(Eg__gte = low_en, Eg__lte = high_en, Ig__gte = en["int"]) 
		else:
			res = Gammas.objects.filter(Eg__gte = low_en, Eg__lte = high_en, Ig__lte = en["int"])
		res = filter_rad(res, iZA_list)
		for nuc in res:
			if(iza_list.count(nuc.iZA) > 0):
				c_index = iza_list.index(nuc.iZA)
				if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Eg - en["en"])):
					table_en_list[c_index] = nuc.Eg
					table_en_str_list[c_index] = nuc.EgStr
					table_int_list[c_index] = nuc.Ig
					table_int_str_list[c_index] = nuc.IgStr
				else:
					pass
			else:
				iza_list.append(nuc.iZA)
				table_en_list.append(nuc.Eg)
				table_en_str_list.append(nuc.EgStr)
				table_int_list.append(nuc.Ig)
				table_int_str_list.append(nuc.IgStr)
	else:
		res = None
		if (en["int_dir"] == "gt"):
			res = Gammas.objects.filter(Eg__gte = low_en, Eg__lte = high_en, IgRel__gte = en["int"]) 
		else:
			res = Gammas.objects.filter(Eg__gte = low_en, Eg__lte = high_en, IgRel__lte = en["int"])
		res = filter_rad(res, iZA_list)
		for nuc in res:
			if(iza_list.count(nuc.iZA) > 0):
				c_index = iza_list.index(nuc.iZA)
				if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Eg - en["en"])):
					table_en_list[c_index] = nuc.Eg
					table_en_str_list[c_index] = nuc.EgStr
					table_int_list[c_index] = nuc.IgRel
					table_int_str_list[c_index] = nuc.IgRel
				else:
					pass
			else:
				iza_list.append(nuc.iZA)
				table_en_list.append(nuc.Eg)
				table_en_str_list.append(nuc.EgStr)
				table_int_list.append(nuc.IgRel)
				table_int_str_list.append(nuc.IgRel)
		# res = Gammas.objects.filter(Eg__gte = low_en, Eg__lte = high_en)
		# res = filter_rad(res, iZA_list)
		# for nuc in res:
		# 	res2 = Gammas.objects.filter(iZA = nuc.iZA).aggregate(Max('Ig'))
		# 	if (res2["Ig__max"] == 0 or res2["Ig__max"] == None):
		# 		continue
		# 	comp_int = (nuc.Ig / res2["Ig__max"]) * 100.0
		# 	if ((en["int_dir"] == "gt" and en["int"] <= comp_int) or (en["int_dir"] == "lt" and en["int"] >= comp_int)):
		# 		if(iza_list.count(nuc.iZA) > 0):
		# 			c_index = iza_list.index(nuc.iZA)
		# 			if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Eg - en["en"])):
		# 				table_en_list[c_index] = nuc.Eg
		# 				table_en_str_list[c_index] = nuc.EgStr
		# 				table_int_list[c_index] = comp_int
		# 				table_int_str_list[c_index] = "%.1f" % comp_int
		# 			else:
		# 				pass
		# 		else:
		# 			iza_list.append(nuc.iZA)
		# 			table_en_list.append(nuc.Eg)
		# 			table_en_str_list.append(nuc.EgStr)
		# 			table_int_list.append(comp_int)
		# 			table_int_str_list.append("%.1f" % comp_int)
	ret_table_data = {"iza":iza_list, "en":table_en_list, "en_str":table_en_str_list, "int":table_int_list, "int_str":table_int_str_list}
	return iza_list, ret_table_data

def do_beta_query(iZA_list, en):
	low_en = en["en"] - en["pm"]
	high_en = en["en"] + en["pm"]
	table_en_list = []
	table_en_str_list = []
	table_int_list = []
	table_int_str_list = []
	iza_list = []
	if (en["int_type"] == "abs"):
		res = None
		if (en["int_dir"] == "gt"):
			res = Betas.objects.filter(Eb__gte = low_en, Eb__lte = high_en, Ib__gte = en["int"])
		else:
			res = Betas.objects.filter(Eb__gte = low_en, Eb__lte = high_en, Ib__lte = en["int"])
		res = filter_rad(res, iZA_list)
		for nuc in res:
			if(iza_list.count(nuc.iZA) > 0):
				c_index = iza_list.index(nuc.iZA)
				if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Eb - en["en"])):
					table_en_list[c_index] = nuc.Eb
					table_en_str_list[c_index] = str(nuc.Eb)
					table_int_list[c_index] = nuc.Ib
					table_int_str_list[c_index] = nuc.IbStr
				else:
					pass
			else:
				iza_list.append(nuc.iZA)
				table_en_list.append(nuc.Eb)
				table_en_str_list.append(str(nuc.Eb))
				table_int_list.append(nuc.Ib)
				table_int_str_list.append(nuc.IbStr)
	else:
		res = Betas.objects.filter(Eb__gte = low_en, Eb__lte = high_en)
		res = filter_rad(res, iZA_list)
		for nuc in res:
			res2 = Betas.objects.filter(iZA = nuc.iZA).aggregate(Max('Ib'))
			comp_int = (nuc.Ib / res2["Ib__max"]) * 100.0
			if ((en["int_dir"] == "gt" and en["int"] <= comp_int) or (en["int_dir"] == "lt" and en["int"] >= comp_int)):
				if(iza_list.count(nuc.iZA) > 0):
					c_index = iza_list.index(nuc.iZA)
					if (abs(table_en_list[c_index] - en["en"]) > abs(nuc.Eb - en["en"])):
						table_en_list[c_index] = nuc.Eb
						table_en_str_list[c_index] = str(nuc.Eb)
						table_int_list[c_index] = comp_int
						table_int_str_list[c_index] = "%.1f" % comp_int
					else:
						pass
				else:
					iza_list.append(nuc.iZA)
					table_en_list.append(nuc.Eb)
					table_en_str_list.append(str(nuc.Eb))
					table_int_list.append(comp_int)
					table_int_str_list.append("%.1f" % comp_int)
	ret_table_data = {"iza":iza_list, "en":table_en_list, "en_str":table_en_str_list, "int":table_int_list, "int_str":table_int_str_list}
	return iza_list, ret_table_data

def assemble_do_energy_query(c_obj, GET):
	list_of_iza = []
	for p in c_obj:
		list_of_iza.append(p.iZA)
	list_of_en = []
	for i in range(1,4):
		if (GET.has_key("rad_en_" + str(i))):
			trgt_dict = {"en":float(GET["rad_en_" + str(i)]), "type":"a", "pm":10.0, "int_type":"rel", "int":0.0, "int_dir":"gt"}
			if (GET.has_key("rad_pm_" + str(i))):
				trgt_dict["pm"] = float(GET["rad_pm_" + str(i)])
			if (GET.has_key("rad_int_dir_" + str(i))):
				trgt_dict["int_dir"] = GET["rad_int_dir_" + str(i)]
			if (GET.has_key("rad_int_" + str(i))):
				trgt_dict["int"] = float(GET["rad_int_" + str(i)])
			if (GET.has_key("rad_type_" + str(i))):
				trgt_dict["type"] = GET["rad_type_" + str(i)]
			if (GET.has_key("rad_int_type_" + str(i))):
				trgt_dict["int_type"] = (GET["rad_int_type_" + str(i)])
			list_of_en.append(trgt_dict)
	temp_table_data = []
	col_titles = []
	rad_dict = {"a":u"\u03b1","b":u"\u03b2", "g":u"\u03b3", "x":"X-ray"}
	for en in list_of_en:
		if (en["type"] == "a"):
			list_of_iza, table_data = do_alpha_query(list_of_iza, en)
		elif (en["type"] == "b"):
			list_of_iza, table_data = do_beta_query(list_of_iza, en)
		elif (en["type"] == "x"):
			list_of_iza, table_data = do_xray_query(list_of_iza, en)
		elif (en["type"] == "g"):
			list_of_iza, table_data = do_gamma_query(list_of_iza, en)
		if (len(list_of_en) > 1):
			col_titles.append(rad_dict[en["type"]] + " energy (keV) <br><font class='int_font'>" + "Intensity (%)</font>")
		else:
			col_titles.append(rad_dict[en["type"]] + " energy (keV)")
			col_titles.append("Intensity (%)")
		temp_table_data.append(table_data)
	target_table_data = []
	if (len(list_of_en) == 1):
		temp_en_col = {}
		temp_int_col = {}
		en_order = array(temp_table_data[0]["en"]).argsort().argsort()
		int_order = array(temp_table_data[0]["int"]).argsort().argsort()
		for i in range(len(temp_table_data[0]["iza"])):
			temp_en_col[temp_table_data[0]["iza"][i]] = {"value":temp_table_data[0]["en_str"][i], "order":en_order[i]}
			temp_int_col[temp_table_data[0]["iza"][i]] = {"value":temp_table_data[0]["int_str"][i], "order":int_order[i]}
		target_table_data.append(temp_en_col)
		target_table_data.append(temp_int_col)
	else:
		for k in range(len(temp_table_data)):
			temp_en_col = {}
			en_order = array(temp_table_data[k]["en"]).argsort().argsort()
			for i in range(len(temp_table_data[k]["iza"])):
				value_str = temp_table_data[k]["en_str"][i] + "<br><font class='int_font'>" + temp_table_data[k]["int_str"][i] + "</font>"
				temp_en_col[temp_table_data[k]["iza"][i]] = {"value":value_str, "order":en_order[i]}
			target_table_data.append(temp_en_col)
	
	return c_obj.filter(iZA__in = list_of_iza), col_titles, target_table_data
	
def search_res(request):
	if (len(request.GET) == 0):
		t = loader.get_template("adv_search_res.html")
		c = RequestContext(request, {"search_match":"Found no matches", })
		return HttpResponse(t.render(c))
	extra_columns = []
	extra_col_data = []
	c_parents = Parents.objects.all()
	if (request.GET.has_key("hl_start") or request.GET.has_key("hl_stop")):
		c_parents = assemble_hl_query(c_parents, request.GET)
	if (request.GET.has_key("mass_low") or request.GET.has_key("mass_high")):
		c_parents = assemble_mass_query(c_parents, request.GET)
	if (request.GET.has_key("strt_symb") or request.GET.has_key("strt_z") or request.GET.has_key("stop_symb") or request.GET.has_key("stop_z")):
		c_parents = assemble_elem_query(c_parents, request.GET)
	if (request.GET.has_key("rad_en_1") or request.GET.has_key("rad_en_2") or request.GET.has_key("rad_en_3")):
		c_parents, column_titles, column_data = assemble_do_energy_query(c_parents, request.GET)
		for c in column_titles:
			extra_columns.append(c)
		for c_dat in column_data:
			extra_col_data.append(c_dat)
			
	
	matches_string = "No matches found"
	found_matches = False
	if (len(c_parents) > 0):
		matches_string = "Found " + str(len(c_parents)) + " matches"
		found_matches = True
	result = []
	
	c_parents.order_by("A", "Z")
	name_list = []
	name_order = arange(len(c_parents))
	decay_mode_list = []
	hl_str = []
	hl_value = empty(len(c_parents))
	iZA_list = []
	for i in range(len(c_parents)):
		c_iZA = c_parents[i].iZA
		name_list.append(iZA_to_string(c_iZA))
		decay_mode_list.append(assemble_mode_str(c_iZA))
		hl_str.append(c_parents[i].TStr)
		hl_value[i] = c_parents[i].TSek
		iZA_list.append(c_iZA)
	
	hl_order = hl_value.argsort().argsort()
	
	items_per_page = 50
	page = 0
	stop_index = (page + 1) * items_per_page
	if (stop_index > len(c_parents)):
		stop_index = len(c_parents)
	
	for i in range(page * items_per_page, stop_index):
		row_dict = {"name":name_list[i], "name_order":name_order[i], "mode":decay_mode_list[i], "halflife":hl_str[i], "halflife_order":hl_order[i], "iZA":iZA_list[i]}
		temp_list = []
		for c_col in extra_col_data:
			if (c_col[iZA_list[i]].has_key("order")):
				temp_list.append({"value_str":c_col[iZA_list[i]]["value"], "order":c_col[iZA_list[i]]["order"]})
			else:
				temp_list.append({"value_str":c_col[iZA_list[i]]["value"],})
		row_dict["extra_values"] = temp_list
		result.append(row_dict)
	
	t = loader.get_template("adv_search_res.html")
	c = RequestContext(request, {"matches_string":matches_string, "found_matches":found_matches, "extra_columns":extra_columns, "result_list":result})
	return HttpResponse(t.render(c))
		