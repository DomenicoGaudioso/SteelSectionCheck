from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry, Geometry, Material
import os
import matplotlib.pyplot as plt
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

def elenca_files_cartella(path_cartella,  typeFile = None):
    elenco_files = []
    
    # Scandisci ricorsivamente la cartella e le sue sottocartelle
    for cartella_corrente, sottocartelle, files in os.walk(path_cartella):
        for file in files:
            percorso_file = os.path.join(cartella_corrente, file)
            if typeFile is not None:
                if os.path.splitext(file)[1] == typeFile:
                    elenco_files.append(percorso_file)
            else:
                elenco_files.append(percorso_file)

    return elenco_files

def importSection(dxfFile, rotate = 0):
    
    dictGeom = {}
    for idxf in dxfFile:
        path = Path(idxf)
        geom = Geometry.from_dxf(path)
        geom = Geometry.rotate_section(geom, rotate, "center")
        geom.create_mesh(mesh_sizes=[1000])

        dictGeom[path.name.replace(".dxf", '')] = geom
        
        
    return dictGeom

def assMat(dictGeom, name = "Steel", E = 210e3, v=0.3, rho=7.85e-6, fy=250):
    
    material = Material(
    name=name,
    elastic_modulus=E,
    poissons_ratio=v,
    density=rho,
    yield_strength=fy,
    color="grey",
    )
    
    for ilist in dictGeom:
        dictGeom[ilist].material = material
    
    return dictGeom

def calcPro(dictGeom):
    dictionaryProp = {} #ASSEGNARE UNA DICTIONARY 
    
    for ilist in dictGeom:
        section = Section(geometry=dictGeom[ilist])
        section.calculate_geometric_properties()
        section.calculate_warping_properties()
        dictGeom[ilist] = section
        #section.calculate_plastic_properties()
        
        area = section.get_area()
        igx, igy = section.get_c()
        ixx_c, iyy_c, ixy_c = section.get_ic()
        wxx_pos, wxx_neg, wyy_pos, wyy_neg = section.get_z()
        phi = section.get_phi()
        j = section.get_j()
        scx_c, scy_c = section.get_sc_p()
        ax_c, ay_c = section.get_as() #area di taglio
        
        dictionaryProp[ilist] = {"A": area,
                                 "xg": igx,
                                 "yg": igy,
                                 "xsc": scx_c,
                                 "ysc": scy_c,
                                 "Ixx": ixx_c,
                                 "Iyy": iyy_c,
                                 "Ixy": ixy_c,
                                 "Wx+": wxx_pos,
                                 "Wx-": wxx_neg,
                                 "Wy+": wyy_pos,
                                 "Wy-": wyy_neg,                                    
                                 "c_torsion": j,
                                 "Avx":  ax_c,
                                 "Avy": ay_c,
                                 
                                }
        
    
    return dictGeom, dictionaryProp

def calcTension(dictGeom, dataFile, unit = "KNm"):
    if unit == "KNm":
        c = 1000
        
    dictTension = {}
        
    for iName in dictGeom:
        cds = dataFile.loc[dataFile['Nome']==iName]
        dictTension[iName] = {}
        for i in cds.values:
            stress = dictGeom[iName].calculate_stress( n=i[2]*c, vx=i[3]*c, vy=i[4]*c, mzz=i[5]*c**2, mxx=i[6]*c**2, myy=i[7]*c**2 )
            dictTension[iName][i[1]] = stress
    
    return dictTension

def tensionVM_Max(dictTension):
    tension = {}
    for iN in dictTension:
        tension[iN] = {}
        for j in dictTension[iN]: #posso avere più combinazioni per sezione
            tensionAll= dictTension[iN][j].get_stress()[0]
            tension[iN][j] = max(abs(max(tensionAll["sig_vm"])), abs(min(tensionAll["sig_vm"])))
    
    return tension

def _color_red_or_green(val):
    color = 'red' if val > 1 else 'green'
    #txt = f'color:clack;background-color:{color};'
    txt = 'color: %s' % color
    return txt

def checkTension(tension, tLimit):
    #fyd
    df_DC =(pd.DataFrame(tension)/tLimit).round(2)
    df_DC.style.applymap(_color_red_or_green)
         
    return df_DC

"""
stress = sec.calculate_stress(
    n=50e3, mxx=-5e6, m22=2.5e6, mzz=0.5e6, vx=10e3, vy=5e3
)

# plot stress contour
stress.plot_stress(stress="vm", cmap="viridis", normalize=False)

StressPost.get_stress()
"""

# path = r"C:\Users\Domen\OneDrive\00_TOLS\GitHub\SteelSectionCheck\example\Sezioni Pilone"
# file = elenca_files_cartella(path, typeFile=".dxf")
# listSection = importSection(file, rotate=90)
# #listSection["3C1"].plot_geometry()
# geometryList, dictProp = calcPro(listSection)
# dataFile = pd.read_excel(r'C:\Users\Domen\OneDrive\00_TOLS\GitHub\SteelSectionCheck\example\CDS_Pilone\CDS_pilone.xlsx')
# tension = calcTension(geometryList, dataFile)
# #tension["3C1"][1].plot_stress(stress="vm", cmap="YlOrRd", normalize=False, fmt="{x:.2f}")
# #tension["3C1"][1].plot_stress(stress="myy_zz", cmap="YlOrRd", normalize=False, fmt="{x:.2f}")
# #tension["3C1"][1].plot_stress(stress="mxx_zz", cmap="YlOrRd", normalize=False, fmt="{x:.2f}")

# #calcolo il massimo in valore assoluto
# tMax = tensionVM_Max(tension)
# checkTension(tMax, 355)