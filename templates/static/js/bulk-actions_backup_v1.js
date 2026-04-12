/**
 * Bulk Actions JS - WVSU Admin Tables
 */
document.addEventListener('DOMContentLoaded', function() {
    // Find all bulk tables
    const bulkTables = document.querySelectorAll('table[data-bulk-actions]');
    
    bulkTables.forEach(table => {
        const selectAllCheckbox = table.querySelector('thead [data-select-all]');
        const rowCheckboxes = table.querySelectorAll('tbody [data-row-select]');
        const bulkButton = table.querySelector('[data-bulk-action]');
        const counterSpan = table.querySelector('[data-selected-count]');
        
        if (!selectAllCheckbox || !rowCheckboxes.length) return;
        
        // Select All toggle
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            rowCheckboxes.forEach(cb => {
                cb.checked = isChecked;
            });
            updateCounter(counterSpan, rowCheckboxes);
            toggleBulkButton(bulkButton);
        });
        
        // Individual checkboxes
        rowCheckboxes.forEach(cb => {
            cb.addEventListener('change', function() {
                updateCounter(counterSpan, rowCheckboxes);
                toggleBulkButton(bulkButton);
                // Update select all if all/none selected
                const allChecked = Array.from(rowCheckboxes).every(rowCb => rowCb.checked);
                const noneChecked = Array.from(rowCheckboxes).every(rowCb => !rowCb.checked);
                selectAllCheckbox.indeterminate = !allChecked && !noneChecked;
                selectAllCheckbox.checked = allChecked;
            });
        });
        
        // Bulk form submit confirmation
        if (bulkButton) {
            bulkButton.closest('form').addEventListener('submit', function(e) {
                const selectedCount = getSelectedCount(rowCheckboxes);
                if (selectedCount === 0) {
                    e.preventDefault();
                    alert('Please select items first.');
                    return false;
                }
                if (!confirm(`Delete ${selectedCount} item(s) permanently?`)) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    });
    
    function updateCounter(counterSpan, checkboxes) {
        if (counterSpan) {
            const count = getSelectedCount(checkboxes);
            counterSpan.textContent = count;
        }
    }
    
    function toggleBulkButton(button) {
        if (button) {
            const hasSelected = getSelectedCount(button.closest('table').querySelectorAll('[data-row-select]')) > 0;
            button.disabled = !hasSelected;
            button.style.opacity = hasSelected ? '1' : '0.5';
        }
    }
    
    function getSelectedCount(checkboxes) {
        return Array.from(checkboxes).filter(cb => cb.checked).length;
    }
});
