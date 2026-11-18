# 📘 Mi vocabulario de inglés

App de Streamlit para guardar las palabras de inglés que aprendo (finanzas y negocios):
palabra, significado en español, categoría gramatical y una frase de ejemplo.

- **Mis palabras**: tabla con buscador y filtro por categoría.
- **Por categoría**: las palabras agrupadas (noun, verb, phrasal verb, expression…) con su ejemplo.
- **Agregar palabra**: formulario para sumar palabras nuevas.
- **Repaso**: tarjetas para practicar.

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
