from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry, Geometry, Material
import os
import matplotlib.pyplot as plt

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

def importSection(dxfFile):
    
    listGeom = []
    for idxf in dxfFile:
        geom = Geometry.from_dxf(idxf)
        geom.create_mesh(mesh_sizes=[100])
        listGeom.append(geom)
        
        #Section(geometry=geom).plot_mesh(materials=False)
    return listGeom

def assMat(listGeom, name = "Steel", E = 210e3, v=0.3, rho=7.85e-6, fy=250):
    
    material = Material(
    name=name,
    elastic_modulus=E,
    poissons_ratio=v,
    density=rho,
    yield_strength=fy,
    color="grey",
    )
    
    for ilist in listGeom:
        ilist.material = material
    
    return listGeom

def calcPro(listGeom):
    dictionaryProp = {} #ASSEGNARE UNA DICTIONARY 
    
    for ilist in listGeom:
        section = Section(geometry=ilist)
        section.calculate_geometric_properties()
        section.calculate_warping_properties()
        #section.calculate_plastic_properties()
        
        area = section.get_area()
        ixx_c, iyy_c, ixy_c = section.get_ic()
        phi = section.get_phi()
        j = section.get_j()
        
        print(f"Area = {area:.1f} mm2")
        print(f"Ixx = {ixx_c:.3e} mm4")
        print(f"Iyy = {iyy_c:.3e} mm4")
        print(f"Ixy = {ixy_c:.3e} mm4")
        print(f"Principal axis angle = {phi:.1f} deg")
        print(f"Torsion constant = {j:.3e} mm4")
    
    return listGeom, dictionaryProp

"""
stress = sec.calculate_stress(
    n=50e3, mxx=-5e6, m22=2.5e6, mzz=0.5e6, vx=10e3, vy=5e3
)

# plot stress contour
stress.plot_stress(stress="vm", cmap="viridis", normalize=False)

StressPost.get_stress()
"""

#path = r"C:\Users\Domen\OneDrive\00_TOLS\GitHub\SteelSectionCheck\example\Sezioni Pilone"
#file = elenca_files_cartella(path, typeFile=".dxf")
#listSection = importSection(file)

#for i in listSection:
    #Section(geometry=i).plot_mesh()
    #section = Section(geometry=geom)
    #section.calculate_geometric_properties()
    #section.calculate_warping_properties()
    #section.calculate_plastic_properties()

    #section.plot_centroids()