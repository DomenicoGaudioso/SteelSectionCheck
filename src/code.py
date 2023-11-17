from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry, Geometry

def elenca_files_cartella(path_cartella):
    elenco_files = []
    
    # Scandisci ricorsivamente la cartella e le sue sottocartelle
    for cartella_corrente, sottocartelle, files in os.walk(path_cartella):
        for file in files:
            percorso_file = os.path.join(cartella_corrente, file)
            elenco_files.append(percorso_file)

    return elenco_files

def importSection(dxfFile):
    
    listGeom = []
    for idxf in dxfFile:
        geom = Geometry.from_dxf(idxf)
        geom.create_mesh(mesh_sizes=[1])
        listGeom.append(geom)
        
        Section(geometry=geom).plot_mesh(materials=False)
    return 

path = [r"C:\Users\Domen\OneDrive\00_TOLS\GitHub\SteelSectionCheck\example\Sezioni Pilone\3C1.dxf"]
#importSection( path)
geom = Geometry.from_dxf(dxf_filepath = r"C:\Users\Domen\OneDrive\00_TOLS\GitHub\SteelSectionCheck\example\Sezioni Pilone\5C2.dxf")
geom.create_mesh(mesh_sizes=[100])
Section(geometry=geom).plot_mesh(materials=False)