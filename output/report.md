# Guía Completa y Actualizada para Escribir Tests Unitarios en Python (2025)

¡Hey, qué tal, Pythonista curioso! 👋 ¿Alguna vez tocaste tu código, pensaste ‘esto no va a romper nada’, y dos segundos después todo explotó? Hoy vamos a ponerle fin a ese ciclo de terror con **tests unitarios**. Literalmente tu seguro de vida como developer en 2025... ¡y para siempre!

---

## 🔥 Introducción: ¿Por qué necesitas tests unitarios?

Imagina que tu código es como una torre de Jenga después de tres cafés: cada vez que quitas algo (o lo optimizas), tienes miedo de que todo se venga abajo. ¿La solución? ¡Tests unitarios! Así puedes refactorizar, agregar features, o trabajar en equipo sin sudar frío.

En este video te voy a enseñar **qué son los tests unitarios, por qué importan, cuáles frameworks están de moda en 2025 y cómo escribir tus propios tests con Pytest** usando ejemplos claros, directos y (casi) sin drama. Al final, serás capaz de:
- Escribir tests simples, parametrizados y con mocks.
- Integrar tus tests con CI/CD como un pro.
- Evitar los errores más comunes y lograr que tus tests sean útiles de verdad.

¿Listo? Si ya conoces la intro y quieres ir directo al código, salta al minuto [3:27].

---

## 🧠 ¿Qué son los tests unitarios? (Y por qué a ti sí te importan)

Un **test unitario** es como un mini guardia de seguridad para cada función: la examina en aislamiento y se asegura de que hace EXACTAMENTE lo que esperas. Cambias algo y... ¡PUM!, el test te avisa si rompiste algo.

### Ventajas rápidas:
- Previenen regresiones (errores fantasmas de features pasadas).
- Facilitan refactorización con confianza.
- Mejoran la calidad y mantenibilidad del código.
- Son la base para CI/CD sin miedo.

¿Quién no quiere dormir tranquilo?

---

## 🏆 Los frameworks top para testear en Python en 2025

### 1. **unittest**
- Parte de la librería estándar (no instalas nada extra).
- Basado en clases, inspiradísimo en Java.
- Verboso, pero muy confiable para empezar.

```python
import unittest

def suma(a, b):
    return a + b

class TestSum(unittest.TestCase):
    def test_suma(self):
        self.assertEqual(suma(2, 3), 5)

if __name__ == "__main__":
    unittest.main()
```

### 2. **pytest** (el rey en 2025 👑)
- Sintaxis mucho más fresca y natural (funciones normales, sin clases).
- Fixture, parametrización y plugins hasta para hacerte un café.
- Adoptado por startups, unicornios y tu proyecto personal.

```python
def suma(a, b):
    return a + b

def test_suma():
    assert suma(2, 3) == 5
```
**Tendencia:** Si inicias algo desde cero hoy, casi seguro usas pytest.

### 3. Otros que debes conocer
- **nose2**: Fue boom, ahora es más de nicho.
- **Hypothesis**: Testear propiedades de tu código (genera casos locos automáticamente).
- **Doctest**: Si te gusta poner tests en los docstrings.
- **Robot/Behave**: Testing de “aceptación” o historias de usuario.

---

## 🗂️ Organización y estructura de tus tests (¡Esto sí importa!)

- Pon tus tests en carpeta aparte (`tests/`)
- Nómbralos bien: `test_funcion.py`, `TestMiClase`
- Un test, una verificación.
- Reutiliza fixtures y mocks (nada de copiar/pegar archivos gigantes).

**¿Cómo se ve un proyecto bien estructurado?**
```
mi_proyecto/
│
├── src/
│    └── mi_modulo.py
│
└── tests/
     ├── __init__.py
     └── test_mi_modulo.py
```

---

## ✨ Mejores prácticas para 2025

- Testea temprano y testea SIEMPRE (cada cambio, cada feature)
- Mantenlos independientes (nada de ‘si falla el anterior ya nada jala’)
- Cubre casos borde, no solo el happy path.
- Mocks para lo externo.
- Automatiza todo en CI/CD.
- ¡No te vuelvas esclavo de la cobertura! Mejor pocos tests útiles, que muchos inútiles.
- Refactoriza tests igual que el código real.
- Usa validación de tipos (`mypy`) cuando puedas.

---

## 🔬 Ejemplos paso a paso con pytest

### 1. **Test básico**
```python
def suma(a, b):
    return a + b

def test_suma():
    assert suma(2, 3) == 5
```

### 2. **Tests parametrizados (casos a lo bestia)**
```python
import pytest

@pytest.mark.parametrize("a, b, esperado", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_suma_parametros(a, b, esperado):
    assert suma(a, b) == esperado
```

### 3. **Fixtures (Preparando datos de forma inteligente)**
```python
import pytest

@pytest.fixture
def datos():
    return {"a": 2, "b": 3}

def test_suma_fixture(datos):
    assert suma(datos["a"], datos["b"]) == 5
```

### 4. **Mocks: Simulando lo que no quieres tocar**
```python
from unittest.mock import patch

def obtener_precio_apiexterna():
    raise NotImplementedError  # Simula llamada a API real

def test_obtener_precio(monkeypatch):
    monkeypatch.setattr("mimodulo.obtener_precio_apiexterna", lambda: 7.5)
    assert obtener_precio_apiexterna() == 7.5
```
¡Y con `pytest-mock`, aún mejor!
```python
def test_precio(mocker):
    mocker.patch("mimodulo.obtener_precio_apiexterna", return_value=8.2)
    assert obtener_precio_apiexterna() == 8.2
```

### 5. **Tests pendientes o que DEBEN fallar**
```python
import pytest

@pytest.mark.xfail
def test_funcion_no_implementada():
    assert funcion_no_hecha() == 10

@pytest.mark.skip(reason="Funcionalidad en desarrollo")
def test_funcion_en_desarrollo():
    pass
```

---

## 🔥 Comparativa ultra–rápida: unittest vs pytest vs el resto

| Característica      | unittest           | pytest           | nose2/Hypothesis |
|--------------------|--------------------|------------------|------------------|
| Sintaxis           | Verboso            | Ligero/natural   | Intermedia       |
| Parametrización    | Manual             | Decoradores      | En plugins       |
| Fixtures           | setUp/tearDown     | Muy poderosos    | Limitados        |
| Plugins            | Pocos              | Muchísimos       | Pocos            |
| Mocking            | mock               | mock/mocker      | Básico           |
| Cobertura          | Plugin             | pytest-cov       | Limitado         |

Traducción: Para casi todo, prueba primero con pytest ;)


---

## 🚀 Automatización, CI/CD y métricas de calidad

- Ejecútalos en cada push/pull request con GitHub Actions, GitLab CI, Jenkins...
- Ejemplo mínimo con **GitHub Actions:**

```yaml
name: Python Tests

on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest --cov=src --cov-report=xml
```

- **Cobertura de código:**
```sh
pytest --cov=src tests/
```
- **Umbral mínimo recomendado:**
```sh
pytest --cov=src --cov-fail-under=85
```

---

## 💡 Consejos, errores típicos y hacks pro

### Tips
- Escribe tests atómicos y claros (nada de monstruos de 300 líneas).
- Asegura feedback rápido: ¡tests veloces o nada!
- Automatiza hasta la revisión de tests en pre-commit si puedes.
- Usa `pytest.mark.parametrize` y `hypothesis` para casos de prueba inteligentes.

### Errores mortales
- Tests que dependen del estado, internet o una DB  (¡aislamiento siempre!).
- No limpiar recursos tras cada test.
- Medir “calidad” por cobertura: busca valor, no sólo estadística.

### Casos de uso ideales
- Validar funciones pequeñitas, cálculos, transformaciones.
- Verificar validadores y utilidades.
- Mantener código legacy bajo control sin miedo a cambios.

---

## 🚀 Tendencias y futuro en 2025 (¡No te quedes atrás!)

- **pytest sigue dominando**
- Combinación de type checking (`mypy`) y testing.
- Testing por "property–based" (con Hypothesis)
- Tests en paralelo, en local y CI (¡velocidad total!)
- Feedback automático con pre-commit y reportería visual en CI con badges (Codecov, etc).

---

## 📚 Recursos recomendados
- [Documentación oficial de pytest](https://docs.pytest.org/)
- [pytest-cov (cobertura)](https://pytest-cov.readthedocs.io/en/latest/)
- [Quick pytest cheatsheet](https://github.com/augustogoulart/pytest-cheat-sheet)
- [Best Practices for Writing Unit Tests in Python (Medium)](https://medium.com/infosecmatrix/best-practices-for-writing-unit-tests-in-python-cd1da23d3b79)
- [11 Top Python Testing Frameworks in 2025](https://www.ongraph.com/top-python-testing-frameworks/)
- [Pytest vs. Unittest en profundidad](https://builtin.com/data-science/pytest-vs-unittest)

---

## 🎬 Cierre poderoso

¡Y listo! Hoy aprendiste desde cero hasta moderno cómo escribir tests unitarios en Python como se hace HOY (bueno, en 2025). Vimos frameworks, prácticas y hasta integración en el mundo real.

**Resumen flash:**
1. Tests te salvan la vida dev (y la de tu equipo)
2. Unittest si quieres clásico, PYTEST si quieres un superpoder.
3. Automatiza, innova y duerme en paz.

¿Te sirvió el video? Dale like, suscríbete y cuéntame en los comentarios qué testing nightmare has superado últimamente…

¡Nos vemos en el próximo video! Y mientras tanto… ¡Testea TODO! 🐍💥