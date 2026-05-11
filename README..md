# Sistema Inteligente de Nutrición y Fitness
Este proyecto es una aplicación web que genera planes de nutrición y entrenamiento personalizados. Utiliza Inteligencia Artificial para entender las necesidad del usuario mediante NLP (procesamiento del lenguaje natural), y procesar esa información a través de un motor de reglas experto

## Arquitectura del Proyecto
El sistema se divide en tres capas principales que trabajan en conjunto: 

### 1. Módulo de Procesamiento de Lenguaje Natural
Este modelo está basado en spaCy, este módulo actúa como el traductor del sistema.

- Análisis gramatical: utiliza el modelo **`es_core_news_sm`** para procesar el texto.
- Extracción de inteciones: emplea el **`Matcher`** para identificar objetivos mediante **`Lemas`**, en este caso reconocer términos como "perder","perdiendo", o "adelgazar".
- Detección de entidades: identifica condiciones de salud analizando estructuras de **Sustantivo + Adjetivo**, como pueden ser términos como "lesión crónica".
  

### 2. Motor de Inferencia 
Utilizamos la librería **Experta**, para simular el razonamiento de un nutricionista humano.
- Base de hechos: almacena los datos de usuarios, datos como el sexo, peso, altura y objetivo.
- Base de reglas: aplica lógica condicional, como la fórmula de Mifflin-St Jeor para calcular calorías y asignar tipos de dieta según el perfil.
- Resolución de conflictos: gestiona alertas de salud para evitar ejercicios o alimentos no recomendados.


### 3. Backend y API
He creado una API en FastAPI (python), que sirve como puente de comunicación:
- Recibe los datos del Frontend como petición POST.



## Requisitos e Instalación
Para ejecutar el proyecto localmente, sigue estos pasos:
### 1. Instalar dependencias:
```
pip install fastapi uvicorn spacy experta
```

Si no te funciona el comando anteriormente, prueba a instalar con python
```
python - m pip install fastapi uvicorn spacy experta
```

### 2. Descargar el modelo de lenguaje español:
```
python -m spacy download es_core_news_sm
```

### 3. Ejecutar el servidor
Desde la raíz del proyecto ejecuta:
```
python -m uvicorn backend.main:app --reload
```

### 4. Abrir la interfaz
Abre el index.html, utilizando un servidor local como puede serlo Live Server dentro de Visual Studio Code.
