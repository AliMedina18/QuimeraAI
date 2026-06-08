"""
Test SPIKE 1: Validar que few-shot examples mejoran la paleta de colores.

Script simple que:
1. Lee un brief simple
2. Llama a analyze_and_design (Step 1) 
3. Extrae y muestra los colores generados
4. Valida que hay ≥5 colores (NO solo 2-3)
"""

import asyncio
import sys
import os
import re

# Agregar backend a path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.models import DesignContext
from backend.pipeline.step1_analyze import analyze_and_design


async def test_color_palette_generation():
    """Test: Verificar que Gemini genera paleta de 5+ colores."""
    
    brief = "Landing page para app de fitness con enfoque en wellness y energía. Público: 25-45 años activos. Debe transmitir confianza, energía, modernidad. Incluir dashboard para tracking de ejercicio."
    
    print("=" * 80)
    print("🧪 TEST SPIKE 1: Few-Shot Examples para Mejora de Paleta")
    print("=" * 80)
    print(f"\n📝 Brief: {brief}\n")
    
    context = DesignContext(
        design_brief=brief,
        project_type="landing_page"
    )
    
    print("🎨 Generando DESIGN.md con ejemplos reales...")
    
    try:
        result = await analyze_and_design(context)
        
        if not result.design_markdown:
            print("❌ ERROR: No se generó DESIGN.md")
            return False
        
        # Extraer colores del YAML
        colors_section = result.design_markdown.split("colors:")[1].split("typography:")[0]
        colors = re.findall(r'(\w+):\s*"(#[0-9a-f]{6})"', colors_section)
        
        print(f"\n✅ DESIGN.md Generado!")
        print(f"   Tamaño: {len(result.design_markdown)} caracteres\n")
        
        print("🎨 PALETA DE COLORES EXTRAÍDA:")
        print("-" * 40)
        for color_name, color_hex in colors:
            print(f"  {color_name:<25} {color_hex}")
        
        print(f"\n📊 RESUMEN:")
        print(f"   Total de colores: {len(colors)}")
        
        if len(colors) >= 5:
            print("   ✅ EXCELENTE: Paleta con 5+ colores (como empresas premium)")
        elif len(colors) >= 3:
            print("   ⚠️  ACEPTABLE: Paleta con 3-4 colores (mejorar)")
        else:
            print(f"   ❌ POBRE: Solo {len(colors)} colores (debería ser ≥5)")
        
        # Extraer tipografía
        typo_section = result.design_markdown.split("typography:")[1].split("rounded:")[0]
        typo_levels = re.findall(r'(\w+):', typo_section)
        typo_levels = [t for t in typo_levels if t not in ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing']]
        
        print(f"\n📝 NIVELES TIPOGRÁFICOS: {len(typo_levels)}")
        print(f"   Niveles: {', '.join(typo_levels[:6])}{' ...' if len(typo_levels) > 6 else ''}")
        
        if len(typo_levels) >= 6:
            print("   ✅ EXCELENTE: 6+ niveles semánticos")
        elif len(typo_levels) >= 4:
            print("   ⚠️  ACEPTABLE: 4-5 niveles (mejorar)")
        else:
            print(f"   ❌ POBRE: Solo {len(typo_levels)} niveles")
        
        # Mostrar descripción
        description = result.design_markdown.split("description:")[1].split("\n")[0][:100]
        print(f"\n📖 DESCRIPCIÓN (primeros 100 chars):")
        print(f"   {description}...")
        
        print("\n" + "=" * 80)
        
        # Validación
        success = len(colors) >= 5 and len(typo_levels) >= 6
        
        if success:
            print("✅ TEST PASÓ: Paleta profesional generada")
        else:
            print("⚠️  TEST PARCIAL: Mejora visible pero revisar más")
        
        print("=" * 80)
        
        # Mostrar primeras líneas del DESIGN.md
        print("\n📄 PRIMERAS LÍNEAS DEL DESIGN.md:\n")
        print(result.design_markdown[:500] + "...\n")
        
        return success
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_color_palette_generation())
    sys.exit(0 if success else 1)
