import json
import os
import re
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


def go_to_dataset_edit_from_list(driver, host: str, dataset_title: str):
    """
    /dataset/list  -> busca la fila por título -> click en 'Edit metadata'
    """
    driver.get(f"{host}/dataset/list")
    wait_for_page_to_load(driver)

    row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//table//tbody//tr[.//a[normalize-space()='{dataset_title}']]"))
    )

    edit_link = row.find_element(
        By.XPATH, ".//a[@title='Edit metadata' and contains(@href, '/materials/') and contains(@href, '/edit')]"
    )
    edit_link.click()
    wait_for_page_to_load(driver)

    assert driver.current_url.endswith("/edit"), f"No estás en /materials/<id>/edit. URL: {driver.current_url}"


def extract_record_id_from_href(href: str) -> str | None:
    m = re.search(r"/records/(\d+)/edit", href or "")
    return m.group(1) if m else None


def get_view_csv_json(driver, host: str, dataset_id: str) -> dict:
    """
    Obtiene el JSON REAL de /materials/<id>/view_csv usando fetch() desde el navegador.
    Esto evita el JSON viewer de Firefox/Chrome que rompe json.loads(body.text).
    """
    url = f"{host}/materials/{dataset_id}/view_csv"

    # execute_async_script: el último argumento es callback
    result = driver.execute_async_script(
        """
        const url = arguments[0];
        const done = arguments[arguments.length - 1];

        fetch(url, { headers: { "Accept": "application/json" } })
          .then(r => r.json())
          .then(data => done(JSON.stringify(data)))
          .catch(err => done(JSON.stringify({ "__error__": String(err) })));
        """,
        url,
    )

    data = json.loads(result)
    if "__error__" in data:
        raise AssertionError(f"Error obteniendo JSON por fetch() en view_csv: {data['__error__']}")
    return data


def submit_delete_record_form_with_csrf(driver, dataset_id: str, record_id: str):
    """
    Ejecuta un POST real a /materials/<dataset_id>/records/<record_id>/delete
    usando el csrf_token que exista en la página actual.
    """
    csrf = driver.find_element(By.NAME, "csrf_token").get_attribute("value")
    assert csrf, "No se encontró csrf_token en la página actual"

    driver.execute_script(
        """
        const datasetId = arguments[0];
        const recordId = arguments[1];
        const csrf = arguments[2];

        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/materials/${datasetId}/records/${recordId}/delete`;

        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrf_token';
        input.value = csrf;
        form.appendChild(input);

        document.body.appendChild(form);
        form.submit();
        """,
        dataset_id,
        record_id,
        csrf,
    )


def wait_until_csv_reflects_value(driver, host, dataset_id, record_id, expected_value, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        data = get_view_csv_json(driver, host, dataset_id)
        row = next((r for r in data.get("rows", []) if str(r.get("record_id", "")).strip() == str(record_id)), None)
        if row:
            v = str(row.get("property_value", "")).strip()
            if v in {expected_value, expected_value.rstrip(".0"), "9999", "9999.0", "9999.00"}:
                return
        time.sleep(0.5)
    raise AssertionError(f"El CSV no refleja el valor esperado '{expected_value}' para record_id={record_id}")


def wait_for_page_to_load(driver, timeout: int = 15):
    WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")


def login(driver, host: str, email: str = "user1@example.com", password: str = "1234"):
    """
    Hace login en /login y verifica que no nos quedamos en la página de login.
    """
    driver.get(f"{host}/login")
    wait_for_page_to_load(driver)

    # Esperar al formulario
    email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
    password_field = driver.find_element(By.NAME, "password")

    email_field.clear()
    email_field.send_keys(email)
    password_field.clear()
    password_field.send_keys(password)

    # Intentar hacer click en botón submit
    try:
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
        )
        submit_button.click()
    except TimeoutException:
        # Fallback: ENTER en el campo de contraseña
        password_field.send_keys(Keys.RETURN)

    wait_for_page_to_load(driver)

    current_url = driver.current_url
    assert "/login" not in current_url, f"El login no ha funcionado, seguimos en /login. URL actual: {current_url}"


def create_materials_dataset_and_go_to_csv_upload(driver, host: str, title_suffix: str = ""):
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
        title_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title")))
    except TimeoutException:
        html_path = "/tmp/selenium_dataset_upload_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            f"No se encontró el input name='title' en /dataset/upload. " f"HTML guardado en {html_path}"
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
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "csvFile")))
    except TimeoutException:
        html_path = "/tmp/selenium_csv_upload_page_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se ha llegado a la página de subida de CSV " f"(/materials/<id>/upload). HTML guardado en {html_path}"
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

    file_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "csvFile")))
    file_input.send_keys(csv_path)

    upload_button = driver.find_element(By.ID, "uploadBtn")
    upload_button.click()

    # Esperar a que aparezca el mensaje de éxito
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#uploadResult .alert-success"))
        )
    except TimeoutException:
        html_path = "/tmp/selenium_csv_upload_result_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se ha mostrado el mensaje de éxito tras subir el CSV. " f"HTML guardado en {html_path}"
        )


def go_to_view_dataset_from_upload_result(driver, dataset_id: str):
    """
    Desde la pantalla /materials/<id>/upload (tras subir CSV),
    pulsa el botón "View Dataset" para ir a /materials/<id>.
    """
    try:
        view_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'View Dataset')]"))
        )
    except TimeoutException:
        html_path = "/tmp/selenium_view_dataset_button_error.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise AssertionError(
            "No se encontró el botón/enlace 'View Dataset' tras subir el CSV. " f"HTML guardado en {html_path}"
        )

    view_button.click()
    wait_for_page_to_load(driver)

    current_url = driver.current_url
    assert f"/materials/{dataset_id}" in current_url, (
        f"No estamos en la vista del dataset tras pulsar 'View Dataset'. " f"URL actual: {current_url}"
    )


def _wait_for_recommendations_wrapper_update(driver, wrapper_elem, old_html, timeout=15):
    """
    Espera a que el contenido del wrapper cambie (AJAX).
    """

    def changed(d):
        try:
            new_html = wrapper_elem.get_attribute("innerHTML") or ""
            return new_html != old_html and len(new_html.strip()) > 0
        except Exception:
            return False

    WebDriverWait(driver, timeout).until(changed)


def _extract_record_id_from_href(href: str) -> int | None:
    m = re.search(r"/records/(\d+)/edit", href or "")
    return int(m.group(1)) if m else None


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
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="E2E")

        # 3) Subir CSV
        upload_csv_for_dataset(driver)

        # 4) Ir a "View Dataset"
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # 5) Comprobar que hay registros en la vista del dataset
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(@class, 'material-record-item') " "or contains(text(), 'No material records')]",
                )
            )
        )

        material_items = driver.find_elements(By.CSS_SELECTOR, ".material-record-item")
        assert len(material_items) > 0, "No se han creado registros de materiales a partir del CSV"

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
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="Listed")
        upload_csv_for_dataset(driver)

        # 3) Ir a la lista de datasets del usuario
        driver.get(f"{host}/dataset/list")
        wait_for_page_to_load(driver)

        # 4) Buscar nuestro dataset en la tabla
        table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "table")))
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
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="Search")
        upload_csv_for_dataset(driver)

        # 3) Ir a la vista del dataset
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Esperar a que haya al menos un registro de material
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".material-record-item")))
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

        assert visible_items, f"El filtro no ha dejado visible ningún material al buscar '{search_term}'"

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

        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="CSVModal")
        upload_csv_for_dataset(driver)
        go_to_view_dataset_from_upload_result(driver, dataset_id)

        # Pulsar el botón "View" del CSV (con onclick="viewCSV()")
        view_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'viewCSV')]"))
        )
        view_button.click()

        # Esperar a que se cargue la tabla dentro del modal
        headers_row = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "csvHeaders")))
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
        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix=" Stats")
        upload_csv_for_dataset(driver)

        # 3) Ir a la página de estadísticas
        stats_url = f"{host}/materials/{dataset_id}/statistics"
        driver.get(stats_url)
        wait_for_page_to_load(driver)

        current_url = driver.current_url

        # 4.a) Asegurarnos de que no nos ha mandado a /login
        assert "/login" not in current_url, (
            "La página de estadísticas ha redirigido a /login. " f"URL actual: {current_url}"
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

        assert dataset_title in body_text or base_title in body_text or "Statistics" in body_text, (
            "La página de estadísticas no parece mostrar información del dataset.\n"
            f"Buscábamos algo como '{dataset_title}' o 'Statistics' y no aparece."
        )

    finally:
        close_driver(driver)


def test_delete_material_record_from_edit_dataset_page():
    """
    Borra un MaterialRecord (POST real) usando CSRF, partiendo desde /materials/<id>/edit.
    Comprueba que el total de filas en /view_csv disminuye en 1.
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        dataset_id, dataset_title = create_materials_dataset_and_go_to_csv_upload(driver, host, "DeleteRecord")
        upload_csv_for_dataset(driver)

        # Total antes (del CSV)
        before = get_view_csv_json(driver, host, dataset_id)
        total_before = int(before.get("total", 0))
        assert total_before > 0, "No hay records para borrar"

        # Ir a /materials/<id>/edit
        go_to_dataset_edit_from_list(driver, host, dataset_title)

        # Sacar un record_id desde el primer enlace de editar record
        record_edit_link = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/records/') and contains(@href, '/edit')]"))
        )
        href = record_edit_link.get_attribute("href")
        record_id = extract_record_id_from_href(href)
        assert record_id, f"No pude extraer record_id del href: {href}"

        # POST delete con csrf_token (desde la propia página /edit donde existe csrf_token)
        submit_delete_record_form_with_csrf(driver, dataset_id, record_id)
        wait_for_page_to_load(driver)

        # Validar que el total baja
        after = get_view_csv_json(driver, host, dataset_id)
        total_after = int(after.get("total", 0))

        assert (
            total_after == total_before - 1
        ), f"El total no bajó en 1 tras borrar. Antes={total_before}, Después={total_after}"

    finally:
        close_driver(driver)


def test_fakenodo_assigns_dataset_doi_visible_in_view():
    """
    Flujo: comprobar que Fakenodo asigna un DOI al MaterialsDataset
    y que se muestra en la vista /materials/<id> dentro del bloque "Dataset DOI".

    Requisitos del template:
    - exista el bloque con texto "Dataset DOI"
    - el enlace sea https://doi.org/<dataset_doi>
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        # 1) Login
        login(driver, host)

        # 2) Crear dataset -> ir a /materials/<id>/upload
        dataset_id, _ = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="DOI")

        # 3) Subir CSV y ir a /materials/<id>
        upload_csv_for_dataset(driver)
        go_to_view_dataset_from_upload_result(driver, dataset_id)
        wait_for_page_to_load(driver)

        # 4) Localizar el bloque "Dataset DOI" (evitando coger el link "Edit")
        doi_label = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Dataset DOI']"))
        )

        # Subir a la fila y coger el link SOLO de la columna derecha (col-md-8)
        doi_link = doi_label.find_element(
            By.XPATH,
            "./ancestor::div[contains(@class,'row')][1]//div[contains(@class,'col-md-8')]//a",
        )

        doi_text = (doi_link.text or "").strip()
        doi_href = (doi_link.get_attribute("href") or "").strip()

        assert doi_text, "El bloque 'Dataset DOI' existe, pero el enlace no tiene texto"
        assert doi_href, "El bloque 'Dataset DOI' existe, pero el enlace no tiene href"

        # 5) Comprobar formato: el href debe ir a doi.org/<doi_text>
        expected_prefix = "https://doi.org/"
        assert doi_href.startswith(expected_prefix), "El enlace del DOI no apunta a doi.org.\n" f"href: {doi_href}"

        # el template hace: https://doi.org/{{ dataset.ds_meta_data.dataset_doi }}
        assert doi_href == f"{expected_prefix}{doi_text}", (
            "El href del DOI no coincide con el DOI mostrado.\n"
            f"Texto DOI: {doi_text}\n"
            f"href: {doi_href}\n"
            f"Esperado: {expected_prefix}{doi_text}"
        )

        # Validación mínima del DOI (flexible pero útil)
        assert doi_text.startswith("10."), (
            "El DOI debería empezar por '10.' (formato típico de DOI).\n" f"Texto DOI: {doi_text}"
        )

    finally:
        close_driver(driver)


def test_top_global_page_loads_and_metric_toggle():
    """
    1) Login
    2) Ir a /datasets/top (por defecto downloads)
    3) Verificar que hay tabla o mensaje "No datasets found."
    4) Cambiar a 'views' y comprobar que la cabecera cambia a Views (si hay tabla)
    5) Volver a 'downloads' y comprobar cabecera Downloads (si hay tabla)
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        driver.get(f"{host}/datasets/top")
        wait_for_page_to_load(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Top" in body_text, "No parece la página de Top datasets"

        # Tabla o placeholder
        has_table = len(driver.find_elements(By.TAG_NAME, "table")) > 0
        has_empty = "No datasets found" in body_text
        assert has_table or has_empty, "No hay tabla ni mensaje de 'No datasets found.'"

        # Cambiar a Most viewed
        viewed_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @name='metric' and @value='views']"))
        )
        viewed_btn.click()
        wait_for_page_to_load(driver)

        if len(driver.find_elements(By.TAG_NAME, "table")) > 0:
            ths = driver.find_elements(By.CSS_SELECTOR, "table thead th")
            headers = [th.text.strip() for th in ths]
            assert "Views" in headers, f"Cabeceras inesperadas en modo views: {headers}"

        # Volver a Most downloaded
        downloads_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and @name='metric' and @value='downloads']"))
        )
        downloads_btn.click()
        wait_for_page_to_load(driver)

        if len(driver.find_elements(By.TAG_NAME, "table")) > 0:
            ths = driver.find_elements(By.CSS_SELECTOR, "table thead th")
            headers = [th.text.strip() for th in ths]
            assert "Downloads" in headers, f"Cabeceras inesperadas en modo downloads: {headers}"

    finally:
        close_driver(driver)


def test_top_global_limit_and_invalid_params_are_sanitized():
    """
    1) Login
    2) Ir con limit=3 y comprobar filas <= 3 (si hay tabla)
    3) Ir con metric inválido y comprobar que vuelve a Downloads (si hay tabla)
    4) Ir con days inválido y comprobar que la página carga (no rompe)
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        # 2) limit=3, days=7
        driver.get(f"{host}/datasets/top?metric=downloads&days=7&limit=3")
        wait_for_page_to_load(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        has_table = len(driver.find_elements(By.TAG_NAME, "table")) > 0
        has_empty = "No datasets found" in body_text
        assert has_table or has_empty, "No hay tabla ni mensaje de 'No datasets found.'"

        if has_table:
            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            assert len(rows) <= 3, f"Esperaba <=3 filas, pero hay {len(rows)}"

        # 3) metric inválido -> debe sanearse a downloads
        driver.get(f"{host}/datasets/top?metric=INVALID&days=7&limit=5")
        wait_for_page_to_load(driver)

        if len(driver.find_elements(By.TAG_NAME, "table")) > 0:
            ths = driver.find_elements(By.CSS_SELECTOR, "table thead th")
            headers = [th.text.strip() for th in ths]
            assert "Downloads" in headers, f"metric inválido no se saneó a downloads. Cabeceras: {headers}"

        # 4) days inválido -> debe sanearse a 30 (no se ve directo, pero no debe romper)
        driver.get(f"{host}/datasets/top?metric=downloads&days=999&limit=5")
        wait_for_page_to_load(driver)

        body_text = driver.find_element(By.TAG_NAME, "body").text
        assert "Top" in body_text, "La página no cargó correctamente con days inválido"

    finally:
        close_driver(driver)


def test_edit_material_record_from_edit_dataset_page():
    """
    Edita un MaterialRecord desde /materials/<id>/edit (edit dataset):
    - abre el primer botón de editar record (.edit-record-btn)
    - cambia property_value
    - vuelve a /materials/<id>/edit (return_to=edit)
    - pulsa "Save All Changes" para consolidar (y crear versión)
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        dataset_id, _ = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="EditRecord")
        upload_csv_for_dataset(driver)

        # Ir a edit dataset
        driver.get(f"{host}/materials/{dataset_id}/edit")
        wait_for_page_to_load(driver)

        # Esperar a que haya records
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".material-record-item")))

        # Click primer botón editar record
        edit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.edit-record-btn")))
        href = edit_btn.get_attribute("href")
        record_id = _extract_record_id_from_href(href)
        assert record_id, f"No pude extraer record_id del href: {href}"

        edit_btn.click()
        wait_for_page_to_load(driver)

        # Edit form record: cambiar property_value
        new_value = "9999.0"
        prop_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "property_value")))
        prop_input.click()
        prop_input.send_keys(Keys.CONTROL + "a")
        prop_input.send_keys(Keys.DELETE)
        prop_input.send_keys(new_value)

        submit_record = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit']"))
        )
        submit_record.click()
        wait_for_page_to_load(driver)

        # Debe volver a /materials/<id>/edit (por return_to=edit)
        assert (
            f"/materials/{dataset_id}/edit" in driver.current_url
        ), f"No volvimos a edit dataset. URL actual: {driver.current_url}"

        # Guardar todos los cambios (crea versión única)
        save_all = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#editDatasetForm button[type='submit']"))
        )
        save_all.click()
        wait_for_page_to_load(driver)

        # Redirige a la vista del dataset
        assert f"/materials/{dataset_id}" in driver.current_url

    finally:
        close_driver(driver)


def test_version_history_creates_new_version_after_edit():
    """
    E2E:
    - Crear dataset + CSV (v1)
    - Editar un record desde /materials/<id>/edit
    - Guardar cambios
    - Ir a /materials/<id>/versions
    - Comprobar que existen al menos 2 versiones
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        dataset_id, _ = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="VersionTest")
        upload_csv_for_dataset(driver)

        # Editar dataset → crea v2
        driver.get(f"{host}/materials/{dataset_id}/edit")
        wait_for_page_to_load(driver)

        edit_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.edit-record-btn")))
        edit_btn.click()
        wait_for_page_to_load(driver)

        prop_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "property_value")))
        prop_input.clear()
        prop_input.send_keys("8888.0")

        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait_for_page_to_load(driver)

        # Guardar todos los cambios (crea versión)
        save_all = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#editDatasetForm button[type='submit']"))
        )
        save_all.click()
        wait_for_page_to_load(driver)

        # Ir a version history
        driver.get(f"{host}/materials/{dataset_id}/versions")
        wait_for_page_to_load(driver)

        versions = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".version-checkbox"))
        )

        assert len(versions) >= 2, f"Se esperaban al menos 2 versiones, encontradas {len(versions)}"

    finally:
        close_driver(driver)


def test_version_compare_ui_renders_changes():
    """
    E2E:
    - Crear dataset (v1)
    - Editar record (v2)
    - Ir a /versions
    - Seleccionar 2 versiones
    - Compare
    - Verificar UI de comparación
    """
    driver = initialize_driver()
    host = get_host_for_selenium_testing()

    try:
        login(driver, host)

        dataset_id, _ = create_materials_dataset_and_go_to_csv_upload(driver, host, title_suffix="CompareUI")
        upload_csv_for_dataset(driver)

        # Crear v2 editando record
        driver.get(f"{host}/materials/{dataset_id}/edit")
        wait_for_page_to_load(driver)

        driver.find_element(By.CSS_SELECTOR, "a.edit-record-btn").click()
        wait_for_page_to_load(driver)

        prop_input = driver.find_element(By.NAME, "property_value")
        prop_input.clear()
        prop_input.send_keys("7777.0")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait_for_page_to_load(driver)

        driver.find_element(By.CSS_SELECTOR, "#editDatasetForm button[type='submit']").click()
        wait_for_page_to_load(driver)

        # Version history
        driver.get(f"{host}/materials/{dataset_id}/versions")
        wait_for_page_to_load(driver)

        checkboxes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".version-checkbox"))
        )
        assert len(checkboxes) >= 2

        # Seleccionar 2 versiones
        checkboxes[0].click()
        checkboxes[1].click()

        compare_btn = driver.find_element(By.ID, "compareBtn")
        assert compare_btn.is_enabled()

        compare_btn.click()
        wait_for_page_to_load(driver)

        # Validar UI compare
        assert "/versions/compare" in driver.current_url
        assert "Comparing Versions" in driver.page_source
        assert (
            "Modified Records" in driver.page_source
            or "Deleted Records" in driver.page_source
            or "Added Records" in driver.page_source
        )

    finally:
        close_driver(driver)
