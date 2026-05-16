import os

from sectionproperties.analysis import Section
from sectionproperties.pre import Geometry


def elenca_files_cartella(path_cartella):
    elenco_files = []
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
    return listGeom


if __name__ == "__main__":
    # Esempio di utilizzo — aggiornare il path prima di eseguire
    example_path = r"example\Sezioni Pilone\5C2.dxf"
    geom = Geometry.from_dxf(dxf_filepath=example_path)
    geom.create_mesh(mesh_sizes=[100])
    Section(geometry=geom).plot_mesh(materials=False)
