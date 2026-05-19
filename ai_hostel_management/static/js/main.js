document.addEventListener("DOMContentLoaded", () => {
    setupSidebar();
    setupLiveSearch();
    setupFormValidation();
    setupModals();
    setupKeyboardShortcut();
});

function setupSidebar() {
    const sidebar = document.getElementById("sidebar");
    const toggleButton = document.querySelector("[data-sidebar-toggle]");
    const overlay = document.querySelector("[data-sidebar-overlay]");

    if (!sidebar || !toggleButton || !overlay) {
        return;
    }

    const closeSidebar = () => {
        sidebar.classList.remove("is-open");
        overlay.classList.remove("show");
    };

    toggleButton.addEventListener("click", () => {
        sidebar.classList.toggle("is-open");
        overlay.classList.toggle("show");
    });

    overlay.addEventListener("click", closeSidebar);

    window.addEventListener("resize", () => {
        if (window.innerWidth > 900) {
            closeSidebar();
        }
    });
}

function setupLiveSearch() {
    document.querySelectorAll("[data-table-search]").forEach((input) => {
        const tableId = input.dataset.tableSearch;
        const table = document.getElementById(tableId);

        if (!table) {
            return;
        }

        input.addEventListener("input", () => {
            const query = input.value.trim().toLowerCase();
            const rows = table.querySelectorAll("tbody tr");

            rows.forEach((row) => {
                const match = row.textContent.toLowerCase().includes(query);
                row.style.display = match ? "" : "none";
            });
        });
    });
}

function setupFormValidation() {
    document.querySelectorAll("form[data-validate='true']").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const fields = form.querySelectorAll("[required]");
            let valid = true;

            fields.forEach((field) => {
                const isEmpty = !field.value.trim();
                field.classList.toggle("invalid", isEmpty);
                if (isEmpty) {
                    valid = false;
                }
            });

            const fromDate = form.querySelector("[name='from_date']");
            const toDate = form.querySelector("[name='to_date']");
            if (fromDate && toDate && fromDate.value && toDate.value) {
                const invalidDateRange = new Date(fromDate.value) > new Date(toDate.value);
                toDate.classList.toggle("invalid", invalidDateRange);
                if (invalidDateRange) {
                    valid = false;
                }
            }

            if (!valid) {
                event.preventDefault();
                showInlineAlert("Please review the highlighted fields before submitting.", "error");
            }
        });
    });
}

function setupModals() {
    document.querySelectorAll("[data-open-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            const modal = document.getElementById(button.dataset.openModal);
            modal?.classList.add("show");
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            button.closest(".modal")?.classList.remove("show");
        });
    });

    document.querySelectorAll(".modal").forEach((modal) => {
        modal.addEventListener("click", (event) => {
            if (event.target === modal) {
                modal.classList.remove("show");
            }
        });
    });
}

function setupKeyboardShortcut() {
    document.addEventListener("keydown", (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
            const searchInput = document.querySelector("[data-table-search], .topbar__search input");
            if (searchInput) {
                event.preventDefault();
                searchInput.focus();
                searchInput.select?.();
            }
        }
    });
}

function showInlineAlert(message, type) {
    const page = document.querySelector(".page-content") || document.body;
    const alert = document.createElement("div");
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<i class="fa-solid fa-circle-exclamation"></i><span>${message}</span>`;
    page.prepend(alert);

    setTimeout(() => {
        alert.remove();
    }, 4000);
}
