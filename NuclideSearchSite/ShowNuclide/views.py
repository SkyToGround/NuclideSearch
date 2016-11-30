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
from NucStringConv import iZA_to_string, iZA_to_html, iZA_to_meta, to_nice_mode, assemble_mode_str, iZA_to_element
from Data.models import Gammas, Betas, Alphas, Parents2, Parents, XIntensities, Production, EvaluationCitation, References, XRays
from numpy import array
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

def add_if_exists(list, name, value):
	try:
		if (len(value) == 0):
			return
	except:
		pass
	list.append({"key":name + ":", "value":value})

def nice_prod_str(in_str):
	prod_dict = {"-":"", "N":"Naturally occurring", "C":"Charged particle reaction", "P":"Photon reaction", "F":"Fast neutron activation", "I":"Fission product", "T":"Thermal neutron activation"}
	target_str = ""
	for i in range(len(in_str)):
		target_str = target_str + prod_dict[in_str[i]] + "<br>"
	return target_str[0:-4]

def show_nuclide(request, iZA):
	iZA = int(iZA)
	parent_data = None
	try:
		parent_data = Parents.objects.get(iZA = iZA)
	except Parents.DoesNotExist as e:
		raise Http404
	
	nuclide_str = iZA_to_string(iZA)
	nuclide_str_pretty = iZA_to_html(iZA)
	gammas = Gammas.objects.filter(iZA = iZA)
	betas = Betas.objects.filter(iZA = iZA)
	alphas = Alphas.objects.filter(iZA = iZA)
	
	
	info = []
	add_if_exists(info, "Half-life", parent_data.TStr)
	if (parent_data.El != 0.0):
		add_if_exists(info, "Excitation level (keV)", parent_data.ElStr)
	add_if_exists(info, "Nuclear spin, J<sup>&#960;</sup>", parent_data.JPi)
	add_if_exists(info, "N. sep. energy, S<sub>n</sub> (keV)", parent_data.SnStr)
	add_if_exists(info, "P. sep. energy, S<sub>p</sub> (keV)", parent_data.SpStr)
	prod_str = ""
	try:
		nice_prod_str(Production.objects.get(iZA = iZA).GenShort)
	except ObjectDoesNotExist:
		pass
	add_if_exists(info, "Prod. mode", prod_str)
	add_if_exists(info, "Natural abundance (%)", parent_data.AbundStr)
	
	citation_info = []
	try:
		evalCit = EvaluationCitation.objects.filter(A = parent_data.A, Symb = parent_data.Symb)
		if (len(evalCit) == 1):
			if (evalCit[0].Update == 0):
				add_if_exists(citation_info, "ENSDF citation", evalCit[0].Citation)
				add_if_exists(citation_info, "Literature cut-off date", evalCit[0].PubDate)
				add_if_exists(citation_info, "Author(s)", evalCit[0].Authors)
			else:
				add_if_exists(citation_info, "Literature cut-off date", " ")
				add_if_exists(citation_info, "Author(s)", " ")
				add_if_exists(citation_info, "Update", str(evalCit[0].PubDate) + ", " + str(evalCit[0].Authors))
		else:
			for ev in evalCit:
				if (ev.Update == 0):
					add_if_exists(citation_info, "ENSDF citation", ev.Citation)
					add_if_exists(citation_info, "Literature cut-off date", ev.PubDate)
					add_if_exists(citation_info, "Author(s)", ev.Authors)
				else:
					add_if_exists(citation_info, "Update", str(ev.PubDate) + ", " + str(ev.Authors))
	except ObjectDoesNotExist:
		pass
	
	decay_prop = []
	has_dec_ref = False
	dec_paths = Parents2.objects.filter(iZA = iZA).order_by("-Perc")
	if (len(dec_paths) > 0):
		for dec in dec_paths:
			refs = References.objects.filter(iZA = iZA, Mode = dec.nMode)
			dec_ref_str = ""
			for r in refs:
				dec_ref_str = dec_ref_str + r.KeyNo + " "
				has_dec_ref = True
			decay_prop.append({"mode":to_nice_mode(dec.Mode), "branch":dec.PercStr, "q":dec.QStr, "ref":dec_ref_str})
	
	related_nuclides = []
	for dec in dec_paths:
		tmp_par = None
		if (dec.Mode == "A"):
			tmp_par = Parents.objects.filter(A = parent_data.A - 4, Z = parent_data.Z - 2)
		elif (dec.Mode == "B-"):
			tmp_par = Parents.objects.filter(A = parent_data.A, Z = parent_data.Z + 1)
		elif (dec.Mode == "B+" or dec.Mode == "EC" or dec.Mode == "EC+B+"):
			tmp_par = Parents.objects.filter(A = parent_data.A, Z = parent_data.Z - 1)
		elif (dec.Mode == "IT"):
			tmp_par = Parents.objects.filter(A = parent_data.A, Z = parent_data.Z, El = 0.0)
		if (tmp_par != None):
			for t_p in tmp_par:
				related_nuclides.append({"name":iZA_to_string(t_p.iZA), "iZA":t_p.iZA, "relation":"Daughter", "halflife":t_p.TStr, "mode":assemble_mode_str(t_p.iZA)})
	for alt in Parents.objects.filter(A = parent_data.A + 4, Z = parent_data.Z + 2):
		if (len(Parents2.objects.filter(iZA = alt.iZA, Mode = "A")) > 0):
			related_nuclides.append({"name":iZA_to_string(alt.iZA), "iZA":alt.iZA, "relation":"Mother", "halflife":alt.TStr, "mode":assemble_mode_str(alt.iZA)})
	for alt in Parents.objects.filter(A = parent_data.A, Z = parent_data.Z + 1):
		if (len(Parents2.objects.filter(iZA = alt.iZA, Mode__in = ["B+", "EC", "EC+B+"])) > 0):
			related_nuclides.append({"name":iZA_to_string(alt.iZA), "iZA":alt.iZA, "relation":"Mother", "halflife":alt.TStr, "mode":assemble_mode_str(alt.iZA)})
	for alt in Parents.objects.filter(A = parent_data.A, Z = parent_data.Z - 1):
		if (len(Parents2.objects.filter(iZA = alt.iZA, Mode = "B-")) > 0):
			related_nuclides.append({"name":iZA_to_string(alt.iZA), "iZA":alt.iZA, "relation":"Mother", "halflife":alt.TStr, "mode":assemble_mode_str(alt.iZA)})
	if (parent_data.El == 0.0):
		for alt in Parents.objects.filter(A = parent_data.A, Z = parent_data.Z, Symb = parent_data.Symb).exclude(El = 0.0):
			if (len(Parents2.objects.filter(iZA = alt.iZA, Mode = "IT")) > 0):
				related_nuclides.append({"name":iZA_to_string(alt.iZA), "iZA":alt.iZA, "relation":"Mother", "halflife":alt.TStr, "mode":assemble_mode_str(alt.iZA)})	
	
	extra_information = []
	extra_information.append({"desc":"Summary drawing for A = " + str(parent_data.A), "url":"http://nucleardata.nuclear.lu.se/toi/pdf/" + str(parent_data.A) + ".pdf"})
	extra_information.append({"desc":"X-ray and Auger electron data on " + iZA_to_element(parent_data.iZA), "url":"/aug_xray/" + str(parent_data.Z) + "/"})
	extra_information.append({"desc":"Search ENSDF database", "url":"http://www.nndc.bnl.gov/ensdf/"})
	
	gamma_table = []
	alpha_table = []
	beta_table = []
	xray_table = []
	
	gamma_footnote = False
	if (len(gammas) > 0):
		temp_arr = array(gammas.values_list("Eg", "Ig"))
		gamma_order = temp_arr[:,0].argsort().argsort()
		gamma_yeild_order = temp_arr[:,1].argsort().argsort()
		for i in range(len(gammas)):
			has_footnote = False
			if (gammas[i].Foot != ""):
				has_footnote = True
				gamma_footnote = True
			gamma_table.append({"energy":gammas[i].EgStr, "yeild":gammas[i].IgStr, "mode":to_nice_mode(gammas[i].Mode), "energy_order":gamma_order[i], "yeild_order":gamma_yeild_order[i], "has_footnote":has_footnote})
	
	if (len(betas) > 0):
		temp_arr = array(betas.values_list("Eb", "Ib"))
		beta_order = temp_arr[:,0].argsort().argsort()
		beta_yeild_order = temp_arr[:,1].argsort().argsort()
		for i in range(len(betas)):
			beta_table.append({"energy":betas[i].Eb, "yeild":betas[i].IbStr, "mode":to_nice_mode(betas[i].Mode), "energy_order":beta_order[i], "yeild_order":beta_yeild_order[i]})
	
	if (len(alphas)):
		temp_arr = array(alphas.values_list("Ea", "Ia"))
		alpha_order = temp_arr[:,0].argsort().argsort()
		alpha_yeild_order = temp_arr[:,1].argsort().argsort()
		for i in range(len(alphas)):
			alpha_table.append({"energy":alphas[i].EaStr, "yeild":alphas[i].IaStr, "energy_order":alpha_order[i], "yeild_order":alpha_yeild_order[i]})
	
	xrays = XIntensities.objects.filter(iZA = iZA)
	if (len(xrays) > 0):
		x_yeild_order = array(xrays.values_list("Int"))[:,0].argsort().argsort()
		for i in range(len(xrays)):
			real_xray = XRays.objects.get(XCode = xrays[i].XCode)
			xray_table.append({"energy":real_xray.Energy, "yeild":xrays[i].IntStr, "yeild_order":x_yeild_order[i], "assignment":real_xray.Element + " " + real_xray.Assignment.replace("\"\"", "\"")})
	
	t = loader.get_template("show_nuclide.html")
	c = RequestContext(request, {"halflife":parent_data.TStr,"nuclide":nuclide_str,"nuclide_pretty":nuclide_str_pretty, "gamma_data":gamma_table, "alpha_data":alpha_table, "beta_data":beta_table, "xray_data":xray_table, "iZA":iZA, "A":parent_data.A, "Z":parent_data.Z, "symb":parent_data.Symb, "N":parent_data.A - parent_data.Z, "meta":iZA_to_meta(parent_data.iZA), "gamma_footnote":gamma_footnote, "general_info":info, "citation_info":citation_info, "decay_properties":decay_prop, "has_dec_ref":has_dec_ref, "related_nuclides":related_nuclides, "extra_information":extra_information})
	return HttpResponse(t.render(c))
	