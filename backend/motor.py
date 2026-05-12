
# Parche por imcompatibilidad (Importante para Python 3.10+), experta fue diseñado para versiones antiguas de Python
# Este bloque corrige la ruta de Mapping para que funcione para python 10 o superior.
import collections
if not hasattr(collections, 'Mapping'):
    import collections.abc
    collections.Mapping = collections.abc.Mapping

from experta import *
import math


# Definimos los hechos, que son las unidades de información que el motor procesa
class Usuario(Fact):
    """Información capturada en el Módulo 1"""
    # nombre, edad, peso, talla, sexo, objetivo, actividad, salud, presupuesto
    pass

class PlanGenerado(Fact):
    """Resultados que el motor irá deduciendo"""
    # tipo (calorias, macro, ejercicio, aviso), valor
    pass

FACTORES_ACTIVIDAD = {
    "sedentario": 1.2,
    "ligero":     1.375,
    "moderado":   1.55,
    "activo":     1.725,
    "muy_activo": 1.9
    }

# Creamos el motor de inferencia 
class MotorFitness(KnowledgeEngine):

    # Regla 1: calculamos la tasa metabólica Basal, con la fórmula de Mifflin-St Jeor
    # TMB = (10xP) + (6,25xh) - (5xe) + s(5=H,-161=M)
    @Rule(Usuario(peso=MATCH.p, talla=MATCH.t, edad=MATCH.e, sexo=MATCH.s, actividad=MATCH.a))
    def calcular_tmb(self, p, t, e, s, a):
        tmb = (10 * p) + (6.25 * t) - (5 * e) + (5 if s == "H" else -161)
        factor = FACTORES_ACTIVIDAD.get(a, 1.2)
        tdee = tmb * factor  # ahora usamos el TDEE real
        self.declare(Fact(tdee_calculado=tdee))

    # Regla 2: lógica para la pérdida de grasa
    @Rule(Fact(tdee_calculado=MATCH.tdee), Usuario(objetivo="perder_grasa"))
    def objetivo_deficit(self, tdee):
        # calculamos el 95% de la tasa, ya que si la tasa que nos ha dado es el 100%, con un 95 estaríamos perdiendo bastante porcentaje de la tasa.
        self.declare(PlanGenerado(tipo="calorias", valor=int(tdee * 0.90)))
        self.declare(Fact(tipo_dieta="definicion"))

    # Regla 3: lógica para la ganancia Muscular 
    @Rule(Fact(tdee_calculado=MATCH.tdee), Usuario(objetivo="ganar_musculo"))
    def objetivo_superavit(self, tdee):
        # calculamos ahora el 110% de la tasa con un aumento calórico del 10%
        self.declare(PlanGenerado(tipo="calorias", valor=int(tdee * 1.10)))
        self.declare(Fact(tipo_dieta="volumen"))

    # Regla 4: generación del menú semanal, y adaptación por salud
    @Rule(Fact(tipo_dieta=MATCH.td), Usuario(salud=MATCH.s))
    def generar_dieta_semanal(self, td, s):
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        # Mini base de datos en un diccionario donde vamos a definir dietas bastantes generales según el tipo de dieta
        menus = {
            "definicion": {
                "Lunes": ("Claras con pavo", "Pollo y espárragos", "Pescado blanco"),
                "Martes": ("Yogur desnatado", "Ensalada de atún", "Tortilla francesa"),
                "Miércoles": ("Kiwi y avena", "Pavo a la plancha", "Verduras al vapor"),
                "Jueves": ("Tostada integral", "Merluza al horno", "Pechuga de pollo"),
                "Viernes": ("Tortilla de claras", "Ternera magra", "Sepia a la plancha"),
                "Sábado": ("Batido proteico", "Wok de tofu", "Ensalada mixta"),
                "Domingo": ("Fruta variada", "Conejo al ajillo", "Sopa de verduras")
            },
            "volumen": {
                "Lunes": ("Avena y plátano", "Pasta boloñesa", "Salmón con patata"),
                "Martes": ("Tortilla y aguacate", "Arroz con pollo", "Filete de ternera"),
                "Miércoles": ("Sándwich de atún", "Lentejas con arroz", "Huevos revueltos"),
                "Jueves": ("Gachas de avena", "Guiso de patatas", "Pechuga y quinoa"),
                "Viernes": ("Tortitas de arroz", "Hamburguesa casera", "Pasta integral"),
                "Sábado": ("Yogur griego y nueces", "Arroz con ternera", "Pizza fitness"),
                "Domingo": ("Omelette de jamón", "Paella de pollo", "Salmón y espárragos")
            }
        }

        dieta_dict = {}
        for dia in dias:
            # Desempaquetamos la tupla de 3 elementos en tres variables 
            d, c, cen = menus[td][dia]

            # si detectamos intoleracia, cambiamos el ingrediente
            if "intolerante_lactosa" in s:
                d = d.replace("Yogur", "Yogur de soja")
            dieta_dict[dia] = {"desayuno": d, "comida": c, "cena": cen}

        self.declare(PlanGenerado(tipo="dieta_semanal", valor=dieta_dict))

    # Regla 5: recomendación de ejericios según la salud
    @Rule(Usuario(salud=MATCH.s))
    def alertas_salud(self, s):
        msg = "Priorizar natación o bicicleta. Evitar saltos." if "lesion_rodilla" in s else "Entrenamiento de fuerza combinado con cardio."
        self.declare(PlanGenerado(tipo="ejercicio", valor=msg))