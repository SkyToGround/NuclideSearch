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
from django.shortcuts import redirect
from NucStringConv import *
from Data.models import *
from numpy import empty, array
import json
import re

def is_value_number(value):
	try:
		float(value)
	except ValueError:
		return False
	return True

def is_value_int(value):
	try:
		int(value)
	except ValueError:
		return False
	return True

def par_list_to_nuc_list(par_list, gammas = None):
	ret_list = []
	hl_arr = empty(len(par_list))
	ctr = 0
	for p in par_list:
		hl_arr[ctr] = p.TSek
		ctr += 1
	hl_order = hl_arr.argsort().argsort()
	if (gammas != None):
		gamma_order = array(gammas).argsort().argsort()
	ctr = 0
	for p in par_list:
		temp_dict = {"mode":assemble_mode_str(p.iZA), "halflife":p.TStr, "halflife_order":hl_order[ctr], "name":iZA_to_string(p.iZA), "name_order":ctr, "iZA":p.iZA}
		if (gammas != None):
			temp_dict["gamma"] = gammas[ctr]
			temp_dict["gamma_order"] = gamma_order[ctr]
		ctr += 1
		ret_list.append(temp_dict)
	return ret_list
	

def find_nuclides(symb, A, meta = None, symbol_complete = False, limit_response = True):
	parents_by_symbol = None
	if (len(A) > 0 or symbol_complete):
		parents_by_symbol = Parents.objects.filter(Symb__iexact = symb, TSek__lt = 1e30).order_by("-TSek").filter()
	else:
		parents_by_symbol = Parents.objects.filter(Symb__istartswith = symb, TSek__lt = 1e30).order_by("-TSek").filter()
	final_list = []
	ctr = 0
	if (len(A) > 0 and len(parents_by_symbol) > 0):
		for par in parents_by_symbol:
			c_A = str(par.A)
			meta_stable = ""
			if (A == c_A[:len(A)]):
				mode_str = "Mode: " + assemble_mode_str(par.iZA)
				final_list.append({"value":iZA_to_string(par.iZA), "desc":"Half-life: " + str(par.TStr), "extra":mode_str, "url":"/show_nuclide/" + str(par.iZA)})
				ctr += 1
			if (ctr >= 5):
				break
	else:
		for par in parents_by_symbol:
			mode_str = "Mode: " + assemble_mode_str(par.iZA)
			final_list.append({"value":iZA_to_string(par.iZA), "desc":"Half-life: " + str(par.TStr), "extra":mode_str, "url":"/show_nuclide/" + str(par.iZA)})
			ctr += 1
			if (ctr >= 5):
				break
	return final_list
	

def handle_nuclide_str(value):
	nuclide_re1 = re.compile("([A-Za-z]{1,2})([- ]{0,1})([0-9]{0,3})([mM]{0,1})")
	res = re.match(nuclide_re1, value)
	if (res != None):
		return find_nuclides(res.group(1), res.group(3), res.group(4), len(res.group(2)) > 0)
	
	nuclide_re1 = re.compile("([0-9]{1,3})([A-Za-z]{1,2})")
	res = re.match(nuclide_re1, value)
	if (res != None):
		return find_nuclides(res.group(2), res.group(1), "")
	
	nuclide_re1 = re.compile("([A-Za-z]{2,30})([- ]{0,1})([0-9]{1,3})([mM]{0,1})")
	res = re.match(nuclide_re1, value)
	if (res != None):
		return find_nuclides(res.group(1), res.group(3), res.group(4), len(res.group(2)) > 0)
	
	return []
	
def auto_complete_query(request, search_term):
	ret_list = []
	if (is_value_int(search_term)):
		if (int(search_term) > 2 and int(search_term) < 260):
			ret_list.append({"value":"A = " + str(search_term), "extra":"", "desc":"List nuclides with mass " + str(search_term), "url":"/search/?query=A=" + str(search_term)})
	if (is_value_number(search_term)):
		if (float(search_term) > 0):
			ret_list.append({"value":"Energy = " + str(search_term) + " keV", "extra":"", "desc":"List nuclides with radiation energies near " + str(search_term), "url":"/search/?query=E=" + str(search_term) + " keV"})
	nuclide_list_res = handle_nuclide_str(search_term)
	for nuc in nuclide_list_res:
		ret_list.append(nuc)
	return HttpResponse(json.dumps(ret_list), content_type="text/plain")

def isotopes_query(query):
	ret_list = []
	reg_exp_res = re.match("([A-Za-z]{1,3})([- ]{0,1})([0-9]{0,3})([mM]{0,1})$", query)
	alt_reg_exp_res = re.match("([0-9]{1,3})([mM]{0,1})([A-Za-z]{1,3})$", query)
	if (not reg_exp_res and not alt_reg_exp_res):
		z_reg_exp_res = re.match("^[zZ]{1}[ ]?=[ ]?(\d{1,3})", query)
		if (z_reg_exp_res):
			c_z = int(z_reg_exp_res.group(1))
			z_parents = Parents.objects.filter(Z = c_z).exclude(A = 0).order_by("Z")
			return par_list_to_nuc_list(z_parents)
		return ret_list
	if (reg_exp_res):
		symb_part = reg_exp_res.group(1)
		mass_part = reg_exp_res.group(3)
	else:
		symb_part = alt_reg_exp_res.group(3)
		mass_part = alt_reg_exp_res.group(1)
	if (mass_part != ""):
		parents_by_symbol = Parents.objects.filter(Symb__iexact = symb_part, A__istartswith = mass_part).exclude(A = 0).order_by("TSek")
	else:
		parents_by_symbol = Parents.objects.filter(Symb__iexact = symb_part).exclude(A = 0)
	return par_list_to_nuc_list(parents_by_symbol.order_by("A"))

def nuclides_query(query):
	ret_list = []
	reg_exp_res = re.match("(?:[Aa]{1}?[ =]{1,4})?([0-9]{1,3})[ ]*$", query)
	if (reg_exp_res):
		parents_by_symbol = Parents.objects.filter(A = reg_exp_res.group(1)).order_by("Z")
		ret_list = par_list_to_nuc_list(parents_by_symbol)
	return ret_list

def time_query(query):
	ret_list = []
	query = query.lower()
	desc_str = ""
	time = 0
	reg_exp_res_sec = re.match("([0-9]+)[ ]*(s|se|sec|seco|secon|second|seconds)[ ]*$", query)
	reg_exp_res_min = re.match("([0-9]+)[ ]*(m|mi|min|minu|minut|minute|minutes)[ ]*$", query)
	reg_exp_res_hour = re.match("([0-9]+)[ ]*(h|ho|hou|hour|hours)[ ]*$", query)
	reg_exp_res_day = re.match("([0-9]+)[ ]*(d|da|day|days)[ ]*$", query)
	reg_exp_res_year = re.match("([0-9]+)[ ]*(y|ye|yea|year|years)[ ]*$", query)
	if (reg_exp_res_sec):
		time = int(reg_exp_res_sec.group(1))
		desc_str = reg_exp_res_sec.group(1) + u"\u00b110% seconds"
	elif (reg_exp_res_min):
		time = int(reg_exp_res_min.group(1)) * 60
		desc_str = reg_exp_res_min.group(1) + u"\u00b110% minutes"
	elif (reg_exp_res_hour):
		time = int(reg_exp_res_hour.group(1)) * 60 * 60
		desc_str = reg_exp_res_hour.group(1) + u"\u00b110% hours"
	elif (reg_exp_res_day):
		time = int(reg_exp_res_day.group(1)) * 60 * 60 * 24
		desc_str = reg_exp_res_day.group(1) + u"\u00b110% days"
	elif (reg_exp_res_year):
		time = float(reg_exp_res_year.group(1)) * 60 * 60 * 24 * 365.242
		desc_str = reg_exp_res_year.group(1) + u"\u00b110% years"
	else:
		return ret_list, desc_str
	desc_str = "Nuclides with a half-life of " + desc_str
	parents_by_half = Parents.objects.filter(TSek__gt = time * 0.9, TSek__lt = time * 1.1).order_by("TSek")
	return par_list_to_nuc_list(parents_by_half), desc_str

def filter_rad(query_res, iza_list):
	return (item for item in query_res if item.iZA in iza_list)

def energy_query(query):
	ret_list = []
	desc_str = ""
	query = query.lower()
	energy = 0
	is_mev = False
	reg_exp = re.match("^(?:[Ee]{1}[ =]{1,3})?([0-9]+[.]?[0-9]*)[ ]*(kev)[ ]*$", query, flags = re.IGNORECASE)
	if (not reg_exp):
		return [], desc_str
	energy = float(reg_exp.group(1))
	gammas = Gammas.objects.filter(Eg__gte = energy - 1.0, Eg__lte = energy + 1.0)
	iza_dict = {}
	for g in gammas:
		iza_dict[g.iZA] = g.Eg
	par = Parents.objects.filter(iZA__in = iza_dict).order_by("A")
	#par = filter_rad(par, iza_dict)
	target_list = []
	for p in par:
		target_list.append(iza_dict[p.iZA])
	desc_str = u"Nuclides with \u03B3-emissions of " + reg_exp.group(1) + u"\u00b11 keV"
	return par_list_to_nuc_list(par, target_list), desc_str

def search(request):
	value_str = ""
	isotopes = []
	nuclides = []
	energies = []
	energy_desc = ""
	times = []
	times_desc = ""
	element = "n/a"
	Z = ""
	if ("query" in request.GET):
		value_str = str(request.GET["query"])
		isotopes = isotopes_query(value_str)
		if (len(isotopes) > 0):
			element = iZA_to_element(isotopes[0]["iZA"])
			Z = iZA_to_Z(isotopes[0]["iZA"])
		nuclides = nuclides_query(value_str)
		energies, energy_desc = energy_query(value_str)
		times, times_desc = time_query(value_str)
		new_list = isotopes + nuclides + energies + times
		if (len(new_list) == 1):
			return redirect("/show_nuclide/" + str(new_list[0]["iZA"]) + "/")
	t = loader.get_template("search.html")
	c = RequestContext(request, {"value_str":value_str, "template":"<a href=\"{{{url}}}\" class=\"search-value\">{{{value}}}</a> <p class=\"search-extra\">{{{extra}}}</p> <p class=\"search-description\">{{{desc}}}</p>", "nuclides":nuclides, "isotopes":isotopes, "energies":energies, "times":times, "times_desc":times_desc, "energies_desc":energy_desc, "element":element, "Z":Z})
	return HttpResponse(t.render(c))
