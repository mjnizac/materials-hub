#!/usr/bin/env python3
"""
Script de prueba para el MaterialsDatasetService CSV Parser

Ejecutar desde la raíz del proyecto:
    python docs/test_csv_parser.py
"""

import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def test_csv_validation():
    """Prueba la validación de columnas del CSV"""
    print("\n" + "="*60)
    print("TEST 1: Validación de Columnas CSV")
    print("="*60)

    from app.modules.dataset.services import MaterialsDatasetService

    service = MaterialsDatasetService()

    # Test con columnas válidas
    print("\n✓ Test con columnas VÁLIDAS:")
    valid_columns = ['material_name', 'property_name', 'property_value', 'temperature', 'chemical_formula']
    result = service.validate_csv_columns(valid_columns)
    print(f"   Válido: {result['valid']}")
    print(f"   Mensaje: {result['message']}")

    # Test con columnas faltantes
    print("\n✗ Test con columnas FALTANTES:")
    invalid_columns = ['material_name', 'temperature']  # Falta property_name y property_value
    result = service.validate_csv_columns(invalid_columns)
    print(f"   Válido: {result['valid']}")
    print(f"   Columnas faltantes: {result['missing_required']}")
    print(f"   Mensaje: {result['message']}")

    # Test con columnas extra
    print("\n⚠ Test con columnas EXTRA (desconocidas):")
    extra_columns = ['material_name', 'property_name', 'property_value', 'unknown_field', 'another_unknown']
    result = service.validate_csv_columns(extra_columns)
    print(f"   Válido: {result['valid']}")
    print(f"   Columnas extra: {result['extra_columns']}")
    print(f"   Mensaje: {result['message']}")


def test_csv_parsing():
    """Prueba el parsing del archivo CSV de ejemplo"""
    print("\n" + "="*60)
    print("TEST 2: Parsing del CSV")
    print("="*60)

    from app.modules.dataset.services import MaterialsDatasetService

    service = MaterialsDatasetService()
    csv_path = os.path.join(os.path.dirname(__file__), 'example_materials.csv')

    if not os.path.exists(csv_path):
        print(f"\n✗ Error: No se encontró el archivo {csv_path}")
        return

    print(f"\n📄 Parseando archivo: {csv_path}")

    result = service.parse_csv_file(csv_path)

    if result['success']:
        print(f"\n✓ Parsing exitoso!")
        print(f"   Filas parseadas: {result['rows_parsed']}")
        print(f"   Validación: {result['validation']['message']}")

        # Mostrar algunas filas de ejemplo
        print(f"\n📊 Primeros 3 registros parseados:")
        for i, row in enumerate(result['data'][:3], 1):
            print(f"\n   Registro {i}:")
            print(f"      Material: {row['material_name']}")
            print(f"      Fórmula: {row['chemical_formula']}")
            print(f"      Propiedad: {row['property_name']} = {row['property_value']} {row.get('property_unit', '')}")
            print(f"      Temperatura: {row['temperature']} K" if row['temperature'] else "      Temperatura: N/A")
            print(f"      Fuente: {row['data_source'].name if row['data_source'] else 'N/A'}")

        # Estadísticas
        materials = set(row['material_name'] for row in result['data'])
        properties = set(row['property_name'] for row in result['data'])

        print(f"\n📈 Estadísticas:")
        print(f"   Materiales únicos: {len(materials)}")
        print(f"   Lista: {', '.join(sorted(materials))}")
        print(f"\n   Propiedades únicas: {len(properties)}")
        print(f"   Lista: {', '.join(sorted(properties))}")

    else:
        print(f"\n✗ Error en parsing:")
        print(f"   {result['error']}")


def test_data_type_conversion():
    """Prueba la conversión de tipos de datos"""
    print("\n" + "="*60)
    print("TEST 3: Conversión de Tipos de Datos")
    print("="*60)

    from app.modules.dataset.services import MaterialsDatasetService
    from app.modules.dataset.models import DataSource

    service = MaterialsDatasetService()

    # Simular una fila del CSV
    test_row = {
        'material_name': 'Al2O3',
        'chemical_formula': 'Al2O3',
        'property_name': 'density',
        'property_value': '3.95',
        'property_unit': 'g/cm3',
        'temperature': '298',
        'pressure': '101325',
        'data_source': 'EXPERIMENTAL',
        'uncertainty': '5',
        'description': 'Test material'
    }

    print("\n📝 Fila CSV de entrada:")
    for key, value in test_row.items():
        print(f"   {key}: {value!r} (type: {type(value).__name__})")

    parsed = service._parse_csv_row(test_row, row_num=2)

    print("\n✓ Datos parseados:")
    for key, value in parsed.items():
        type_name = type(value).__name__ if value is not None else 'None'
        if isinstance(value, DataSource):
            print(f"   {key}: {value.name} (type: DataSource enum)")
        else:
            print(f"   {key}: {value!r} (type: {type_name})")


def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🧪 TESTS DEL CSV PARSER - MaterialsDataset")
    print("="*60)

    try:
        test_csv_validation()
        test_csv_parsing()
        test_data_type_conversion()

        print("\n" + "="*60)
        print("✓ TODOS LOS TESTS COMPLETADOS")
        print("="*60 + "\n")

    except ImportError as e:
        print(f"\n✗ Error de importación: {e}")
        print("Asegúrate de ejecutar este script desde el contexto de Flask:")
        print("   flask shell < docs/test_csv_parser.py")
    except Exception as e:
        print(f"\n✗ Error inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
