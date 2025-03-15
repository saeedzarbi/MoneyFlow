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
    // Initialize date pickers
    $("#expenseDate, #incomeDate").persianDatepicker({
        format: 'YYYY-MM-DD',
        initialValue: false
    });

    // Load categories on page load
    loadCategories();
    loadIncomeCategories();
    loadRecentTransactions();

    $("#expenseForm").submit(function(event) {
        event.preventDefault();
        let amount = unformatNumber($("#amount").val());
        let category = $("#category").val();
        let description = $("#description").val();
        let date = $("#expenseDate").val();

        if (!amount || !category || !date) {
            alert("لطفاً همه فیلدها را پر کنید!");
            return;
        }

        $.ajax({
            url: "/add_expense",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                amount: amount,
                category: category,
                description: description,
                date: date
            }),
            success: function(response) {
                alert(response.message);
                $("#amount").val("");
                $("#category").val("");
                $("#description").val("");
                $("#expenseDate").val("");
                $('#expenseModal').modal('hide');
                loadRecentTransactions();
            },
            error: function(xhr) {
                alert("خطا در ثبت هزینه: " + xhr.responseJSON.message);
            }
        });
    });

    $("#incomeForm").submit(function(event) {
        event.preventDefault();
        let amount = unformatNumber($("#incomeAmount").val());
        let category = $("#incomeCategory").val();
        let description = $("#incomeDescription").val();
        let date = $("#incomeDate").val();

        if (!amount || !category || !date) {
            alert("لطفاً همه فیلدها را پر کنید!");
            return;
        }

        $.ajax({
            url: "/add_income",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                incomeAmount: amount,
                incomeCategory: category,
                incomeDescription: description,
                date: date
            }),
            success: function(response) {
                alert(response.message);
                $("#incomeAmount").val("");
                $("#incomeCategory").val("");
                $("#incomeDescription").val("");
                $("#incomeDate").val("");
                $('#incomeModal').modal('hide');
                loadRecentTransactions();
            },
            error: function(xhr) {
                alert("خطا در ثبت درآمد: " + xhr.responseJSON.message);
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
    $.ajax({
        url: "/get_categories",
        type: "GET",
        success: function(response) {
            if (response.success) {
                let categorySelect = $("#category");
                categorySelect.empty();
                categorySelect.append('<option value="">انتخاب کنید</option>');
                response.categories.forEach(function(category) {
                    categorySelect.append(`<option value="${category.id}">${category.name}</option>`);
                });
            }
        }
    });
}

function loadIncomeCategories() {
    $.ajax({
        url: "/get_income_categories",
        type: "GET",
        success: function(response) {
            if (response.success) {
                let categorySelect = $("#incomeCategory");
                categorySelect.empty();
                categorySelect.append('<option value="">انتخاب کنید</option>');
                response.categories.forEach(function(category) {
                    categorySelect.append(`<option value="${category.id}">${category.name}</option>`);
                });
            }
        }
    });
}

// Load recent transactions
function loadRecentTransactions() {
    // Load recent expenses
    $.ajax({
        url: "/get_recent_expenses",
        type: "GET",
        success: function(expenses) {
            let transactionsHtml = "";
            expenses.forEach(function(expense) {
                transactionsHtml += `
                    <tr>
                        <td>${expense.date}</td>
                        <td><span class="badge bg-danger">هزینه</span></td>
                        <td>${expense.category}</td>
                        <td>${formatNumber(expense.amount)} تومان</td>
                        <td>${expense.description || "-"}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteExpense(${expense.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            $("#recentTransactions").html(transactionsHtml);
        }
    });

    // Load recent incomes
    $.ajax({
        url: "/get_recent_incomes",
        type: "GET",
        success: function(incomes) {
            let transactionsHtml = $("#recentTransactions").html();
            incomes.forEach(function(income) {
                transactionsHtml += `
                    <tr>
                        <td>${income.date}</td>
                        <td><span class="badge bg-success">درآمد</span></td>
                        <td>${income.category}</td>
                        <td>${formatNumber(income.amount)} تومان</td>
                        <td>${income.description || "-"}</td>
                        <td>
                            <button class="btn btn-sm btn-danger" onclick="deleteIncome(${income.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });
            $("#recentTransactions").html(transactionsHtml);
        }
    });
}

function deleteExpense(expenseId) {
    if (confirm("آیا از حذف این هزینه مطمئن هستید؟")) {
        $.ajax({
            url: `/detail/${expenseId}`,
            type: "DELETE",
            success: function(response) {
                alert(response.message);
                loadRecentTransactions();
            },
            error: function(xhr) {
                alert("خطا در حذف هزینه: " + xhr.responseJSON.message);
            }
        });
    }
}

function deleteIncome(incomeId) {
    if (confirm("آیا از حذف این درآمد مطمئن هستید؟")) {
        $.ajax({
            url: `/income-detail/${incomeId}`,
            type: "DELETE",
            success: function(response) {
                alert(response.message);
                loadRecentTransactions();
            },
            error: function(xhr) {
                alert("خطا در حذف درآمد: " + xhr.responseJSON.message);
            }
        });
    }
}

// Show modal functions
function showAddExpenseCategoryModal() {
    $("#addExpenseCategoryModal").modal('show');
}

function showAddIncomeCategoryModal() {
    $("#addIncomeCategoryModal").modal('show');
}