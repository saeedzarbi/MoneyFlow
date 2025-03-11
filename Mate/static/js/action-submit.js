function convertPersianToEnglishNumbers(str) {
    return str.replace(/[۰-۹]/g, function(d) {
        return d.charCodeAt(0) - 1776;
    });
}

// Format currency
function formatCurrency(amount) {
    return amount.toLocaleString('fa-IR') + ' تومان';
}

$(document).ready(function() {
    // Initialize Persian Date Picker
    $("#expenseDate, #incomeDate").pDatepicker({
        format: 'YYYY-MM-DD',
        initialValue: false,
        autoClose: true,
        calendar: {
            persian: {
                locale: 'fa'
            }
        }
    });

    // Load initial data
    loadCategories();
    loadRecentTransactions();
    updateDashboardStats();

    // Expense form submission
    $("#expenseForm").submit(function(event) {
        event.preventDefault();

        let amount = $("#amount").val().trim();
        let category = $("#category").val();
        let description = $("#description").val().trim();
        let date = $("#expenseDate").val().trim();
        date = convertPersianToEnglishNumbers(date);

        if (amount === "" || category === "" || !date) {
            alert("تمامی فیلدها باید پر شوند!");
            return;
        }

        $.ajax({
            url: "/add_expense",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                amount: amount,
                category: category,
                date: date,
                description: description
            }),
            success: function(response) {
                alert(response.message);
                $("#expenseModal").modal('hide');
                $("#amount").val("");
                $("#category").val("");
                $("#description").val("");
                $("#expenseDate").val("");
                loadRecentTransactions();
                updateDashboardStats();
            },
            error: function(xhr, status, error) {
                console.log("Error:", error);
                alert("مشکلی در ثبت هزینه پیش آمده است. لطفاً دوباره تلاش کنید.");
            }
        });
    });

    // Income form submission
    $("#incomeForm").submit(function(event) {
        event.preventDefault();
        let incomeAmount = $("#incomeAmount").val().trim();
        let incomeCategory = $("#incomeCategory").val();
        let incomeDescription = $("#incomeDescription").val().trim();
        let incomeDate = $("#incomeDate").val().trim();
        incomeDate = convertPersianToEnglishNumbers(incomeDate);

        if (incomeAmount === "" || incomeCategory === "" || !incomeDate) {
            alert("تمامی فیلدها باید پر شوند!");
            return;
        }
        $.ajax({
            url: "/add_income",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                incomeAmount: incomeAmount,
                incomeCategory: incomeCategory,
                incomeDescription: incomeDescription,
                date: incomeDate
            }),
            success: function(response) {
                alert(response.message);
                $("#incomeModal").modal('hide');
                $("#incomeAmount").val("");
                $("#incomeCategory").val("");
                $("#incomeDescription").val("");
                $("#incomeDate").val("");
                loadRecentTransactions();
                updateDashboardStats();
            },
            error: function(xhr, status, error) {
                alert("مشکلی در ثبت درآمد پیش آمده است. لطفاً دوباره تلاش کنید.");
            }
        });
    });

    // Expense category form submission
    $("#addExpenseCategoryForm").submit(function(event) {
        event.preventDefault();
        let categoryName = $("#categoryName").val().trim();

        if (categoryName === "") {
            alert("نام دسته‌بندی نمی‌تواند خالی باشد.");
            return;
        }

        $.ajax({
            url: "/add_category",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ categoryName: categoryName }),
            success: function(response) {
                alert(response.message);
                $("#addExpenseCategoryModal").modal("hide");
                $("#categoryName").val("");
                loadCategories();
            },
            error: function(xhr) {
                let errorMessage = "خطا در ثبت دسته‌بندی";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                alert(errorMessage);
            }
        });
    });

    // Income category form submission
    $("#addIncomeCategoryForm").submit(function(event) {
        event.preventDefault();
        let incomeCategoryName = $("#incomeCategoryName").val().trim();

        if (incomeCategoryName === "") {
            alert("نام دسته‌بندی نمی‌تواند خالی باشد.");
            return;
        }

        $.ajax({
            url: "/add_income_category",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ incomeCategoryName: incomeCategoryName }),
            success: function(response) {
                alert(response.message);
                $("#addIncomeCategoryModal").modal("hide");
                $("#incomeCategoryName").val("");
                loadCategories();
            },
            error: function(xhr) {
                let errorMessage = "خطا در ثبت دسته‌بندی درآمد";
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMessage = xhr.responseJSON.error;
                }
                alert(errorMessage);
            }
        });
    });
});

// Update dashboard statistics
function updateDashboardStats() {
    fetch('/get_monthly_analysis')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('monthlyExpense').textContent = formatCurrency(data.analysis.total_expense);
                document.getElementById('monthlyIncome').textContent = formatCurrency(data.analysis.total_income);
                document.getElementById('remainingBudget').textContent = formatCurrency(data.analysis.net_savings);
                document.getElementById('transactionCount').textContent =
                    data.analysis.expense_breakdown.length + data.analysis.income_breakdown.length;
            }
        })
        .catch(error => console.error('Error:', error));
}

// Load categories
function loadCategories() {
    // Load expense categories
    fetch('/get_categories')
        .then(response => response.json())
        .then(data => {
            const expenseSelect = document.getElementById('category');
            const expenseCategoriesDiv = document.getElementById('expenseCategories');

            expenseSelect.innerHTML = '<option value="">انتخاب کنید</option>';
            expenseCategoriesDiv.innerHTML = '';

            data.categories.forEach(category => {
                expenseSelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                expenseCategoriesDiv.innerHTML += `
                    <span class="badge bg-primary p-2">
                        ${category.name}
                    </span>
                `;
            });
        });

    // Load income categories
    fetch('/get_income_categories')
        .then(response => response.json())
        .then(data => {
            const incomeSelect = document.getElementById('incomeCategory');
            const incomeCategoriesDiv = document.getElementById('incomeCategories');

            incomeSelect.innerHTML = '<option value="">انتخاب کنید</option>';
            incomeCategoriesDiv.innerHTML = '';

            data.categories.forEach(category => {
                incomeSelect.innerHTML += `<option value="${category.id}">${category.name}</option>`;
                incomeCategoriesDiv.innerHTML += `
                    <span class="badge bg-success p-2">
                        ${category.name}
                    </span>
                `;
            });
        });
}

// Load recent transactions
function loadRecentTransactions() {
    const tbody = document.getElementById('recentTransactions');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center">در حال بارگذاری...</td></tr>';

    Promise.all([
            fetch('/get_recent_expenses').then(res => res.json()),
            fetch('/get_recent_incomes').then(res => res.json())
        ])
        .then(([expenses, incomes]) => {
            const transactions = [
                ...expenses.map(e => ({...e, type: 'expense' })),
                ...incomes.map(i => ({...i, type: 'income' }))
            ].sort((a, b) => new Date(b.date) - new Date(a.date));

            tbody.innerHTML = transactions.map(t => `
            <tr>
                <td>${t.date}</td>
                <td>
                    <span class="badge ${t.type === 'expense' ? 'bg-danger' : 'bg-success'}">
                        ${t.type === 'expense' ? 'هزینه' : 'درآمد'}
                    </span>
                </td>
                <td>${t.category}</td>
                <td>${formatCurrency(t.amount)}</td>
                <td>${t.description || '-'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTransaction('${t.type}', ${t.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        });
}

// Delete transaction
function deleteTransaction(type, id) {
    if (!confirm('آیا از حذف این تراکنش اطمینان دارید؟')) return;

    const endpoint = type === 'expense' ? `/detail/${id}` : `/income-detail/${id}`;

    fetch(endpoint, { method: 'DELETE' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadRecentTransactions();
                updateDashboardStats();
            }
        })
        .catch(error => console.error('Error:', error));
}

// Show modal functions
function showAddExpenseCategoryModal() {
    $("#addExpenseCategoryModal").modal('show');
}

function showAddIncomeCategoryModal() {
    $("#addIncomeCategoryModal").modal('show');
}