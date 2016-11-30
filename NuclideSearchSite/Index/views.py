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
from NucStringConv import iZA_to_string, iZA_to_html
from Data.models import *

def index(request):
	t = loader.get_template("index.html")
	c = RequestContext(request, {"template":"<a href=\"{{{url}}}\" class=\"search-value\">{{{value}}}</a> <p class=\"search-extra\">{{{extra}}}</p> <p class=\"search-description\">{{{desc}}}</p>"})
	return HttpResponse(t.render(c))
	
