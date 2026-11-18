"""Mi vocabulario de inglés: app de Streamlit para guardar las palabras que aprendo."""

import base64
import io
import random
from datetime import date
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

ARCHIVO = Path(__file__).parent / "palabras.csv"
COLUMNAS = ["palabra", "significado", "categoria", "ejemplo", "fecha"]
CATEGORIAS = [
    "noun", "verb", "phrasal verb", "adjective", "adverb",
    "expression", "preposition", "connector",
]
NOMBRE_ES = {
    "noun": "sustantivo", "verb": "verbo", "phrasal verb": "verbo compuesto",
    "adjective": "adjetivo", "adverb": "adverbio", "expression": "expresión",
    "preposition": "preposición", "connector": "conector",
}

st.set_page_config(page_title="Mi vocabulario de inglés", page_icon="📘", layout="wide")


# ---------- Guardar y leer ----------

def github_configurado() -> bool:
    try:
        return "GITHUB_TOKEN" in st.secrets and "GITHUB_REPO" in st.secrets
    except Exception:
        return False


def leer_palabras() -> pd.DataFrame:
    if ARCHIVO.exists():
        df = pd.read_csv(ARCHIVO, dtype=str).fillna("")
    else:
        df = pd.DataFrame(columns=COLUMNAS)
    return df[COLUMNAS]


def guardar_en_github(contenido: str) -> None:
    """Sube palabras.csv al repositorio para que no se pierda al reiniciar la app."""
    repo = st.secrets["GITHUB_REPO"]
    rama = st.secrets.get("GITHUB_BRANCH", "main")
    url = f"https://api.github.com/repos/{repo}/contents/palabras.csv"
    cabeceras = {
        "Authorization": f"Bearer {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    actual = requests.get(url, headers=cabeceras, params={"ref": rama}, timeout=15)
    sha = actual.json().get("sha") if actual.status_code == 200 else None
    datos = {
        "message": "Agregar palabra desde la app",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("ascii"),
        "branch": rama,
    }
    if sha:
        datos["sha"] = sha
    r = requests.put(url, headers=cabeceras, json=datos, timeout=15)
    r.raise_for_status()


def guardar_palabras(df: pd.DataFrame) -> str:
    contenido = df[COLUMNAS].to_csv(index=False)
    ARCHIVO.write_text(contenido, encoding="utf-8")
    if github_configurado():
        try:
            guardar_en_github(contenido)
            return "github"
        except Exception as e:  # noqa: BLE001
            st.error(f"No se pudo guardar en GitHub: {e}")
    return "local"


# ---------- Interfaz ----------

df = leer_palabras()

st.title("📘 Mi vocabulario de inglés")
st.caption("Palabras de finanzas y negocios que voy aprendiendo, con su significado, categoría y un ejemplo.")

c1, c2, c3 = st.columns(3)
c1.metric("Palabras guardadas", len(df))
c2.metric("Categorías", df["categoria"].nunique())
hoy = date.today().isoformat()
c3.metric("Agregadas hoy", int((df["fecha"] == hoy).sum()))

tab_lista, tab_categorias, tab_agregar, tab_repaso = st.tabs(
    ["📋 Mis palabras", "🗂️ Por categoría", "➕ Agregar palabra", "🎯 Repaso"]
)

# --- Lista con filtros ---
with tab_lista:
    f1, f2 = st.columns([1, 2])
    opciones = sorted(df["categoria"].unique())
    elegidas = f1.multiselect(
        "Filtrar por categoría", opciones,
        format_func=lambda c: f"{c} ({NOMBRE_ES.get(c, c)})",
    )
    buscar = f2.text_input("Buscar (en inglés o español)")
    vista = df.copy()
    if elegidas:
        vista = vista[vista["categoria"].isin(elegidas)]
    if buscar:
        b = buscar.lower()
        vista = vista[
            vista["palabra"].str.lower().str.contains(b, regex=False)
            | vista["significado"].str.lower().str.contains(b, regex=False)
        ]
    st.dataframe(
        vista.sort_values("palabra"),
        hide_index=True,
        width="stretch",
        column_config={
            "palabra": "Palabra",
            "significado": "Significado",
            "categoria": "Categoría",
            "ejemplo": st.column_config.TextColumn("Ejemplo", width="large"),
            "fecha": "Fecha",
        },
    )
    st.download_button(
        "⬇️ Descargar mis palabras (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="palabras.csv",
        mime="text/csv",
    )

# --- Por categoría ---
with tab_categorias:
    st.write("Cada categoría gramatical con sus palabras y un ejemplo de cada una.")
    for cat in sorted(df["categoria"].unique()):
        grupo = df[df["categoria"] == cat].sort_values("palabra")
        with st.expander(f"**{cat}** · {NOMBRE_ES.get(cat, cat)} · {len(grupo)} palabras"):
            for _, fila in grupo.iterrows():
                st.markdown(
                    f"**{fila['palabra']}** = {fila['significado']}  \n"
                    f"<span style='opacity:0.75'>✏️ <i>{fila['ejemplo']}</i></span>",
                    unsafe_allow_html=True,
                )

# --- Agregar ---
with tab_agregar:
    with st.form("nueva", clear_on_submit=True):
        palabra = st.text_input("Palabra en inglés *")
        significado = st.text_input("Significado en español *")
        categoria = st.selectbox(
            "Categoría gramatical *", CATEGORIAS,
            format_func=lambda c: f"{c} ({NOMBRE_ES[c]})",
        )
        ejemplo = st.text_area("Frase de ejemplo en inglés *", height=80)
        enviar = st.form_submit_button("Guardar palabra", type="primary")
    if enviar:
        if not (palabra.strip() and significado.strip() and ejemplo.strip()):
            st.warning("Completa todos los campos.")
        elif palabra.strip().lower() in df["palabra"].str.lower().values:
            st.warning(f"“{palabra}” ya está en tu lista.")
        else:
            nueva = pd.DataFrame([{
                "palabra": palabra.strip(), "significado": significado.strip(),
                "categoria": categoria, "ejemplo": ejemplo.strip(), "fecha": hoy,
            }])
            df = pd.concat([df, nueva], ignore_index=True)
            donde = guardar_palabras(df)
            if donde == "github":
                st.success(f"✅ “{palabra}” guardada en GitHub.")
            else:
                st.success(f"✅ “{palabra}” guardada.")
                if not github_configurado():
                    st.info(
                        "Ojo: sin la conexión a GitHub configurada, en internet la palabra "
                        "puede borrarse cuando la app se reinicie. Descarga el CSV como respaldo."
                    )
            st.rerun()

# --- Repaso tipo tarjetas ---
with tab_repaso:
    st.write("Mira la palabra, piensa el significado y luego revisa la respuesta.")
    if df.empty:
        st.info("Todavía no hay palabras.")
    else:
        cat_repaso = st.selectbox("Categoría", ["todas"] + sorted(df["categoria"].unique()))
        base = df if cat_repaso == "todas" else df[df["categoria"] == cat_repaso]
        if "tarjeta" not in st.session_state or st.session_state.tarjeta not in base.index:
            st.session_state.tarjeta = random.choice(list(base.index))
            st.session_state.ver = False
        fila = df.loc[st.session_state.tarjeta]
        st.markdown(f"## {fila['palabra']}")
        st.caption(fila["categoria"])
        b1, b2 = st.columns(2)
        if b1.button("Ver respuesta"):
            st.session_state.ver = True
        if b2.button("Siguiente palabra ➡️"):
            st.session_state.tarjeta = random.choice(list(base.index))
            st.session_state.ver = False
            st.rerun()
        if st.session_state.ver:
            st.success(f"**{fila['significado']}**")
            st.markdown(f"✏️ *{fila['ejemplo']}*")
