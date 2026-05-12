
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

class EstadoDieta(Fact):
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
        cal = int(tdee * 0.90)
        self.declare(PlanGenerado(tipo="calorias", valor=cal))
        self.declare(Fact(tipo_dieta="definicion", cal=cal))

    # Regla 3: lógica para la ganancia Muscular 
    @Rule(Fact(tdee_calculado=MATCH.tdee), Usuario(objetivo="ganar_musculo"))
    def objetivo_superavit(self, tdee):
        cal = int(tdee * 1.10)
        self.declare(PlanGenerado(tipo="calorias", valor=cal))
        self.declare(Fact(tipo_dieta="volumen", cal=cal))

    @Rule(Fact(tipo_dieta=MATCH.td, cal=MATCH.cal))
    def generar_dieta_dinamica(self, td, cal):
        if td == "volumen":
            p_prot, p_fat, p_carb = 0.25, 0.25, 0.50 
        else:
            p_prot, p_fat, p_carb = 0.40, 0.25, 0.35

        g_prot = int((cal * p_prot) / 4)
        g_fat = int((cal * p_fat) / 9)
        g_carb = int((cal * p_carb) / 4)

        resumen_macros = {
            "proteinas": f"{g_prot}g",
            "grasas": f"{g_fat}g",
            "carbohidratos": f"{g_carb}g",
            "total_kcal": cal
        }

        guia_alimentos = self.obtener_alimentos_por_macros(td)

        self.declare(PlanGenerado(tipo="macros", valor=resumen_macros))
        self.declare(PlanGenerado(tipo="guia_alimentaria", valor=guia_alimentos))

    def obtener_alimentos_por_macros(self, tipo):
        if tipo == "volumen":
            return "Prioriza: Arroz, pasta, legumbres, pollo y huevos enteros."
        return "Prioriza: Pescado blanco, claras de huevo, verduras verdes y pavo."

    # Regla 5: recomendación de ejericios según la salud
    @Rule(Usuario(salud=MATCH.s))
    def alertas_salud(self, s):
        msg = "Priorizar natación o bicicleta. Evitar saltos." if "lesion_rodilla" in s else "Entrenamiento de fuerza combinado con cardio."
        self.declare(PlanGenerado(tipo="ejercicio", valor=msg))