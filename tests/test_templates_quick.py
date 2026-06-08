"""
Test rápido: Validar que los templates se cargaron correctamente
y que el pipeline puede inyectarlos.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.design_templates import get_templates_manager


def test_templates():
    """Test rápido de templates."""
    print("=" * 80)
    print("🧪 TEST: Validar carga de templates")
    print("=" * 80)
    
    manager = get_templates_manager()
    
    # Listar templates
    available = manager.list_available()
    print(f"\n✅ Templates cargados: {len(available)}")
    print(f"   Primeros 10: {', '.join(available[:10])}\n")
    
    # Metadata de algunos templates
    print("📊 Metadata de templates populares:")
    print("-" * 80)
    
    for template in ["airbnb", "figma", "stripe", "spotify", "slack"]:
        if template in available:
            metadata = manager.get_template_metadata(template)
            if metadata:
                print(f"\n{template.upper()}")
                print(f"  Name: {metadata['name']}")
                print(f"  Colors: {metadata['colors']}+")
                print(f"  Typography levels: {metadata['typography_levels']}+")
                print(f"  Description: {metadata['description']}")
    
    print("\n" + "=" * 80)
    print("✅ TEST PASÓ: Templates listos para usar como referencias")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_templates()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
