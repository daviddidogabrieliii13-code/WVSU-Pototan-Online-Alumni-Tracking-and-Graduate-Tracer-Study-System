/**
 * Bulk Actions JS - WVSU Admin Tables
 * Safe behavior: only binds on tables that explicitly opt in with data-bulk-actions.
 */
document.addEventListener("DOMContentLoaded", function () {
    const bulkTables = document.querySelectorAll("table[data-bulk-actions]");

    bulkTables.forEach(function (table) {
        const scope = table.closest("form") || table.parentElement || table;
        const selectAllCheckbox = table.querySelector("thead [data-select-all]");
        const rowCheckboxes = table.querySelectorAll("tbody [data-row-select]");
        const bulkButton = scope.querySelector("[data-bulk-action]");
        const counterSpan = scope.querySelector("[data-selected-count]");

        if (!selectAllCheckbox || !rowCheckboxes.length) {
            return;
        }

        function getSelectedCount() {
            return Array.from(rowCheckboxes).filter(function (checkbox) {
                return checkbox.checked;
            }).length;
        }

        function syncToolbar() {
            const selectedCount = getSelectedCount();
            if (counterSpan) {
                counterSpan.textContent = String(selectedCount);
            }
            if (bulkButton) {
                const hasSelected = selectedCount > 0;
                bulkButton.disabled = !hasSelected;
                bulkButton.style.opacity = hasSelected ? "1" : "0.6";
            }
        }

        function syncSelectAll() {
            const allChecked = Array.from(rowCheckboxes).every(function (checkbox) {
                return checkbox.checked;
            });
            const noneChecked = Array.from(rowCheckboxes).every(function (checkbox) {
                return !checkbox.checked;
            });
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = !allChecked && !noneChecked;
        }

        selectAllCheckbox.addEventListener("change", function () {
            const shouldCheck = selectAllCheckbox.checked;
            rowCheckboxes.forEach(function (checkbox) {
                checkbox.checked = shouldCheck;
            });
            syncToolbar();
            syncSelectAll();
        });

        rowCheckboxes.forEach(function (checkbox) {
            checkbox.addEventListener("change", function () {
                syncToolbar();
                syncSelectAll();
            });
        });

        if (scope && scope.tagName === "FORM") {
            scope.addEventListener("submit", function (event) {
                const selectedCount = getSelectedCount();
                if (selectedCount === 0) {
                    event.preventDefault();
                    window.alert("Please select at least one user.");
                    return;
                }
                if (!window.confirm("Delete " + selectedCount + " selected account(s)?")) {
                    event.preventDefault();
                }
            });
        }

        syncToolbar();
        syncSelectAll();
    });
});
