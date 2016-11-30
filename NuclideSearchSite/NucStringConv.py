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

names = ["NN","H", "He","Li","Be","B", "C","N", "O", "F", "Ne","Na","Mg","Al","Si","P", "S", "Cl","Ar","K", "Ca","Sc","Ti","V", "Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y", "Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I", "Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W", "Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U", "Np","Pu","Am","Cm","Bk","Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt","Ds","Rg", "Cn", "Uut", "Fl", "Uup", "Lv", "Uus", "Uuo"]
elements = {"NN":"Neutron","H":"Hydrogen", "He":"Helium","Li":"Lithium","Be":"Beryllium","B":"Boron", "C":"Carbon","N":"Nitrogen", "O":"Oxygen", "F":"Fluorine", "Ne":"Neon","Na":"Sodium","Mg":"Magnesium","Al":"Aluminium","Si":"Silicon","P":"Phosphorus", "S":"Sulfur", "Cl":"Chlorine","Ar":"Argon","K":"Potassium", "Ca":"Calcium","Sc":"Scandium","Ti":"Titanium","V":"Vanadium", "Cr":"Chromium","Mn":"Manganese","Fe":"Iron","Co":"Cobalt","Ni":"Nickel","Cu":"Copper","Zn":"Zinc","Ga":"Gallium","Ge":"Germanium","As":"Arsenic","Se":"Selenium","Br":"Bromine","Kr":"Krypton","Rb":"Rubidium","Sr":"Strontium","Y":"Yttrium", "Zr":"Zirconium","Nb":"Niobium","Mo":"Molybdenum","Tc":"Technetium","Ru":"Ruthenium","Rh":"Rhodium","Pd":"Palladium","Ag":"Silver","Cd":"Cadmium","In":"Indium","Sn":"Tin","Sb":"Antimony","Te":"Tellurium","I":"Iodine", "Xe":"Xenon","Cs":"Caesium","Ba":"Barium","La":"Lanthanum","Ce":"Cerium","Pr":"Praseodymium","Nd":"Neodynium","Pm":"Promethium","Sm":"Samarium","Eu":"Europium","Gd":"Gadolinium","Tb":"Terbium","Dy":"Dysprosium","Ho":"Holmium","Er":"Erbium","Tm":"Thulium","Yb":"Ytterbium","Lu":"Lutetium","Hf":"Hafnium","Ta":"Tantalum","W":"Tungsten", "Re":"Rhenium","Os":"Osmium","Ir":"Iridium","Pt":"Platinum","Au":"Gold","Hg":"Mercury","Tl":"Thallium","Pb":"Lead","Bi":"Bismuth","Po":"Polonium","At":"Astatine","Rn":"Radon","Fr":"Francium","Ra":"Radium","Ac":"Actinum","Th":"Thorium","Pa":"Protactinium","U":"Uranium", "Np":"Neptunium","Pu":"Plutonium","Am":"Americium","Cm":"Curium","Bk":"Berkelium","Cf":"Californium","Es":"Einsteinium","Fm":"Fermium","Md":"Mendelevium","No":"Nobelium","Lr":"Lawrencium","Rf":"Rutherfordium","Db":"Dubnium","Sg":"Seaborgium","Bh":"Bohrium","Hs":"Hassium","Mt":"Meitnerium","Ds":"Darmstadtium","Rg":"Roentgenium", "Cn":"Copernicium", "Uut":"Ununtrium", "Fl":"Flerovium", "Uup":"Ununpentium", "Lv":"Livermorium", "Uus":"Ununseptium", "Uuo":"Ununoctium"}

def iZA_to_meta(iZA):
	A = iZA // 10000
	m = (iZA - A * 10000) // 300
	if (m == 0):
		return ""
	elif (m == 1):
		return "m"
	return "m" + str(m)

def iZA_to_element(iZA):
	Z = iZA // 10000
	symbol = names[Z]
	return elements[symbol]

def iZA_to_Z(iZA):
	return iZA // 10000

def iZA_to_string(iZA):
	A = iZA // 10000
	Z = (iZA - A * 10000) % 300
	m = (iZA - A * 10000) // 300
	if (m == 1):
		return names[A] + "-" + str(Z) + "m"
	elif (m > 1):
		return names[A] + "-" + str(Z) + "m" + str(m)
	return names[A] + "-" + str(Z)

def iZA_to_html(iZA):
	A = iZA // 10000
	Z = (iZA - A * 10000) % 300
	m = (iZA - A * 10000) // 300
	if (m == 1):
		return "<sup>" + str(Z) + "m</sup>" + names[A]
	elif (m > 1):
		return "<sup>" + str(Z) + "m" + str(m) + "</sup>" + names[A]
	return "<sup>" + str(Z) + "</sup>" + names[A]

def is_meta_stable(iZA):
	A = iZA // 10000
	m = (iZA - A * 10000) // 300
	if (m > 0):
		return True
	return False

def to_nice_mode(mode_str):
	mode_dict = {"A":"&#945;", "B+":"&#946;<sup>+</sup>", "B-":"&#946;<sup>-</sup>", "EC":"E.C.", "IT":"I.T.", "EC+B+":"E.C. + &#946;<sup>+</sup>", "SF":"S.F."}
	if (mode_str in mode_dict):
		return mode_dict[mode_str]
	return mode_str

def assemble_mode_str(iZA):
	from Data.models import Parents2
	p2_parents = Parents2.objects.filter(iZA = iZA)
	ret_str = ""
	first = True
	for p in p2_parents:
		dec_str = p.Mode
		if (not first):
			ret_str = ret_str + ", "
		first = False
		ret_str = ret_str + to_nice_mode(dec_str)
	return ret_str


if __name__ == '__main__':
	print(iZA_to_string(920238))