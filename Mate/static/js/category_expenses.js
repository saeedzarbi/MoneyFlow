// Make initializePage function globally accessible
window.initializePage = function() {
    console.log('Initializing page...');

    // Wait for DOM to be fully loaded
    function init() {
        const categorySelect = document.getElementById('category');
        console.log('Category select element:', categorySelect);

        if (!categorySelect) {
            console.error('Category select element not found, retrying in 100ms...');
            setTimeout(init, 100);
            return;
        }

        const datePickerOptions = {
            format: 'YYYY-MM-DD',
            initialValue: false,
            autoClose: true,
            timePicker: {
                enabled: false
            },
            onSelect: function(unix) {
                try {
                    const date = new Date(unix);
                    const persianDate = new persianDate(date);
                    return persianDate.format('YYYY-MM-DD');
                } catch (error) {
                    console.error('Date conversion error:', error);
                    return '';
                }
            }
        };

        try {
            $('#startDate').persianDatepicker(datePickerOptions);
            $('#endDate').persianDatepicker(datePickerOptions);
        } catch (error) {
            console.error('Error initializing date pickers:', error);
        }

        function loadCategories() {
            console.log('Loading categories...');
            if (!categorySelect) {
                console.error('Category select element not found');
                return;
            }

            categorySelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
            categorySelect.disabled = true;

            fetch('/get_categories')
                .then(response => {
                    console.log('Response received:', response);
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Categories data received:', data);
                    if (data.success) {
                        categorySelect.innerHTML = '<option value="">انتخاب کنید</option>';

                        data.categories.forEach(category => {
                            const option = document.createElement('option');
                            option.value = category.id;
                            option.textContent = category.name;
                            categorySelect.appendChild(option);
                        });
                    } else {
                        throw new Error(data.message || 'خطا در دریافت لیست');
                    }
                })
                .catch(error => {
                    console.error('Error loading categories:', error);
                    categorySelect.innerHTML = '<option value="">خطا در ارتباط با سرور</option>';
                })
                .finally(() => {
                    categorySelect.disabled = false;
                });
        }

        function searchExpenses() {
            const categoryId = document.getElementById('category').value;
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;

            if (!categoryId) {
                alert('لطفاً یک دسته‌بندی انتخاب کنید');
                return;
            }

            if (startDate && endDate && startDate > endDate) {
                alert('تاریخ شروع نمی‌تواند بزرگتر از تاریخ پایان باشد');
                return;
            }

            const loadingElement = document.getElementById('loading');
            const resultsElement = document.getElementById('results');

            if (loadingElement) loadingElement.style.display = 'block';
            if (resultsElement) resultsElement.style.display = 'none';

            let url = `/category_expenses_summary?category_id=${categoryId}`;
            if (startDate) url += `&start_date=${startDate}`;
            if (endDate) url += `&end_date=${endDate}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        displayResults(data);
                    } else {
                        throw new Error(data.message || 'خطا در دریافت اطلاعات');
                    }
                })
                .catch(error => {
                    console.error('Error fetching expenses:', error);
                    alert('خطا در ارتباط با سرور: ' + error.message);
                })
                .finally(() => {
                    if (loadingElement) loadingElement.style.display = 'none';
                });
        }

        function displayResults(data) {
            const resultsElement = document.getElementById('results');
            if (!resultsElement) {
                console.error('Results element not found');
                return;
            }

            resultsElement.style.display = 'block';

            const elements = {
                categoryName: document.getElementById('categoryName'),
                expenseCount: document.getElementById('expenseCount'),
                totalAmount: document.getElementById('totalAmount'),
                expensesTable: document.getElementById('expensesTable')
            };

            // Update summary information
            if (elements.categoryName) elements.categoryName.textContent = data.category_name;
            if (elements.expenseCount) elements.expenseCount.textContent = data.expense_count;
            if (elements.totalAmount) {
                elements.totalAmount.textContent = new Intl.NumberFormat('fa-IR').format(data.total_amount) + ' تومان';
            }

            // Update expenses table
            if (elements.expensesTable) {
                elements.expensesTable.innerHTML = '';

                if (!data.expenses || data.expenses.length === 0) {
                    elements.expensesTable.innerHTML = `
                        <tr>
                            <td colspan="3" class="text-center">هیچ هزینه‌ای یافت نشد</td>
                        </tr>
                    `;
                    return;
                }

                data.expenses.forEach(expense => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${expense.date || '-'}</td>
                        <td>${new Intl.NumberFormat('fa-IR').format(expense.amount)} تومان</td>
                        <td>${expense.description || '-'}</td>
                    `;
                    elements.expensesTable.appendChild(row);
                });
            }
        }

        // Initialize event listeners
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                e.preventDefault();
                searchExpenses();
            });
        }

        // Load initial data
        console.log('Loading initial data...');
        loadCategories();
    }

    // Start initialization
    init();
};

// Let the HTML file handle the initialization
console.log('Category expenses script loaded, waiting for initialization...');