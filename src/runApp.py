import streamlit as st
from codes import *
from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry, Geometry, Material
from tempfile import NamedTemporaryFile
import os
import matplotlib


# Folder picker button
st.title('Make List of Files inside folder')

st.write('Please insert path folder:')
dirname = st.text_input('Path Folder', '\\')


if dirname is not "\\":
    dirname = os.path.normpath(dirname)
    file = elenca_files_cartella(dirname, typeFile=".dxf")
    st.write(file)

    geometryList = importSection(file)

## Assign material
geometryList = assMat(geometryList , name = "Steel", E = 210e3, v=0.3, rho=7.85e-6, fy=250)

## Calculate property
geometryList = calcPro(geometryList)




