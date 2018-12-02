from django.conf.urls import url

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

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

import Index.views, ShowNuclide.views, Search.views, About.views, AdvSearch.views, XRayAug.views

from django.contrib import admin
from django.urls import path
#
urlpatterns = [
    # Examples:
    url(r'^$', Index.views.index, name = "index"),
    url(r'^show_nuclide/([0-9]+)/$', ShowNuclide.views.show_nuclide),
    url(r'^auto_complete/input=(?P<search_term>.+)', Search.views.auto_complete_query),
    url(r'^search/$', Search.views.search),
    url(r'^about/$', About.views.about),
    url(r'^adv_search/$', AdvSearch.views.search),
    url(r'^adv_search_res/$', AdvSearch.views.search_res),
    url(r'^aug_xray/([0-9]{1,3})/$', XRayAug.views.view_data),
    path('admin/', admin.site.urls)
]
