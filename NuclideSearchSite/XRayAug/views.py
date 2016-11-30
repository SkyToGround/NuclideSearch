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
from NucStringConv import elements, names
from Data.models import XRays, Augers
from numpy import array, where, equal
from django.core.exceptions import ObjectDoesNotExist


def view_data(request, Z):
	name = "Z = " + str(Z)
	element = "Z = " + str(Z)
	try:
		name = names[int(Z)]
		element = elements[name]
	except:
		pass
	ret_dict = {"nothing_found":True, "name":name, "element":element}
	xrays = []
	c_rays = XRays.objects.filter(Z = int(Z))
	augs = Augers.objects.filter(Z = int(Z))
	
	if (len(c_rays) > 0):
		tmp_arr = array(c_rays.values_list("Kint", "L1Int", "L2Int", "L3Int"))
		none_ind = where(equal(tmp_arr, None) == True)
		tmp_arr[none_ind] = 0
		k_order = tmp_arr[:,0].argsort().argsort()
		l1_order = tmp_arr[:,1].argsort().argsort()
		l2_order = tmp_arr[:,2].argsort().argsort()
		l3_order = tmp_arr[:,3].argsort().argsort()
	
		for i in range(len(c_rays)):
			xrays.append({"assignment_order":i, "energy":c_rays[i].Energy, "assignment":c_rays[i].Element + " " + c_rays[i].Assignment, "k":c_rays[i].KintStr, "k_order":k_order[i], "l1":c_rays[i].L1IntStr, "l1_order":l1_order[i], "l2":c_rays[i].L2IntStr, "l2_order":l2_order[i], "l3":c_rays[i].L3IntStr, "l3_order":l3_order[i]})
	
	augers = []
	if (len(augs) > 0):
		tmp_arr = array(augs.values_list("Kint", "L1Int", "L2Int", "L3Int"))
		none_ind = where(equal(tmp_arr, None) == True)
		tmp_arr[none_ind] = 0
		k_order = tmp_arr[:,0].argsort().argsort()
		l1_order = tmp_arr[:,1].argsort().argsort()
		l2_order = tmp_arr[:,2].argsort().argsort()
		l3_order = tmp_arr[:,3].argsort().argsort()
	
		for i in range(len(augs)):
			augers.append({"assignment_order":i, "energy":augs[i].Energy, "assignment":augs[i].Element + " " + augs[i].Assignment, "k":augs[i].KintStr, "k_order":k_order[i], "l1":augs[i].L1IntStr, "l1_order":l1_order[i], "l2":augs[i].L2IntStr, "l2_order":l2_order[i], "l3":augs[i].L3IntStr, "l3_order":l3_order[i]})
	
	if (len(augers) > 0 or len(xrays) > 0):
		ret_dict["nothing_found"] = False
	
	ret_dict["xrays"] = xrays
	ret_dict["augers"] = augers
	t = loader.get_template("xray_aug.html")
	c = RequestContext(request, ret_dict)
	return HttpResponse(t.render(c))
	
	
	

