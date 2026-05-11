
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


# Creamos el motor de inferencia 
class MotorFitness(KnowledgeEngine):

    # Regla 1: calculamos la tasa metabólica Basal, con la fórmula de Mifflin-St Jeor
    # TMB = (10xP) + (6,25xh) - (5xe) + s(5=H,-161=M)
    @Rule(Usuario(peso=MATCH.p, talla=MATCH.t, edad=MATCH.e, sexo=MATCH.s))
    def calcular_tmb(self, p, t, e, s):
        # aplicamos la fórmula matemática según el sexo del usuario
        tmb = (10 * p) + (6.25 * t) - (5 * e) + (5 if s == "H" else -161)
        # declaramos un nuevo hecho interno con el resultado de la tasa
        self.declare(Fact(tmb_base=tmb))


    # Regla 2: lógica para la pérdida de grasa
    @Rule(Fact(tmb_base=MATCH.tmb), Usuario(objetivo="perder_grasa"))
    def objetivo_deficit(self, tmb):
        # calculamos el 85% de la tasa, ya que si la tasa que nos ha dado es el 100%, con un 85 estaríamos perdiendo bastante porcentaje de la tasa.
        self.declare(PlanGenerado(tipo="calorias", valor=int(tmb * 0.85)))
        self.declare(Fact(tipo_dieta="definicion"))

    # Regla 3: lógica para la ganancia Muscular 
    @Rule(Fact(tmb_base=MATCH.tmb), Usuario(objetivo="ganar_musculo"))
    def objetivo_superavit(self, tmb):
        # calculamos ahora el 115% de la tasa con un aumento calórico del 15%
        self.declare(PlanGenerado(tipo="calorias", valor=int(tmb * 1.15)))
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