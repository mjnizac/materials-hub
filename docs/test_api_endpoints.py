#!/usr/bin/env python3
"""
Script de prueba para los endpoints de API REST de MaterialsDataset

Ejecutar:
    python docs/test_api_endpoints.py

Requisitos:
    - Flask server corriendo en http://localhost:5000
    - Usuario de prueba creado
    - Base de datos migrada
"""

import requests
import os
import sys
from pprint import pprint

BASE_URL = 'http://localhost:5000/api/v1'

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")


def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")


def print_section(title):
    print(f"\n{Colors.YELLOW}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")


def test_list_materials_datasets():
    """Test GET /api/v1/materials-datasets/"""
    print_section("TEST 1: Listar MaterialsDatasets")

    try:
        response = requests.get(f'{BASE_URL}/materials-datasets/')

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Total datasets: {len(data.get('items', []))}")

            if data.get('items'):
                print_info("Primer dataset:")
                pprint(data['items'][0])
            else:
                print_info("No hay datasets en la base de datos")

            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_create_materials_dataset():
    """Test POST /api/v1/materials-datasets/"""
    print_section("TEST 2: Crear MaterialsDataset")

    try:
        # Nota: Necesitas IDs válidos de user y ds_meta_data
        dataset_data = {
            "user_id": 1,  # Ajustar según tu base de datos
            "ds_meta_data_id": 1,  # Ajustar según tu base de datos
            "csv_file_path": "/test/path.csv"
        }

        response = requests.post(
            f'{BASE_URL}/materials-datasets/',
            json=dataset_data
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"Dataset creado con ID: {data.get('id')}")
            return data.get('id')
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def test_get_materials_dataset(dataset_id):
    """Test GET /api/v1/materials-datasets/{id}"""
    print_section(f"TEST 3: Obtener MaterialsDataset ID={dataset_id}")

    try:
        response = requests.get(f'{BASE_URL}/materials-datasets/{dataset_id}')

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info("Datos del dataset:")
            pprint(data)
            return True
        elif response.status_code == 404:
            print_error("Dataset no encontrado")
            return False
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_upload_csv(dataset_id, csv_path):
    """Test POST /api/v1/materials-datasets/{id}/upload"""
    print_section(f"TEST 4: Upload CSV al Dataset ID={dataset_id}")

    if not os.path.exists(csv_path):
        print_error(f"Archivo CSV no encontrado: {csv_path}")
        return False

    try:
        files = {'file': open(csv_path, 'rb')}
        response = requests.post(
            f'{BASE_URL}/materials-datasets/{dataset_id}/upload',
            files=files
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_success(f"CSV parseado exitosamente")
            print_info(f"Registros creados: {data.get('records_created')}")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            data = response.json()
            print_error(f"Error: {data.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_get_statistics(dataset_id):
    """Test GET /api/v1/materials-datasets/{id}/statistics"""
    print_section(f"TEST 5: Estadísticas del Dataset ID={dataset_id}")

    try:
        response = requests.get(f'{BASE_URL}/materials-datasets/{dataset_id}/statistics')

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Total registros: {data.get('total_records')}")
            print_info(f"Materiales únicos: {data.get('materials_count')}")
            print_info(f"Propiedades únicas: {data.get('properties_count')}")

            print_info("\nMateriales:")
            for material in data.get('unique_materials', []):
                print(f"  - {material}")

            print_info("\nPropiedades:")
            for prop in data.get('unique_properties', []):
                print(f"  - {prop}")

            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_get_records(dataset_id, page=1, per_page=10):
    """Test GET /api/v1/materials-datasets/{dataset_id}/records"""
    print_section(f"TEST 6: Listar Registros (página {page}, {per_page} por página)")

    try:
        response = requests.get(
            f'{BASE_URL}/materials-datasets/{dataset_id}/records',
            params={'page': page, 'per_page': per_page}
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Total registros: {data.get('total')}")
            print_info(f"Página: {data.get('page')}/{data.get('total_pages')}")
            print_info(f"Registros en esta página: {len(data.get('records', []))}")

            if data.get('records'):
                print_info("\nPrimer registro:")
                pprint(data['records'][0])

            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_search_records(dataset_id, search_term):
    """Test GET /api/v1/materials-datasets/{dataset_id}/records/search"""
    print_section(f"TEST 7: Buscar Registros (término: '{search_term}')")

    try:
        response = requests.get(
            f'{BASE_URL}/materials-datasets/{dataset_id}/records/search',
            params={'q': search_term}
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Status: {response.status_code}")
            print_info(f"Resultados encontrados: {data.get('total')}")
            print_info(f"Término de búsqueda: {data.get('search_term')}")

            if data.get('records'):
                print_info("\nPrimeros 3 resultados:")
                for i, record in enumerate(data['records'][:3], 1):
                    print(f"\n  {i}. {record['material_name']} ({record['chemical_formula']})")
                    print(f"     {record['property_name']}: {record['property_value']} {record['property_unit']}")

            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_delete_materials_dataset(dataset_id):
    """Test DELETE /api/v1/materials-datasets/{id}"""
    print_section(f"TEST 8: Eliminar MaterialsDataset ID={dataset_id}")

    try:
        response = requests.delete(f'{BASE_URL}/materials-datasets/{dataset_id}')

        if response.status_code in [200, 204]:
            print_success(f"Status: {response.status_code}")
            print_success("Dataset eliminado exitosamente")
            return True
        else:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False

    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Ejecuta todos los tests"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("🧪 TESTS DE API REST - MaterialsDataset")
    print(f"{'='*60}{Colors.END}\n")

    print_info(f"Base URL: {BASE_URL}")

    # Path al CSV de ejemplo
    csv_path = os.path.join(os.path.dirname(__file__), 'example_materials.csv')

    # Test 1: Listar datasets
    test_list_materials_datasets()

    # Test 2: Crear dataset
    dataset_id = test_create_materials_dataset()

    if dataset_id:
        # Test 3: Obtener dataset
        test_get_materials_dataset(dataset_id)

        # Test 4: Upload CSV (si existe el archivo)
        if os.path.exists(csv_path):
            if test_upload_csv(dataset_id, csv_path):
                # Test 5: Estadísticas
                test_get_statistics(dataset_id)

                # Test 6: Listar registros
                test_get_records(dataset_id, page=1, per_page=10)

                # Test 7: Buscar registros
                test_search_records(dataset_id, 'Al2O3')
        else:
            print_info(f"CSV de ejemplo no encontrado en: {csv_path}")
            print_info("Saltando tests 4-7")

        # Test 8: Eliminar dataset (opcional - comentar si quieres mantener el dataset)
        # test_delete_materials_dataset(dataset_id)

    print(f"\n{Colors.GREEN}{'='*60}")
    print("✓ TESTS COMPLETADOS")
    print(f"{'='*60}{Colors.END}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrumpidos por el usuario{Colors.END}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error fatal: {str(e)}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
