# 📘 Mi vocabulario de inglés

App de Streamlit para guardar las palabras de inglés que aprendo (finanzas y negocios):
palabra, significado en español, categoría gramatical y una frase de ejemplo con su traducción.

- **Por aprender**: tarjetas que se voltean al tocarlas (frente: palabra; reverso: significado, categoría, ejemplo y su traducción). Botón ✅ Aprendida.
- **Aprendidas**: carpeta con las palabras que ya sabes (puedes devolverlas a estudiar).
- **Agregar palabra**: formulario para sumar palabras nuevas.

Las palabras viven en `palabras.csv`.

## Guardar palabras nuevas de forma permanente (opcional)

En Streamlit Cloud, las palabras agregadas desde la app se pierden cuando la app se reinicia,
a menos que la app pueda escribir en GitHub. Para eso, en la app de Streamlit Cloud ve a
**Settings → Secrets** y pega:

```toml
GITHUB_TOKEN = "tu_token_de_github"
GITHUB_REPO = "tu_usuario/vocabulario-ingles"
GITHUB_BRANCH = "main"
```

El token se crea en GitHub → Settings → Developer settings → Fine-grained tokens,
solo para este repositorio, con permiso **Contents: Read and write**.

## Correr en tu computadora

```bash
pip install -r requirements.txt
streamlit run app.py
```
