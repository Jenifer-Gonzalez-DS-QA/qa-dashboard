# 📊 QA Dashboard — API Quality Metrics

Dashboard interactivo de métricas de calidad generado automáticamente con *Python + pandas + Plotly*.
Combina automatización de pruebas de API con análisis de datos para visualizar el estado de calidad en tiempo real.

> *API usada:* [JSONPlaceholder](https://jsonplaceholder.typicode.com) — gratuita, sin registro, sin API key, disponible 24/7.

> 💡 Este proyecto une dos perfiles: *QA Automation + Data Science* — una combinación poco común y muy valorada en equipos de ingeniería modernos.

-----

## 📌 Tabla de Contenidos

- [¿Qué hace este proyecto?](#qué-hace-este-proyecto)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación](#instalación)
- [Cómo Usarlo](#cómo-usarlo)
- [Flujo de Datos](#flujo-de-datos)
- [Cómo leer el Dashboard](#cómo-leer-el-dashboard)
- [Autora](#autora)

-----

## ¿Qué hace este proyecto?

1. *Ejecuta 22 pruebas automatizadas* contra la API REST de JSONPlaceholder (GET, POST, PUT, PATCH, DELETE sobre posts, usuarios, comentarios y todos)
1. *Guarda los resultados* en un archivo CSV acumulativo con timestamp, status real, tiempo de respuesta y resultado pass/fail
1. *Analiza los datos* con pandas: tasa de éxito, métricas por método HTTP, pruebas más lentas, tendencias entre ejecuciones
1. *Genera un dashboard HTML interactivo* con plotly: KPIs, gráficas y tabla de fallos — sin necesidad de servidor

Todo con un solo comando:

bash
python main.py


-----

## 🛠 Tecnologías

|Herramienta|Versión|Uso                            |
|-----------|-------|-------------------------------|
|Python     |3.11+  |Lenguaje base                  |
|requests   |2.31.0 |Ejecución de pruebas HTTP      |
|pandas     |2.1.4  |Análisis de métricas de calidad|
|plotly     |5.18.0 |Visualizaciones interactivas   |

-----

## 📁 Estructura del Proyecto


qa-dashboard/
│
├── test_runner.py      # Ejecuta las 22 pruebas y guarda resultados en CSV
├── analyzer.py         # Carga el CSV y calcula métricas con pandas
├── dashboard.py        # Genera el dashboard HTML interactivo con plotly
├── main.py             # Punto de entrada — orquesta el flujo completo
│
├── data/
│   └── test_results.csv    # Resultados acumulados (generado automáticamente)
│
├── reports/
│   └── dashboard.html      # Dashboard generado (abrir en navegador)
│
├── requirements.txt
├── .gitignore
└── README.md


-----

## ⚙️ Instalación

bash
# 1. Clonar el repositorio
git clone https://github.com/Jenifer-Gonzalez-DS-QA/qa-dashboard.git
cd qa-dashboard

# 2. Crear entorno virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt


-----

## ▶️ Cómo Usarlo

### Flujo completo (recomendado)

bash
python main.py


Esto ejecuta las 3 etapas en secuencia y abre el dashboard.

### Por etapas (para depuración o aprendizaje)

bash
# 1. Solo ejecutar pruebas y guardar CSV
python test_runner.py

# 2. Solo analizar resultados en consola
python analyzer.py

# 3. Solo regenerar el dashboard HTML
python dashboard.py


### Ver el dashboard

Abre el archivo en tu navegador:


reports/dashboard.html


> 💡 *Tip clave:* Ejecuta python main.py varias veces (3-5 veces) para que aparezca la gráfica de *tendencia en el tiempo*. Cada ejecución acumula resultados en el CSV y el dashboard los visualiza.

-----

## 🔄 Flujo de Datos


python main.py
      │
      ▼
test_runner.py
  Ejecuta 22 pruebas HTTP
  Mide tiempo de cada respuesta
  Compara status real vs esperado
      │
      ▼
data/test_results.csv
  timestamp, test_name, method, endpoint,
  expected_status, actual_status, passed, response_time_ms, error
      │
      ▼
analyzer.py  (pandas)
  ✔ Tasa de éxito global
  ✔ Métricas por método HTTP
  ✔ Top 5 pruebas más lentas
  ✔ Listado de pruebas fallidas
  ✔ Tendencia entre ejecuciones
      │
      ▼
dashboard.py  (plotly)
      │
      ▼
reports/dashboard.html → Abrir en navegador 🌐


-----

## 📊 Cómo leer el Dashboard

Abre reports/dashboard.html en tu navegador. De arriba hacia abajo:

### 1. KPIs — Indicadores Clave

6 tarjetas con los números más importantes:

- *Tasa de Éxito %* — el número más importante. Meta: 100%
- *Pasaron / Fallaron* — conteo absoluto
- *Tiempo Promedio / Máximo / Mínimo* — en milisegundos. Un tiempo alto puede indicar un problema de red o un endpoint lento

### 2. Gráfica Donut — Distribución Pass/Fail

El porcentaje en el centro es tu tasa de éxito. El verde son pruebas que pasaron, el rojo las que fallaron.

### 3. Barras por Método HTTP

Muestra la tasa de éxito agrupada por GET, POST, PUT, PATCH, DELETE.

- Si DELETE tiene 0% de éxito → ese método tiene un problema
- Si GET tiene 100% pero POST tiene 50% → hay algo específico con la creación de recursos

### 4. Top 5 Pruebas más Lentas

Barras horizontales con gradiente de color: azul = rápido, rojo = lento.
Un endpoint que tarda más de 1000ms merece investigación.

### 5. Tendencia en el Tiempo

Línea doble: % de éxito (verde) y tiempo promedio (azul punteado) a lo largo de varias ejecuciones.
Solo aparece si has ejecutado python main.py más de una vez.

- Si el % de éxito baja de una ejecución a otra → algo cambió en la API
- Si el tiempo sube sostenidamente → posible problema de rendimiento

### 6. Tabla de Pruebas Fallidas

Detalle de cada prueba que falló con: nombre, método, status real, status esperado y mensaje de error.
Si está vacía (o aparece el mensaje “¡Todas las pruebas pasaron!”) → todo está perfecto ✅

-----

## 👩‍💻 Autora

*Jenifer Gonzalez*
QA Engineer | Data Science | Scrum Master 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin)](www.linkedin.com/in/jenifer-paola-gonzalez-peñuela)
[![GitHub](https://img.shields.io/badge/GitHub-black?style=flat&logo=github)](https://github.com/Jenifer-Gonzalez-DS-QA/jenifergon91))

-----

> 💡 *Este proyecto es parte de un portafolio de 3 proyectos de automatización QA.
> Ver también: [API Testing Framework](https://github.com/Jenifer-Gonzalez-DS-QA/api-testing-framework) y [QA CI/CD Pipeline](https://github.com/Jenifer-Gonzalez-DS-QA/qa-cicd-pipeline)*
