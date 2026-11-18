# 📘 Mi vocabulario de inglés

App de Streamlit para guardar las palabras de inglés que aprendo (finanzas y negocios):
palabra, significado en español, categoría gramatical y una frase de ejemplo con su traducción.

- **Por aprender**: tarjetas que se voltean al tocarlas (frente: palabra; reverso: significado, categoría, ejemplo y su traducción). Cada tarjeta tiene un ícono minimalista de referencia y un botón para escuchar la pronunciación de la palabra y del ejemplo. Botón ✅ Aprendida.
- **Aprendidas**: carpeta con las palabras que ya sabes (puedes devolverlas a estudiar).
- **Agregar palabra**: formulario para sumar palabras nuevas.

Las palabras viven en `palabras.csv`.

## Guardar los cambios para siempre (palabras aprendidas y nuevas)

Streamlit Cloud borra los cambios cuando la app se reinicia. Para que se guarden en GitHub
(y se vean igual en el celular y en la computadora):

1. Crea un token en https://github.com/settings/personal-access-tokens/new
   - Repository access: **Only select repositories** → `Vocabulario-Ingles`
   - Permissions → Repository permissions → **Contents: Read and write**
2. En share.streamlit.io, en tu app: **⋮ → Settings → Secrets**, pega y guarda:

```toml
GITHUB_TOKEN = "github_pat_..."
GITHUB_REPO = "jhonanthonyf-arch/Vocabulario-Ingles"
GITHUB_BRANCH = "main"
```

## Correr en tu computadora

```bash
pip install -r requirements.txt
streamlit run app.py
```

Íconos: [Lucide](https://lucide.dev) (licencia ISC, ver `iconos/LICENSE-lucide.txt`).
