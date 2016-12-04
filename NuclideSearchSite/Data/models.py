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

from Data.models import *
from NucStringConv import iZA_to_string
from django.db import models

class Alphas(models.Model):
    iZA = models.BigIntegerField(null = False)
    Foot = models.CharField(max_length = 2)
    Ea = models.FloatField()
    EaStr = models.CharField(max_length = 100)
    Ia = models.FloatField()
    IaStr = models.CharField(max_length = 100)
    #IaRel = models.FloatField()

    def __unicode__(self):
        return unicode(iZA_to_string(self.iZA)) + u" " + unicode(self.Ea) + u" keV (" + unicode(self.Ia) + u" %)"

# class Augers(models.Model):
# 	ACode = models.BigIntegerField()
# 
class Betas(models.Model):
    iZA = models.BigIntegerField(null = False)
    Mode = models.CharField(max_length = 16)
    Eb = models.FloatField()
    Ib = models.FloatField()
    #IbRel = models.FloatField()
    IbStr = models.CharField(max_length = 100)

    def __unicode__(self):
        return unicode(iZA_to_string(self.iZA)) + u" " + unicode(self.Eb) + u" keV (" + unicode(self.Ib) + u" %)"
# 
# class EvaluationCitation(models.Model):
# 	A = models.BigIntegerField(null = False)
# 
class Gammas(models.Model):
    iZA = models.BigIntegerField()
    Foot = models.CharField(max_length = 2)
    Eg = models.FloatField(db_index = True)
    EgStr = models.CharField(max_length = 100)
    Ig = models.FloatField(null = True, db_index = True)
    IgRel = models.FloatField(null = True, db_index = True)
    IgStr = models.CharField(max_length = 54)
    Mode = models.CharField(max_length = 16)

    def __unicode__(self):
        return unicode(iZA_to_string(self.iZA)) + u" " + unicode(self.Eg) + u" keV (" + unicode(self.Ig) + u" %)"

class XRays(models.Model):
    XCode = models.BigIntegerField()
    Z = models.IntegerField()
    Energy = models.FloatField(null = False)
    Element = models.CharField(max_length = 4)
    Assignment = models.CharField(max_length = 100)
    Kint = models.FloatField(null = True)
    KintStr = models.CharField(max_length = 100, null = True)
    L1Int = models.FloatField(null = True)
    L1IntStr = models.CharField(max_length = 100, null = True)
    L2Int = models.FloatField(null = True)
    L2IntStr = models.CharField(max_length = 100, null = True)
    L3Int = models.FloatField(null = True)
    L3IntStr = models.CharField(max_length = 100, null = True)


class XIntensities(models.Model):
    iZA = models.BigIntegerField(null = False)
    XCode = models.BigIntegerField(null = False)
    Int = models.FloatField()
    IntStr = models.CharField(max_length = 100)

########################################################################
class History(models.Model):
    FULL = 'FUL'
    UPDATE = 'UPD'
    FORMAT = "FMT"
    ERROR = "ERR"
    MODIFIED = "MOD"
    EXPERIMENTAL = "EXP"
    TYPE_CHOICES = ((FULL, 'Full'), (UPDATE, 'Update'), (FORMAT, "Format"), (ERROR, "Errata"), (MODIFIED, "Modified"), (EXPERIMENTAL, "Experimental"))
    HistoryType = models.CharField(max_length=3, choices=TYPE_CHOICES,)
    Author = models.CharField(max_length = 100)
    Citation = models.CharField(max_length = 100)
    Date = models.DateField(null = True)
    CutOff = models.DateField(null = True)
    Comments = models.CharField(max_length = 100, default = "")

########################################################################
class Q_Record(models.Model):
    Qb = models.FloatField(null = True)
    QbSA = models.FloatField(null = True)
    Sn = models.FloatField(null = True)
    SnSA = models.FloatField(null = True)
    Sp = models.FloatField(null = True)
    SpSA = models.FloatField(null = True)
    Qa = models.FloatField(null = True)
    QaSA = models.FloatField(null = True)    
    Reference = models.CharField(max_length = 10, default = "")
    Comments = models.CharField(max_length = 100, default = "")

class Nuclide(models.Model):
    Com = models.TextField()
    A = models.IntegerField(null = False)
    Z = models.IntegerField(null = False)
    Symb = models.CharField(max_length = 4, null = False)
    iZA = models.BigIntegerField(null = False, primary_key = True, unique = True)
    History = models.ManyToManyField(History)
    QRec = models.ManyToManyField(Q_Record)
    def __unicode__(self):
        return unicode(self.Symb) + u"-" + unicode(self.A)

class Parents(models.Model):
    Comments = models.CharField(max_length = 400, default = "")
    A = models.IntegerField(null = False)
    Z = models.IntegerField(null = False)
    iZA = models.BigIntegerField(null = False, primary_key = True, unique = True)
    def __unicode__(self):
        return unicode(self.Symb) + u"-" + unicode(self.A)

class Parents2(models.Model):
    iZA = models.BigIntegerField(null = False)
    nMode = models.IntegerField()
    DSID = models.CharField(max_length = 60, null = True)
    Spec = models.CharField(max_length = 4)
    Mode = models.CharField(max_length = 16)
    Perc = models.FloatField(null = True)
    PercStr = models.CharField(max_length = 100)
    QStr = models.CharField(max_length = 100)

class Status(models.Model):
    DatabaseID = models.CharField(max_length = 510)
    BuildDate = models.DateField()
    Remarks = models.CharField(max_length = 510)

    def __unicode__(self):
        return unicode(self.DatabaseID)

class References(models.Model):
    RefKey = models.CharField(null = False, max_length = 10, primary_key = True, unique = True)
    Title = models.CharField(max_length = 100)
    Authors = models.CharField(max_length = 200)
    Publication = models.CharField(max_length = 100)
    BOOK = 'BK'
    JOURNAL = 'JR'
    PUB_TYPE_CHOICES = ((BOOK, 'Book'), (JOURNAL, 'Journal'),)
    PublicationType = models.CharField(max_length=2, choices=PUB_TYPE_CHOICES, default=JOURNAL,)

class Production(models.Model):
    iZA = models.BigIntegerField(null = False)
    GenShort = models.CharField(max_length = 12)

class EvaluationCitation(models.Model):
    A = models.BigIntegerField(null = False)
    Symb = models.CharField(max_length = 4, null = False)
    Update = models.IntegerField(null = False)
    Citation  = models.CharField(max_length = 100)
    PubDate = models.CharField(max_length = 100)
    Authors = models.CharField(max_length = 200)

class Augers(models.Model):
    ACode = models.BigIntegerField()
    Z = models.IntegerField()
    Energy = models.FloatField(null = False)
    Element = models.CharField(max_length = 4)
    Assignment = models.CharField(max_length = 100)
    Kint = models.FloatField(null = True)
    KintStr = models.CharField(max_length = 100, null = True)
    L1Int = models.FloatField(null = True)
    L1IntStr = models.CharField(max_length = 100, null = True)
    L2Int = models.FloatField(null = True)
    L2IntStr = models.CharField(max_length = 100, null = True)
    L3Int = models.FloatField(null = True)
    L3IntStr = models.CharField(max_length = 100, null = True)
# 
# class Parents(models.Model):
# 	iZA = models.BigIntegerField(null = False)
# 	
# class Parents2(models.Model):
# 	iZA = models.BigIntegerField(null = False)
# 	
# class Production(models.Model):
# 	iZA = models.BigIntegerField(null = False)
# 	
# class References(models.Model):
# 	iZA = models.BigIntegerField(null = False)
# 
# class Status(models.Model):
# 	DatabaseID = models.CharField(max_length = 510)
# 
# class Terms(models.Model):
# 	ID = models.BigIntegerField()
# 
# class XIntensities(models.Model):
# 	iZA = models.BigIntegerField(null = False)
# 	
# class XRays(models.Model):
# 	XCode = models.BigIntegerField()