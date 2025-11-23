let currentFilter = null;
let currentPage = 1;
const datasetId = window.location.pathname.split("/")[2];

async function loadRecommendations(page = 1, filterType = null) {
    const params = new URLSearchParams({ page });
    if (filterType) params.append("filter_type", filterType);

    const response = await fetch(`/dataset/${datasetId}/recommendations?${params.toString()}`);
    const data = await response.json();

    document.querySelector("#recommendations-container").innerHTML = data.html;
    renderPagination(data.page, data.total_pages);
}

function applyFilter(type) {
    currentFilter = type;
    currentPage = 1;
    loadRecommendations(currentPage, currentFilter);
}

function renderPagination(page, total) {
    const pagination = document.querySelector("#pagination");
    pagination.innerHTML = "";
    for (let p = 1; p <= total; p++) {
        const li = document.createElement("li");
        li.className = `page-item ${p === page ? "active" : ""}`;
        li.innerHTML = `<a class="page-link" href="#">${p}</a>`;
        li.onclick = e => {
            e.preventDefault();
            currentPage = p;
            loadRecommendations(p, currentFilter);
        };
        pagination.appendChild(li);
    }
}

document.addEventListener("DOMContentLoaded", () => loadRecommendations());
