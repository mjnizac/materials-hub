import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.environment.host import get_host_for_selenium_testing
from core.selenium.common import close_driver, initialize_driver

# ==============================
# HELPERS GENERALES
# ==============================


def wait_for_page_to_load(driver, timeout: int = 15):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )


def login(driver, host: str, email: str = "user1@example.com", password: str = "1234"):
    """
    Hace login en /login y verifica que no nos quedamos en la página de login.
    """
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)

    # Esperar al formulario
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    password_field = driver.find_element(By.NAME, "password")

    email_field.clear()
    email_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)

    # Intentar hacer click en botón submit
    try:
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            )
        )
        submit_button.click()
    except TimeoutException:
        # Fallback: ENTER en el campo de contraseña
        password_field.send_keys(Keys.RETURN)

    wait_for_page_to_load(driver)

    current_url = driver.current_url
    assert "/login" not in current_url, (
        f"El login no ha funcionado, seguimos en /login. URL actual: {current_url}"
    )


def create_materials_dataset_and_go_to_csv_upload(
    driver,
    host: str,
    title_suffix: str = ""
):
    """
    Crea un MaterialsDataset desde /dataset/upload.

    Flujo:

    1. Ir a /dataset/upload
    2. Rellenar título, descripción y tags mínimos
    3. Aceptar el checkbox "agree"
    4. Pulsar "Create Materials Dataset"
    5. Esperar a /materials/<id>/upload y devolver (dataset_id, dataset_title)
    """
    driver.get(f"{host}/dataset/upload")
    wait_for_page_to_load(driver)

    dataset_title = f"Selenium Materials Dataset {title_suffix}".strip()

    try:
        title_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "title"))
        )
    except TimeoutException:
        html_path = "/tmp/selenium_dataset_upload_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            f"No se encontró el input name='title' en /dataset/upload. "
            f"HTML guardado en {html_path}"
        )

    desc_input = driver.find_element(By.NAME, "desc")
    tags_input = driver.find_element(By.NAME, "tags")

    title_input.clear()
    title_input.send_keys(dataset_title)
    desc_input.clear()
    desc_input.send_keys("Dataset de materiales creado automáticamente con Selenium.")
    tags_input.clear()
    tags_input.send_keys("selenium,materials,test")

    # Aceptar condiciones
    agree_checkbox = driver.find_element(By.ID, "agreeCheckbox")
    agree_checkbox.click()

    # Crear dataset
    upload_button = driver.find_element(By.ID, "upload_button")
    upload_button.click()

    # Esperar a que aparezca el input de CSV en /materials/<id>/upload
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "csvFile"))
        )
    except TimeoutException:
        html_path = "/tmp/selenium_csv_upload_page_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se ha llegado a la página de subida de CSV "
            f"(/materials/<id>/upload). HTML guardado en {html_path}"
        )

    wait_for_page_to_load(driver)

    # URL esperada: .../materials/<id>/upload
    current_url = driver.current_url.rstrip("/")
    parts = current_url.split("/")
    if "materials" not in parts:
        raise AssertionError(f"URL inesperada tras crear el dataset: {current_url}")

    idx = parts.index("materials")
    dataset_id = parts[idx + 1]

    return dataset_id, dataset_title


def upload_csv_for_dataset(driver):
    """
    Sube el CSV de ejemplo en la pantalla /materials/<id>/upload.
    """
    # Ruta al CSV de ejemplo (carpeta 'examples' en la raíz del proyecto)
    csv_path = os.path.abspath("examples/materials_example.csv")
    if not os.path.exists(csv_path):
        raise AssertionError(
            f"No se encontró el CSV de ejemplo en: {csv_path}. "
            "Asegúrate de que existe 'examples/materials_example.csv'."
        )

    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "csvFile"))
    )
    file_input.send_keys(csv_path)

    upload_button = driver.find_element(By.ID, "uploadBtn")
    upload_button.click()

    # Esperar a que aparezca el mensaje de éxito
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#uploadResult .alert-success")
            )
        )
    except TimeoutException:
        html_path = "/tmp/selenium_csv_upload_result_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se ha mostrado el mensaje de éxito tras subir el CSV. "
            f"HTML guardado en {html_path}"
        )


def go_to_view_dataset_from_upload_result(driver, dataset_id: str):
    """
    Desde la pantalla /materials/<id>/upload (tras subir CSV),
    pulsa el botón "View Dataset" para ir a /materials/<id>.
    """
    try:
        view_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(., 'View Dataset')]")
            )
        )
    except TimeoutException:
        html_path = "/tmp/selenium_view_dataset_button_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se encontró el botón/enlace 'View Dataset' tras subir el CSV. "
            f"HTML guardado en {html_path}"
        )

    view_button.click()
    wait_for_page_to_load(driver)

    current_url = driver.current_url
    assert f"/materials/{dataset_id}" in current_url, (
        f"No estamos en la vista del dataset tras pulsar 'View Dataset'. "
        f"URL actual: {current_url}"
    )


# ==============================
# TESTS
# ==============================

def test_login_success():
    """
    Test simple: comprobar que el login con user1@example.com / 1234 funciona.
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)
        # Si no lanza excepción, consideramos el login correcto.
        assert "/login" not in driver.current_url
    finally:
        close_driver(driver)


def test_create_materials_dataset_upload_csv_and_view():
    """
    Flujo E2E principal:

    1. Login
    2. Crear Materials Dataset (metadatos)
    3. Subir CSV de ejemplo
    4. Ver el dataset (/materials/<id>)
    5. Comprobar que hay registros de materiales
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y llegar a /materials/<id>/upload
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="E2E"
        )

        # 3) Subir CSV
        upload_csv_for_dataset(driver)

        # 4) Ir a "View Dataset"
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # 5) Comprobar que hay registros en la vista del dataset
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(@class, 'material-record-item') "
                    "or contains(text(), 'No material records')]",
                )
            )
        )

        material_items = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        assert len(material_items) > 0, (
            "No se han creado registros de materiales a partir del CSV"
        )

    finally:
        close_driver(driver)


def test_dataset_appears_in_my_materials():
    """
    Flujo:

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /dataset/list (My Materials Datasets)
    4. Comprobar que aparece el dataset en la tabla
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="Listed"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la lista de datasets del usuario
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # 4) Buscar nuestro dataset en la tabla
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

        assert rows, "No hay filas en la tabla de My Materials Datasets"

        found = any(dataset_title in row.text for row in rows)
        assert found, f"No se ha encontrado el dataset '{dataset_title}' en la lista"

    finally:
        close_driver(driver)


def test_material_search_filter_works_with_example_csv():
    """
    Flujo extra (sidebar search):

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>
    4. Usar el cuadro de búsqueda lateral por nombre de material
       (usando el nombre de un material real del dataset)
    5. Comprobar que se filtran los registros mostrados
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="Search"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la vista del dataset
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Esperar a que haya al menos un registro de material
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".material-record-item"))
        )
        items = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        assert items, "No hay registros de materiales tras subir el CSV"

        # Tomamos el nombre del PRIMER material real como término de búsqueda
        first_name = (items[0].get_attribute("data-material-name") or "").strip()
        assert first_name, "El primer registro no tiene atributo data-material-name"

        # Usamos una parte del nombre (por si es largo)
        search_term = first_name[:5] if len(first_name) >= 5 else first_name

        # 4) Localizar input de búsqueda por ID
        try:
            search_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "materialSearchInput"))
            )
        except TimeoutException:
            html_path = "/tmp/selenium_material_search_input_error.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise AssertionError(
                "No se encontró el input con id='materialSearchInput' en la vista "
                f"del dataset. HTML guardado en {html_path}"
            )

        # 5) Escribir el término de búsqueda y dejar tiempo a JS para filtrar
        search_input.clear()
        search_input.send_keys(search_term)
        time.sleep(1)  # pequeño margen para que JS filtre

        # 6) Comprobar que hay elementos visibles y que coinciden con el término
        filtered_items = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        visible_items = []
        for item in filtered_items:
            style = item.get_attribute("style") or ""
            if "display: none" not in style:
                visible_items.append(item)

        assert visible_items, (
            f"El filtro no ha dejado visible ningún material al buscar '{search_term}'"
        )

        for item in visible_items:
            material_name = (item.get_attribute("data-material-name") or "").lower()
            assert search_term.lower() in material_name, (
                f"Se muestra un material que no coincide con el término de búsqueda "
                f"'{search_term}': '{material_name}'"
            )

    finally:
        close_driver(driver)


def test_csv_modal_displays_csv_contents():
    """
    Flujo extra (modal CSV):

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>
    4. Pulsar botón 'View' del CSV
    5. Comprobar que el modal muestra una tabla con cabeceras y filas
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="CSVModal"
        )
        upload_csv_for_dataset(driver)
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Pulsar el botón "View" del CSV (con onclick="viewCSV()")
        view_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@onclick, 'viewCSV')]")
            )
        )
        view_button.click()

        # Esperar a que se cargue la tabla dentro del modal
        headers_row = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "csvHeaders"))
        )
        body_tbody = driver.find_element(By.ID, "csvBody")

        headers = headers_row.find_elements(By.TAG_NAME, "th")
        rows = body_tbody.find_elements(By.TAG_NAME, "tr")

        assert len(headers) > 0, "La tabla CSV no tiene cabeceras"
        assert len(rows) > 0, "La tabla CSV no tiene filas de datos"

    finally:
        close_driver(driver)


def test_materials_statistics_page_loads():
    """
    Flujo: página de estadísticas de un Materials Dataset.

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>/statistics
    4. Comprobar que la página carga, no redirige a /login
       y muestra información del dataset.
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix=" Stats"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la página de estadísticas
        stats_url = f"{host}/materials/{dataset_id}/statistics"
        driver.get(stats_url)
        wait_for_page_to_load(driver)

        current_url = driver.current_url

        # 4.a) Asegurarnos de que no nos ha mandado a /login
        assert "/login" not in current_url, (
            "La página de estadísticas ha redirigido a /login. "
            f"URL actual: {current_url}"
        )

        # 4.b) Asegurarnos de que estamos en la URL correcta
        assert f"/materials/{dataset_id}/statistics" in current_url, (
            "No estamos en la URL de estadísticas esperada.\n"
            f"Esperada: /materials/{dataset_id}/statistics\n"
            f"Actual:   {current_url}"
        )

        # 4.c) Comprobar que aparece el título del dataset o texto de estadísticas
        body_text = driver.find_element(By.TAG_NAME, "body").text

        base_title = dataset_title.replace("Stats", "").strip()

        assert (
            dataset_title in body_text
            or base_title in body_text
            or "Statistics" in body_text
        ), (
            "La página de estadísticas no parece mostrar información del dataset.\n"
            f"Buscábamos algo como '{dataset_title}' o 'Statistics' y no aparece."
        )

    finally:
        close_driver(driver)


def test_edit_material_record_updates_value_in_view():
    """
    Flujo: edición de un MaterialRecord.

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>
    4. Editar el primer registro de material
    5. Cambiar el valor de la propiedad (property_value)
    6. Guardar y comprobar que en la vista del dataset aparece el nuevo valor
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix=" Edit"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la vista del dataset
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Esperar a que haya al menos un registro
        records = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".material-record-item")
            )
        )
        assert records, "No hay registros de materiales tras subir el CSV"

        first_record = records[0]
        material_name = (first_record.get_attribute("data-material-name") or "").strip()
        assert material_name, "El primer registro no tiene data-material-name"

        # 4) Localizar y pulsar el botón de editar de ese registro
        edit_link = first_record.find_element(
            By.XPATH,
            ".//a[contains(@href, '/materials/') and contains(@href, '/edit')]",
        )
        edit_link.click()
        wait_for_page_to_load(driver)

        # 5) Estamos en el formulario de edición: cambiar property_value (y opcionalmente descripción)
        new_value = "9999.0"

        property_value_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "property_value"))
        )
        property_value_input.clear()
        property_value_input.send_keys(new_value)

        # Opcional: cambiar descripción para ver luego el cambio
        try:
            description_input = driver.find_element(By.NAME, "description")
            description_input.clear()
            description_input.send_keys("Editado con Selenium")
        except Exception:
            # Si por lo que sea el campo no existe, no rompemos el test
            pass

        # 6) Guardar el formulario (botón type='submit')
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@type='submit' and "
                        "(contains(., 'Save') or contains(., 'Guardar') or contains(., 'Save Record'))]"
                    )
                )
            )
            submit_button.click()
        except TimeoutException:
            # Fallback genérico: primer botón type=submit que encontremos
            submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()

        wait_for_page_to_load(driver)

        # Después de guardar, la vista debería redirigir a /materials/<id>
        current_url = driver.current_url
        assert f"/materials/{dataset_id}" in current_url, (
            "Tras guardar el registro editado no hemos vuelto a la vista del dataset.\n"
            f"URL actual: {current_url}"
        )

        # 7) Comprobar que el registro con ese material_name muestra el nuevo valor
        updated_records = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".material-record-item")
            )
        )

        # Filtramos por el mismo material_name
        same_material_items = [
            el for el in updated_records
            if (el.get_attribute("data-material-name") or "").strip() == material_name
        ]
        assert same_material_items, (
            f"No se encontró ningún registro con material_name='{material_name}' "
            "después de la edición."
        )

        # Al menos uno debe contener el nuevo valor en su texto
        found_new_value = any(new_value in el.text for el in same_material_items)
        assert found_new_value, (
            f"Ningún registro para el material '{material_name}' muestra el nuevo "
            f"valor '{new_value}' tras la edición."
        )

    finally:
        close_driver(driver)


def test_delete_material_record_removes_it_from_view():
    """
    Flujo: borrado de un MaterialRecord.

    1. Login
    2. Crear Materials Dataset + subir CSV
    3. Ir a /materials/<id>
    4. Borrar el primer registro de material (botón papelera)
    5. Aceptar el confirm() de JS
    6. Comprobar que el número TOTAL de registros disminuye (badge #recordCount)
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset y subir CSV
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(
            driver, host, title_suffix="DeleteRecord"
        )
        upload_csv_for_dataset(driver)

        # 3) Ir a la vista del dataset
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Esperar a que haya al menos un registro en la página
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".material-record-item"))
        )

        # Leer el contador global de registros (badge #recordCount)
        record_count_elem = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "recordCount"))
        )
        count_before = int(record_count_elem.text.strip())

        assert count_before > 0, "El contador de registros es 0 antes de borrar"

        # Obtenemos la lista de registros visibles en esta página
        records_before = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        assert records_before, "No hay registros de materiales visibles en la página"

        # Nos quedamos con el primer registro (para borrar ese)
        first_record = records_before[0]

        # 4) Localizar el botón de borrar dentro de ese registro
        # En el template: onclick="deleteRecord(datasetId, recordId)"
        delete_button = first_record.find_element(
            By.XPATH,
            ".//button[contains(@onclick, 'deleteRecord')]"
        )
        delete_button.click()

        # 5) Aparece el confirm() -> Selenium lo trata como un Alert.
        try:
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
            alert.accept()  # solo OK / Cancel, no se escribe nada
        except TimeoutException:
            html_path = "/tmp/selenium_delete_material_record_no_alert.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            raise AssertionError(
                "No apareció el confirm() de borrado al pulsar deleteRecord. "
                f"HTML guardado en {html_path}"
            )

        # 6) Esperar recarga de página y que el contador cambie
        wait_for_page_to_load(driver)

        def count_has_decreased(d):
            try:
                elem = d.find_element(By.ID, "recordCount")
                current = int(elem.text.strip())
                return current == count_before - 1
            except Exception:
                return False

        WebDriverWait(driver, 15).until(count_has_decreased)

        # Leer de nuevo el contador para la aserción final
        record_count_elem_after = driver.find_element(By.ID, "recordCount")
        count_after = int(record_count_elem_after.text.strip())

        assert count_after == count_before - 1, (
            f"Tras borrar un registro, el contador global debería haber "
            f"disminuido en 1. Antes: {count_before}, después: {count_after}."
        )

    finally:
        close_driver(driver)