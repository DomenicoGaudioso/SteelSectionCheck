import streamlit as st
from codes import *
from sectionproperties.analysis import Section
from sectionproperties.pre import CompoundGeometry, Geometry, Material
from tempfile import NamedTemporaryFile
import os
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(layout="wide")

with st.sidebar:
   st.title('section check')

   # Utilizza st.markdown per inserire i link
   st.markdown("## Contacts")
   st.write("Name: Domenico")
   st.write("Surname: Gaudioso")
   st.write("📧 dome.gaudioso@gmail.com")
   st.markdown("📱 [LinkedIn]({'https://www.linkedin.com/in/domenico-gaudioso-529a28171/'})", unsafe_allow_html=True)
   st.markdown("💻 [GitHub]({'https://github.com/DomenicoGaudioso'})", unsafe_allow_html=True)

   st.markdown("## About")
   # Link di Streamlit
   st.markdown(f"[Streamlit]({'https://www.streamlit.io/'})", unsafe_allow_html=True)
   # Link di SciPy
   st.markdown(f"[Sectionproperty]({'https://sectionproperties.readthedocs.io/en/latest/index.html'})", unsafe_allow_html=True)



st.write('Please insert path folder conteinr dxf file section:')
dirname = st.text_input('Path Folder', '\\')


if dirname is not "\\":
    dirname = os.path.normpath(dirname)
    file = elenca_files_cartella(dirname, typeFile=".dxf")
    st.write(file)
    angle = st.number_input('angle rotated', value=90)
    st.write('The current number is ', round(angle, 2))
    geometryList = importSection(file, rotate=angle)

## Calculate property
geometryList, dictProp = calcPro(geometryList)

## PLOT SECTION
st.markdown("## Cross Section Geometry")
plotList = []
for i in geometryList:
    fig, axs = plt.subplots(1, 2, figsize=(9, 3), sharey=True)
    # plot the mesh
    geometryList[i].plot_mesh(ax=axs[0])
    geometryList[i].plot_centroids(ax=axs[1])
    plotList.append(fig)
    
sectionPlot = st.slider("Which section do you want to see?",0, len(geometryList), 0)
st.write(f'Section: {list(geometryList.keys())[sectionPlot]}')
st.pyplot(plotList[sectionPlot])

## PROPERTY SECTION
st.markdown("## Property Setion")
df = pd.DataFrame(dictProp)
st.dataframe(df)

st.write('Insert the cds excel file')
uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write(df)

tension = calcTension(geometryList, df)

#calcolo il massimo in valore assoluto
tensionMax = tensionVM_Max(tension)
st.markdown('## Tensione Max')
df_tensMax =pd.DataFrame(tensionMax)
st.dataframe(df_tensMax)

#.map_index(lambda v: "color:pink;" if v>1 else "color:darkblue;", axis=0)
st.markdown('## Rapporto Domanda/Capacità')
sigmaLimit = st.number_input('tension limit', value=255/1.15)
st.write('The current number is ', round(sigmaLimit, 2))
check = checkTension(tensionMax, sigmaLimit)
st.latex(r'\sqrt{(\sigma_{x,\text{Ed}})^2 + (\sigma_{z,\text{Ed}})^2 + \sigma_{z,\text{Ed}} \cdot \sigma_{x,\text{Ed}} + 3 \tau_{\text{Ed}}^2} \leq \sigma_{\text{yield}}')
st.dataframe(check.style.applymap(lambda x: "background-color: red" if x>1 else "background-color: green"))

## PLOT TENSION
st.markdown("## Plot Tension")

# plot the mesh
cols1, cols2, cols3 = st.columns([1,1,1])

nameSec = list(geometryList.keys())
resultOpt = list(geometryList.keys())
resultOpt    = ["vm", "n_zz", "mxx_zz","myy_zz",
"m11_zz" ,"m22_zz","m_zz","mzz_zx","mzz_zy","mzz_zxy",
"vx_zx","vx_zy", "vx_zxy","vy_zx","vy_zy","vy_zxy","v_zx","v_zy","v_zxy",
"zz","zx","zy","zxy","11","33"]

with cols1:
    toggle1 = st.selectbox("section", nameSec)
with cols2:
    toggle2 =  st.selectbox("combination", list(tension[toggle1].keys()))
with cols3:
    toggle3 = st.selectbox( "tension plot", resultOpt, index=0)

fig, axs = plt.subplots(1, 1, figsize=(9, 3), sharey=True)         
tension[toggle1][toggle2].plot_stress(stress=toggle3, ax=axs, fmt="{x:.2f}")
st.pyplot(fig)

