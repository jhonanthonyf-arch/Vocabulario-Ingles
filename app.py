"""Mi vocabulario de inglés: tarjetas que se voltean para aprender palabras de finanzas."""

import base64
import html
import io
import json
import re
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

ARCHIVO = Path(__file__).parent / "palabras.csv"
CARPETA_ICONOS = Path(__file__).parent / "iconos"
COLUMNAS = ["palabra", "significado", "categoria", "ejemplo", "ejemplo_es", "aprendida", "icono"]
CATEGORIAS = [
    "noun", "verb", "phrasal verb", "adjective", "adverb",
    "expression", "preposition", "connector",
]
NOMBRE_ES = {
    "noun": "sustantivo", "verb": "verbo", "phrasal verb": "verbo compuesto",
    "adjective": "adjetivo", "adverb": "adverbio", "expression": "expresión",
    "preposition": "preposición", "connector": "conector",
}
COLOR = {
    "noun": "#2563eb", "verb": "#16a34a", "phrasal verb": "#9333ea",
    "adjective": "#ea580c", "adverb": "#0891b2", "expression": "#db2777",
    "preposition": "#65a30d", "connector": "#ca8a04",
}
POR_FILA = 3

st.set_page_config(page_title="Mi vocabulario de inglés", page_icon="📘", layout="wide")

ICONO = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4V5z"/>'
         '<path d="M15.5 8.5a5 5 0 0 1 0 7"/><path d="M18.5 5.5a9 9 0 0 1 0 13"/></svg>')

ESTILO = """
<style>
body { margin: 0; padding: 4px; }
.flip { perspective: 1000px; height: 230px; position: relative; }
.voz { position: absolute; top: 10px; right: 10px; z-index: 5;
  width: 32px; height: 32px; padding: 0; border-radius: 999px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  background: transparent; border: 1.5px solid rgba(255,255,255,.7); color: #fff;
  transition: background .2s; }
.voz:hover { background: rgba(255,255,255,.15); }
.voz:active { transform: scale(.92); }
.flip input:checked ~ .voz { color: var(--c); border-color: var(--c); }
.voz svg, .voz-ej svg { width: 16px; height: 16px; }
.voz-ej { display: inline-flex; align-items: center; gap: 6px; margin-top: 10px;
  background: transparent; border: 1px solid #d1d5db; color: #4b5563;
  border-radius: 999px; padding: 3px 10px; font-size: .78rem; cursor: pointer; }
.voz-ej:hover { border-color: var(--c); color: var(--c); }
.flip input { display: none; }
.flip label { display: block; width: 100%; height: 100%; cursor: pointer; }
.cara-box { position: relative; width: 100%; height: 100%;
  transition: transform .6s; transform-style: preserve-3d; }
.flip input:checked ~ label .cara-box { transform: rotateY(180deg); }
.cara { position: absolute; inset: 0; backface-visibility: hidden;
  -webkit-backface-visibility: hidden; border-radius: 16px; padding: 18px;
  box-sizing: border-box; display: flex; flex-direction: column;
  justify-content: center; align-items: center; text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,.12); font-family: sans-serif; }
.frente { color: #fff; }
.frente .img { width: 64px; height: 64px; border-radius: 999px; margin-bottom: 12px;
  background: rgba(255,255,255,.14); display: flex; align-items: center; justify-content: center; }
.frente .img svg { width: 34px; height: 34px; color: #fff; }
.frente .pal { font-size: 1.6rem; font-weight: 700; line-height: 1.15; }
.frente .tip { font-size: .75rem; opacity: .75; margin-top: 10px; }
.reverso { background: #fff; color: #1f2937; transform: rotateY(180deg);
  border: 2px solid var(--c); justify-content: flex-start; overflow-y: auto; }
.reverso .sig { font-size: 1.25rem; font-weight: 700; margin: 4px 0 6px; }
.reverso .cat { display: inline-block; background: var(--c); color: #fff;
  border-radius: 999px; padding: 2px 10px; font-size: .75rem; }
.reverso .en { font-style: italic; margin-top: 12px; font-size: .95rem; }
.reverso .es { color: #6b7280; font-size: .9rem; margin-top: 4px; }
</style>
<script>
function hablar(ev, texto) {
  ev.preventDefault(); ev.stopPropagation();
  const synth = window.speechSynthesis || window.parent.speechSynthesis;
  if (!synth) { alert("Tu navegador no permite reproducir audio."); return; }
  synth.cancel();
  const u = new SpeechSynthesisUtterance(texto);
  u.lang = "en-GB"; u.rate = 0.85;
  // Preferir una voz británica; si el dispositivo no tiene, usar otra en inglés.
  const voces = synth.getVoices();
  const norm = x => (x.lang || "").replace("_", "-").toLowerCase();
  const v = voces.find(x => norm(x) === "en-gb")
         || voces.find(x => /british|uk|england/i.test(x.name))
         || voces.find(x => norm(x).startsWith("en"));
  try { if (v) u.voice = v; } catch (e) {}
  synth.speak(u);
}
</script>
"""


# ---------- Guardar y leer ----------

REPO_POR_DEFECTO = "jhonanthonyf-arch/Vocabulario-Ingles"


def _buscar(secretos, nombres):
    """Busca una clave sin importar mayúsculas, también dentro de secciones [algo]."""
    for k, v in secretos.items():
        if hasattr(v, "items"):
            r = _buscar(v, nombres)
            if r:
                return r
        elif k.strip().lower() in nombres and str(v).strip():
            return str(v).strip().strip('"').strip("“”").strip()
    return None


def config_github() -> dict:
    """Lee los Secrets de forma tolerante. Devuelve token, repo, rama y un 'problema' si lo hay."""
    try:
        secretos = dict(st.secrets)
    except Exception as e:  # noqa: BLE001
        texto = str(e)
        if "No secrets" in texto or "not found" in texto.lower():
            return {"problema": "La app no encuentra ningún Secret. Revisa que lo guardaste con Save en la app correcta."}
        return {"problema": "Los Secrets tienen un error de formato (revisa que las comillas sean rectas \" y no “ ”)."}
    token = _buscar(secretos, {"github_token", "token", "github_pat", "gh_token"})
    if not token:
        return {"problema": "Falta GITHUB_TOKEN en los Secrets."}
    repo = _buscar(secretos, {"github_repo", "repo"}) or REPO_POR_DEFECTO
    repo = repo.replace("https://github.com/", "").strip("/")
    rama = _buscar(secretos, {"github_branch", "branch"}) or "main"
    return {"token": token, "repo": repo, "rama": rama, "problema": None}


def github_configurado() -> bool:
    cfg = config_github()
    return cfg["problema"] is None and probar_github(cfg["token"], cfg["repo"]) is None


@st.cache_data(ttl=300, show_spinner=False)
def probar_github(token: str, repo: str) -> str | None:
    """Prueba el token. Devuelve None si todo está bien, o un mensaje simple del problema."""
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}", timeout=15,
                         headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    except Exception as e:  # noqa: BLE001
        return f"No se pudo conectar con GitHub ({e})."
    if r.status_code == 401:
        return "GitHub dice que el token no es válido o venció. Crea uno nuevo y pégalo en Secrets."
    if r.status_code == 404:
        return f"El token no tiene acceso al repositorio {repo}. Al crear el token elige ese repositorio."
    if r.status_code != 200:
        return f"GitHub respondió con error {r.status_code}."
    if not r.json().get("permissions", {}).get("push", False):
        return "El token puede leer pero no guardar. En Permissions → Contents elige 'Read and write'."
    return None


def _cabeceras() -> dict:
    return {
        "Authorization": f"Bearer {config_github()['token']}",
        "Accept": "application/vnd.github+json",
    }


def _url_github() -> str:
    return f"https://api.github.com/repos/{config_github()['repo']}/contents/palabras.csv"


@st.cache_data(ttl=30, show_spinner=False)
def leer_csv_github() -> str:
    """Trae la versión más reciente de palabras.csv desde GitHub (así el celular y la compu ven lo mismo)."""
    r = requests.get(
        _url_github(), timeout=15,
        headers={**_cabeceras(), "Accept": "application/vnd.github.raw+json"},
        params={"ref": config_github()["rama"]},
    )
    r.raise_for_status()
    return r.text


def leer_palabras() -> pd.DataFrame:
    df = None
    if github_configurado():
        try:
            df = pd.read_csv(io.StringIO(leer_csv_github()), dtype=str).fillna("")
        except Exception:  # noqa: BLE001
            df = None
    if df is None and ARCHIVO.exists():
        df = pd.read_csv(ARCHIVO, dtype=str).fillna("")
    if df is None:
        df = pd.DataFrame(columns=COLUMNAS)
    for col in COLUMNAS:
        if col not in df.columns:
            df[col] = {"aprendida": "no", "icono": "book-open"}.get(col, "")
    return df[COLUMNAS]


def guardar_en_github(contenido: str) -> None:
    """Sube palabras.csv al repositorio para que no se pierda al reiniciar la app."""
    rama = config_github()["rama"]
    actual = requests.get(_url_github(), headers=_cabeceras(), params={"ref": rama}, timeout=15)
    sha = actual.json().get("sha") if actual.status_code == 200 else None
    datos = {
        "message": "Actualizar palabras desde la app",
        "content": base64.b64encode(contenido.encode("utf-8")).decode("ascii"),
        "branch": rama,
    }
    if sha:
        datos["sha"] = sha
    requests.put(_url_github(), headers=_cabeceras(), json=datos, timeout=15).raise_for_status()
    leer_csv_github.clear()


def guardar_palabras(df: pd.DataFrame) -> None:
    contenido = df[COLUMNAS].to_csv(index=False)
    ARCHIVO.write_text(contenido, encoding="utf-8")
    if github_configurado():
        try:
            guardar_en_github(contenido)
        except Exception as e:  # noqa: BLE001
            st.session_state.aviso = ("error", f"No se pudo guardar en GitHub: {e}")


def marcar(df: pd.DataFrame, idx, valor: str) -> None:
    df.loc[idx, "aprendida"] = valor
    guardar_palabras(df)
    if "aviso" not in st.session_state:
        st.session_state.aviso = ("ok", "Guardado ✓" if github_configurado() else "Listo")
    st.rerun()


# ---------- Tarjetas ----------

@st.cache_data
def icono_svg(nombre: str) -> str:
    """Lee un ícono de línea (Lucide) de la carpeta iconos/."""
    archivo = CARPETA_ICONOS / f"{nombre}.svg"
    if not re.fullmatch(r"[a-z0-9-]+", nombre or "") or not archivo.exists():
        archivo = CARPETA_ICONOS / "book-open.svg"
    return archivo.read_text(encoding="utf-8").replace('stroke-width="2"', 'stroke-width="1.5"')


def iconos_disponibles() -> list[str]:
    return sorted(p.stem for p in CARPETA_ICONOS.glob("*.svg"))


def hablable(texto: str) -> str:
    """Quita lo que va entre paréntesis, p. ej. 'go up (went up)' -> 'go up, went up'."""
    return re.sub(r"\s*\((.*?)\)", r", \1", str(texto))


def tarjeta_html(idx, fila) -> str:
    e = lambda t: html.escape(str(t))  # noqa: E731
    js = lambda t: html.escape(json.dumps(hablable(t)))  # noqa: E731
    color = COLOR.get(fila["categoria"], "#475569")
    nombre = NOMBRE_ES.get(fila["categoria"], fila["categoria"])
    return f"""
<div class="flip" style="--c:{color}">
  <input type="checkbox" id="t{idx}">
  <button class="voz" title="Escuchar pronunciación"
    onclick="hablar(event, {js(fila['palabra'])})">{ICONO}</button>
  <label for="t{idx}"><div class="cara-box">
    <div class="cara frente" style="background:{color}">
      <div class="img">{icono_svg(fila['icono'] or 'book-open')}</div>
      <div class="pal">{e(fila['palabra'])}</div>
      <div class="tip">Toca para ver el significado</div>
    </div>
    <div class="cara reverso">
      <span class="cat">{e(fila['categoria'])} · {e(nombre)}</span>
      <div class="sig">{e(fila['significado'])}</div>
      <div class="en">“{e(fila['ejemplo'])}”</div>
      <div class="es">{e(fila['ejemplo_es'])}</div>
      <button class="voz-ej" onclick="hablar(event, {js(fila['ejemplo'])})">{ICONO} Escuchar ejemplo</button>
    </div>
  </div></label>
</div>"""


def mostrar_tarjetas(df: pd.DataFrame, vista: pd.DataFrame, aprendidas: bool) -> None:
    if vista.empty:
        st.info("No hay palabras aquí todavía." if not aprendidas else
                "Aún no marcaste palabras como aprendidas. ¡Tú puedes! 💪")
        return
    filas = list(vista.iterrows())
    for i in range(0, len(filas), POR_FILA):
        cols = st.columns(POR_FILA)
        for col, (idx, fila) in zip(cols, filas[i:i + POR_FILA]):
            with col:
                components.html(ESTILO + tarjeta_html(idx, fila), height=245)
                if aprendidas:
                    if st.button("↩️ Volver a estudiar", key=f"v{idx}", width="stretch"):
                        marcar(df, idx, "no")
                elif st.button("✅ Aprendida", key=f"a{idx}", width="stretch"):
                    marcar(df, idx, "si")


def filtros(df: pd.DataFrame, clave: str) -> pd.DataFrame:
    f1, f2 = st.columns([1, 2])
    elegidas = f1.multiselect(
        "Filtrar por categoría", sorted(df["categoria"].unique()),
        format_func=lambda c: f"{c} ({NOMBRE_ES.get(c, c)})", key=f"cat_{clave}", placeholder="Todas",
    )
    buscar = f2.text_input("Buscar (en inglés o español)", key=f"bus_{clave}")
    vista = df
    if elegidas:
        vista = vista[vista["categoria"].isin(elegidas)]
    if buscar:
        b = buscar.lower()
        vista = vista[
            vista["palabra"].str.lower().str.contains(b, regex=False)
            | vista["significado"].str.lower().str.contains(b, regex=False)
        ]
    return vista.sort_values("palabra")


# ---------- Página ----------

df = leer_palabras()
por_aprender = df[df["aprendida"] != "si"]
ya_aprendidas = df[df["aprendida"] == "si"]

st.title("📘 Mi vocabulario de inglés")
if "aviso" in st.session_state:
    tipo, texto = st.session_state.pop("aviso")
    st.error(texto) if tipo == "error" else st.toast(texto)
_cfg = config_github()
_problema = _cfg["problema"] or probar_github(_cfg["token"], _cfg["repo"])
if _problema:
    st.warning(
        "Tus cambios todavía no se guardan para siempre.  \n**Motivo:** " + _problema, icon="⚠️",
    )
c1, c2, c3 = st.columns(3)
c1.metric("Por aprender", len(por_aprender))
c2.metric("Aprendidas", len(ya_aprendidas))
c3.metric("Total", len(df))

tab_estudiar, tab_aprendidas, tab_agregar = st.tabs(
    [f"📚 Por aprender ({len(por_aprender)})",
     f"🏆 Aprendidas ({len(ya_aprendidas)})",
     "➕ Agregar palabra"]
)

with tab_estudiar:
    st.caption("Toca una tarjeta para voltearla. Cuando ya sepas la palabra, toca ✅ Aprendida.")
    mostrar_tarjetas(df, filtros(por_aprender, "estudiar"), aprendidas=False)

with tab_aprendidas:
    st.caption("Tu carpeta de palabras aprendidas. Puedes repasarlas o devolverlas a estudiar.")
    mostrar_tarjetas(df, filtros(ya_aprendidas, "aprendidas"), aprendidas=True)

with tab_agregar:
    with st.form("nueva", clear_on_submit=True):
        palabra = st.text_input("Palabra en inglés *")
        significado = st.text_input("Significado en español * (si tiene varios, sepáralos con /)")
        categoria = st.selectbox(
            "Categoría gramatical *", CATEGORIAS,
            format_func=lambda c: f"{c} ({NOMBRE_ES[c]})",
        )
        ejemplo = st.text_input("Frase de ejemplo en inglés *")
        ejemplo_es = st.text_input("Traducción del ejemplo al español *")
        lista = iconos_disponibles()
        icono = st.selectbox("Imagen de la tarjeta", lista, index=lista.index("book-open"))
        enviar = st.form_submit_button("Guardar palabra", type="primary")
    if enviar:
        campos = [palabra, significado, ejemplo, ejemplo_es]
        if not all(c.strip() for c in campos):
            st.warning("Completa todos los campos.")
        elif palabra.strip().lower() in df["palabra"].str.lower().values:
            st.warning(f"“{palabra}” ya está en tu lista.")
        else:
            nueva = pd.DataFrame([{
                "palabra": palabra.strip(), "significado": significado.strip(),
                "categoria": categoria, "ejemplo": ejemplo.strip(),
                "ejemplo_es": ejemplo_es.strip(), "aprendida": "no", "icono": icono,
            }])
            guardar_palabras(pd.concat([df, nueva], ignore_index=True))
            st.success(f"✅ “{palabra}” guardada.")
            st.rerun()

    st.download_button(
        "⬇️ Descargar respaldo de mis palabras (CSV)",
        df.to_csv(index=False).encode("utf-8"),
        file_name="palabras.csv", mime="text/csv",
    )
