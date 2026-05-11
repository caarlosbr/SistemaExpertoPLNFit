from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

# Importamos tus módulos
from .pln import ModuloPLN
from .motor import MotorFitness, Usuario, PlanGenerado

app = FastAPI(title="API Fitness Experto")

# Configuración de CORS: Permite que tu index.html se comunique con el servidor
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instanciamos el módulo PLN que creamos antes
pln_processor = ModuloPLN()

# Definimos qué datos esperamos recibir del Frontend
class SolicitudPlan(BaseModel):
    nombre: str
    edad: int
    peso: float
    talla: float
    sexo: str
    objetivo: str
    salud: List[str]
    texto_libre: Optional[str] = None # Por si usas el "Modo Conversacional"

@app.post("/generar-plan")
async def api_generar_plan(datos: SolicitudPlan):
    """
    Recibe los datos del usuario, los procesa mediante PLN, 
    ejecuta el motor de reglas experto y devuelve un plan de fitness personalizado.
    """
    try:
        # 1. PASO PLN: Si hay texto libre, extraemos datos. Si no, normalizamos los del form.
        if datos.texto_libre:
            datos_finales = pln_processor.extraer_datos(datos.texto_libre)
            datos_finales["nombre"] = datos.nombre # Mantenemos el nombre del form
        else:
            # Usamos la función de normalización que definimos en pln.py
            datos_finales = pln_processor.normalizar_datos(datos.dict())

        # 2. PASO MOTOR EXPERTO: Alimentamos el motor de tu archivo .ipynb
        engine = MotorFitness()
        engine.reset()
        
        # Declaramos el hecho Usuario con los datos limpios
        engine.declare(Usuario(
            nombre=datos_finales["nombre"],
            sexo=datos_finales["sexo"],
            edad=datos_finales["edad"],
            peso=datos_finales["peso"],
            talla=datos_finales["talla"],
            objetivo=datos_finales["objetivo"],
            salud=datos_finales["salud"]
        ))
        
        engine.run()

        # 3. RECOGIDA DE RESULTADOS: Filtramos los hechos tipo PlanGenerado
        plan_dict = {}
        for fact in engine.facts.values():
            if isinstance(fact, PlanGenerado):
                plan_dict[fact['tipo']] = fact['valor']

        return {
            "status": "success",
            "plan": plan_dict,
            "datos_procesados": datos_finales
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)