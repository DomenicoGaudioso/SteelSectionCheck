import tempfile
import zipfile

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from codes import calcPro, elenca_files_cartella, importSection
from steel_builtup import (
    WeldedISectionInput,
    property_table,
    stress_check_table,
    validate_welded_i,
    welded_i_plot,
    welded_i_properties,
)
from steel_word import genera_word_steel


st.set_page_config(page_title="SteelSectionCheck", layout="wide")


def extract_zip(uploaded_file, output_folder: str) -> str:
    with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
        zip_ref.extractall(output_folder)
    return output_folder


def format_numeric_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    out = dataframe.copy()
    for column in out.columns:
        out[column] = out[column].apply(lambda value: f"{value:.4g}" if isinstance(value, float) else value)
    return out


def dxf_properties_to_table(properties: dict[str, dict[str, float]]) -> pd.DataFrame:
    dataframe = pd.DataFrame(properties).T.reset_index(names="Sezione")
    return dataframe


def draw_section_preview(section):
    fig, axs = plt.subplots(1, 2, figsize=(9, 3), sharey=True)
    section.plot_mesh(ax=axs[0])
    section.plot_centroids(ax=axs[1])
    axs[0].set_title("Mesh")
    axs[1].set_title("Baricentri")
    fig.tight_layout()
    return fig


def welded_input_table(data: WeldedISectionInput) -> pd.DataFrame:
    rows = [
        ("h", data.h, "mm"),
        ("bf superiore", data.bf_top, "mm"),
        ("tf superiore", data.tf_top, "mm"),
        ("bf inferiore", data.bf_bottom, "mm"),
        ("tf inferiore", data.tf_bottom, "mm"),
        ("tw", data.tw, "mm"),
        ("fy", data.fy, "MPa"),
        ("gammaM0", data.gamma_m0, "-"),
    ]
    return pd.DataFrame(rows, columns=["Parametro", "Valore", "Unita"])


st.title("SteelSectionCheck")
st.caption("Analisi di sezioni in acciaio da DXF o da geometria composta saldata.")

mode = st.sidebar.radio(
    "Sorgente sezione",
    ["Sezione composta saldata a doppio T", "Import DXF da ZIP"],
)

if mode == "Import DXF da ZIP":
    st.markdown("## 1. Proprietà geometriche da DXF")
    uploaded_zip = st.file_uploader("Carica un archivio ZIP con file DXF", type=["zip"])
    angle = st.number_input("Rotazione sezioni [deg]", value=0.0, step=1.0)

    if uploaded_zip is None:
        st.info("Carica uno ZIP per avviare l'importazione delle sezioni DXF.")
    else:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                extract_path = extract_zip(uploaded_zip, temp_dir)
                dxf_files = elenca_files_cartella(extract_path, typeFile=".dxf")

                if not dxf_files:
                    st.warning("Nessun file DXF trovato nello ZIP.")
                else:
                    geometry_list = importSection(dxf_files, rotate=angle)
                    geometry_list, dict_prop = calcPro(geometry_list)
                    properties_df = dxf_properties_to_table(dict_prop)

                    st.markdown("### 1.1 Sezioni importate")
                    st.dataframe(pd.DataFrame({"File DXF": dxf_files}), use_container_width=True, hide_index=True)

                    selected_section = st.selectbox("Sezione da visualizzare", list(geometry_list.keys()))
                    preview_fig = draw_section_preview(geometry_list[selected_section])
                    st.pyplot(preview_fig)

                    st.markdown("### 1.2 Proprietà calcolate")
                    st.dataframe(format_numeric_df(properties_df), use_container_width=True, hide_index=True)

                    docx = genera_word_steel(
                        titolo="SteelSectionCheck - relazione sezioni DXF",
                        modello="Importazione geometrica da DXF",
                        properties_df=properties_df,
                        figure=preview_fig,
                        note="Le proprieta' sono calcolate con sectionproperties sulla mesh generata dai file DXF.",
                    )
                    st.download_button(
                        "Scarica relazione Word",
                        data=docx,
                        file_name="SteelSectionCheck_DXF.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )
        except Exception as exc:
            st.error(f"Impossibile completare l'analisi DXF: {exc}")

else:
    st.markdown("## 1. Sezione composta saldata a doppio T")

    with st.sidebar:
        h = st.number_input("Altezza h [mm]", min_value=1.0, value=500.0, step=10.0)
        bf_top = st.number_input("Ala superiore bf [mm]", min_value=1.0, value=220.0, step=10.0)
        tf_top = st.number_input("Spessore ala superiore tf [mm]", min_value=1.0, value=18.0, step=1.0)
        bf_bottom = st.number_input("Ala inferiore bf [mm]", min_value=1.0, value=220.0, step=10.0)
        tf_bottom = st.number_input("Spessore ala inferiore tf [mm]", min_value=1.0, value=18.0, step=1.0)
        tw = st.number_input("Spessore anima tw [mm]", min_value=1.0, value=10.0, step=1.0)
        fy = st.number_input("fy [MPa]", min_value=1.0, value=355.0, step=5.0)
        gamma_m0 = st.number_input("gammaM0 [-]", min_value=0.1, value=1.05, step=0.05)

    section_input = WeldedISectionInput(
        h=h,
        bf_top=bf_top,
        tf_top=tf_top,
        bf_bottom=bf_bottom,
        tf_bottom=tf_bottom,
        tw=tw,
        fy=fy,
        gamma_m0=gamma_m0,
    )

    try:
        validate_welded_i(section_input)
        props = welded_i_properties(section_input)
        input_df = welded_input_table(section_input)
        props_df = property_table("Doppia T saldata", props)
        section_fig = welded_i_plot(section_input, props)

        st.markdown("### 1.1 Dati geometrici")
        st.dataframe(format_numeric_df(input_df), use_container_width=True, hide_index=True)

        st.markdown("### 1.2 Schema della sezione")
        st.pyplot(section_fig)

        st.markdown("### 1.3 Proprietà geometriche")
        st.dataframe(format_numeric_df(props_df), use_container_width=True, hide_index=True)

        st.markdown("## 2. Verifica elastica di tensione")
        n_ed = st.number_input("NEd [kN]", value=0.0, step=10.0)
        mx_ed = st.number_input("Mx,Ed [kNm]", value=0.0, step=10.0)
        my_ed = st.number_input("My,Ed [kNm]", value=0.0, step=10.0)
        checks_df = stress_check_table(section_input, props, n_ed, mx_ed, my_ed)
        st.dataframe(format_numeric_df(checks_df), use_container_width=True, hide_index=True)

        docx = genera_word_steel(
            titolo="SteelSectionCheck - relazione sezione saldata",
            modello="Sezione composta saldata a doppio T",
            input_df=input_df,
            properties_df=props_df,
            checks_df=checks_df,
            figure=section_fig,
            note=(
                "La verifica elastica considera le tensioni normali ai quattro estremi delle ali. "
                "Il valore di J e' stimato con formula sottile aperta."
            ),
        )
        st.download_button(
            "Scarica relazione Word",
            data=docx,
            file_name="SteelSectionCheck_DoppiaT.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
    except ValueError as exc:
        st.error(str(exc))
