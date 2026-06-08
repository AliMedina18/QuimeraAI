import asyncio
import sys
sys.path.insert(0, 'backend')

from backend.models import DesignContext
from backend.pipeline.step1_analyze import analyze_and_design
from backend.pipeline.step3_generate import generate_code

async def test_pipeline():
    brief = """Sakura Sushi - Restaurante premium de sushi en Madrid.
Necesito un sitio web que muestre:
- Presentacion del restaurante
- Menu de especialidades
- Galeria de platos
- Reservas
- Ubicacion y contacto
- Ambiente elegante y moderno"""
    
    context = DesignContext(
        design_brief=brief,
        project_type="restaurant",
        design_reference="stripe",
        design_markdown="",
        html_output=""
    )
    
    print("=" * 60)
    print("PASO 1: Generando DESIGN.md con template Stripe")
    print("=" * 60)
    context = await analyze_and_design(context)
    print("OK - DESIGN.md generado ({} caracteres)".format(len(context.design_markdown)))
    print("\nPrimeros 400 caracteres:\n{}\n".format(context.design_markdown[:400]))
    
    print("=" * 60)
    print("PASO 3: Generando HTML desde los tokens")
    print("=" * 60)
    context = await generate_code(context)
    print("OK - HTML generado ({} caracteres)\n".format(len(context.html_output)))
    
    # Verificaciones
    checks = [
        ("<!DOCTYPE html>" in context.html_output, "Tiene DOCTYPE correcto"),
        ("</html>" in context.html_output, "Tiene cierre HTML correcto"),
        ("<style>" in context.html_output, "Tiene CSS inline"),
        ("Paleta de Colores" not in context.html_output, "NO muestra 'Paleta de Colores'"),
        ("Tipografia" not in context.html_output, "NO muestra 'Tipografia'"),
        ("Componentes" not in context.html_output, "NO muestra 'Componentes'"),
        ("<nav>" in context.html_output or "<header>" in context.html_output, "Tiene navbar/header"),
        ("<footer>" in context.html_output, "Tiene footer"),
    ]
    
    print("\n" + "=" * 60)
    print("VERIFICACION DEL HTML GENERADO")
    print("=" * 60)
    for passed, desc in checks:
        status = "OK" if passed else "ERROR"
        print("{} - {}".format(status, desc))
    
    print("\n" + "-" * 60)
    print("Primeros 1000 caracteres del HTML:")
    print("-" * 60)
    print(context.html_output[:1000])

asyncio.run(test_pipeline())
