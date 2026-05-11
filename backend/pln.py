import spacy
from spacy.matcher import Matcher

# Carga del modelo de lenguaje español de Spacy
nlp = spacy.load("es_core_news_sm")

class ModuloPLN:
    def __init__(self):
        # Vamos a inicializar matcher que trabaja con el vocabulario del modelo
        # recibe el vocabulario interno que mapea cada string
        self.matcher = Matcher(nlp.vocab)
        self._configurar_patrones()


    def _configurar_patrones(self):
        """Define patrones de búsqueda sobre el texto procesado"""
        # Cada patrón es una lista de diccionarios donde cada diccionario lo describe
        # LEMMA -> perder, POS -> categoría gramatical (nombre, verbo, adjetivo)
        # OP -> operador de repeteción -> 0 o 1 vez.
        """Entonces lo que haremos aquí será si detecta el lema perder seguido de un sustantivo, el lema
        permite capturar pierdo,perdiendo, perderás"""
        patron_perder = [{"LEMMA": "perder"}, {"POS": "NOUN", "OP": "?"}]

        # Detecta directamente el lema adelgazar sin necesidad de sustantivo
        patron_adelgazar = [{"LEMMA": "adelgazar"}]
        # Registramos ambos patrones bajo el mismo nombre, enotnces si cualquiera de los dos 
        # hace el match obtendremos match_id="OBJ_PERDER"
        self.matcher.add("OBJ_PERDER", [patron_perder, patron_adelgazar])


        """Este sería el patrón para ganar músculo o masa:
        No usamos OP=?, exigimos que haya un sustantivo detrás para confirmar la intención
        """
        patron_ganar = [{"LEMMA": "ganar"}, {"POS": "NOUN"}] # "ganar músculo"
        self.matcher.add("OBJ_GANAR", [patron_ganar])

        """Patrón para detectar condiciones de salud:
        Busca secuencias SUSTANTIVO + ADJETIVO, como lesión crónica, o rodilla lesionada,
        la inteción no es ser super específico sobre lesiones."""
        patron_salud = [{"POS": "NOUN"}, {"POS": "ADJ"}] 
        self.matcher.add("SALUD_DETECCION", [patron_salud])


    def extraer_datos(self, texto_usuario: str):
        """Procesa el texto y extrae la información"""
        doc = nlp(texto_usuario)
        
        # Diccionario base de resultados
        resultados = {
            "edad": 25, "peso": 70.0, "talla": 170.0,
            "sexo": "H", "objetivo": "perder_grasa", "salud": []
        }

        """doc.ents tiene las entidades que el modelo reconoce automáticamente, PER significa persona;
        se utiliza para personalizar el saludo o guardar el nombre sin que el usuario lo escriba en el campo"""
        for ent in doc.ents:
            if ent.label_ == "PER":
                print(f"Nombre detectado: {ent.text}")

        """matcher(doc) va a devolver una lista de tuplas (match_id, start, end), lo guardamos en matches
        """
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            # convertimos el id numérico de vuelta a nombre string que registramos 
            string_id = nlp.vocab.strings[match_id]
            # mantiene todos los atributos limnguísticos de los tokens que contiene
            span = doc[start:end]
            
            if string_id == "OBJ_PERDER":
                resultados["objetivo"] = "perder_grasa"
            elif string_id == "OBJ_GANAR":
                resultados["objetivo"] = "ganar_musculo"
            elif string_id == "SALUD_DETECCION":

                # Normalizamos el span a minúsculas
                resultados["salud"].append(span.text.replace(" ", "_").lower())

        # Detección de sexo por palabras clave, si algún token del doc coincide con las palabras de la lista
        # asignamos sexo femenino.
        if any(token.text.lower() in ["mujer", "chica"] for token in doc):
            resultados["sexo"] = "M"

        return resultados

    """Garantiza que los tipos de datos sean los correctos antes de pasarlos a Experta"""
    def normalizar_datos(self, datos_formulario: dict):
        """Normalización mencionada en el diagrama de arquitectura"""
        # Asegura que los tipos de datos sean correctos para el Motor de Reglas
        return {
            "nombre": str(datos_formulario.get("nombre", "Usuario")),
            "edad": int(datos_formulario.get("edad", 25)),
            "peso": float(datos_formulario.get("peso", 70.0)),
            "talla": float(datos_formulario.get("talla", 170.0)),
            "sexo": str(datos_formulario.get("sexo", "H")),
            "objetivo": str(datos_formulario.get("objetivo", "perder_grasa")),
            "salud": list(datos_formulario.get("salud", []))
        }