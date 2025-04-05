$(document).ready(function() {
    // دریافت گزارش هزینه‌ها
    $("#filterBtn").click(function() {
        $.ajax({
            url: "/get_all_report",
            type: "GET",
            contentType: "application/json",
            data: JSON.stringify({}),
            success: function(response) {
                if (response.success) {
                    let totalCosts = response.total_costs;
                    let reportHtml = '<table class="table report-table costs table-bordered">';
                    reportHtml += '<thead><tr><th>دسته‌بندی</th><th>مجموع هزینه</th><th>درصد از کل</th></tr></thead><tbody>';

                    // Find the highest percentage for highlighting
                    let maxPercentage = Math.max(...response.report.map(item =>
                        (item.total_amount / totalCosts * 100)
                    ));

                    response.report.forEach(function(item) {
                        let percentage = (item.total_amount / totalCosts * 100).toFixed(2);
                        let rowClass = '';

                        // Add highlighting classes based on percentage
                        if (percentage >= maxPercentage) {
                            rowClass = 'highest-percentage';
                        } else if (percentage >= 30) {
                            rowClass = 'high-percentage';
                        } else if (percentage >= 15) {
                            rowClass = 'medium-percentage';
                        }

                        reportHtml += `
                            <tr class="category-row ${rowClass}">
                                <td class="category-name">${item.category_name}</td>
                                <td>${item.total_amount}</td>
                                <td class="percentage">${percentage}%</td>
                                <td><button class="btn btn-info btn-sm details-btn" data-category-id="${item.category_id}">جزئیات</button></td>
                            </tr>
                        `;
                    });

                    reportHtml += '</tbody></table>';
                    $("#totalCosts").text(totalCosts).addClass("total-costs");
                    $("#reportSection").html(reportHtml);

                    // Add CSS styles for highlighting
                    const styles = `
                        <style>
                            .highest-percentage {
                                background-color: rgba(255, 0, 0, 0.2) !important;
                                font-weight: bold;
                            }
                            .high-percentage {
                                background-color: rgba(255, 165, 0, 0.2) !important;
                            }
                            .medium-percentage {
                                background-color: rgba(255, 255, 0, 0.1) !important;
                            }
                        </style>
                    `;
                    if (!$('style:contains("highest-percentage")').length) {
                        $('head').append(styles);
                    }
                } else {
                    $("#reportSection").html('<p>هیچ گزارشی موجود نیست.</p>');
                }
            },
            error: function(xhr, status, error) {
                alert("مشکلی در دریافت گزارش پیش آمده است.");
            }
        });
    });

    // دریافت گزارش درآمدها
    $("#incomeBtn").click(function() {
        fetchIncome();
    });

    function fetchIncome() {
        $.ajax({
            url: "/get_income_report",
            type: "GET",
            contentType: "application/json",
            data: JSON.stringify({}),
            success: function(response) {
                if (response.success) {
                    let totalIncome = response.total_income;
                    let incomeHtml = '<table class="table report-table income table-bordered">';
                    incomeHtml += '<thead><tr><th>دسته‌بندی</th><th>مجموع درآمد</th><th>درصد از کل</th><th>عملیات</th></tr></thead><tbody>';

                    response.income_report.forEach(function(item) {
                        let percentage = (item.total_amount / totalIncome * 100).toFixed(2);
                        incomeHtml += `
                            <tr class="category-row">
                                <td class="category-id">${item.category_id}</td>
                                <td class="category-name">${item.category_name}</td>
                                <td>${item.total_amount}</td>
                                <td class="percentage">${percentage}%</td>
                                <td><button class="btn btn-info btn-sm income-details-btn" data-category-id="${item.category_id}">جزئیات</button></td>
                            </tr>
                        `;
                    });

                    incomeHtml += '</tbody></table>';
                    $("#totalIncoms").text(totalIncome).addClass("total-incomes");
                    $("#reportSection").html(incomeHtml);
                } else {
                    $("#reportSection").html('<p>هیچ گزارشی برای درآمد موجود نیست.</p>');
                }
            },
            error: function(xhr, status, error) {
                alert("مشکلی در دریافت گزارش درآمد پیش آمده است.");
            }
        });
    }
});
$(document).on("click", ".details-btn", function() {
    let categoryId = $(this).data("category-id");

    $.ajax({
        url: `/expenses/${categoryId}`,
        type: "GET",
        contentType: "application/json",
        success: function(response) {
            if (response.success) {
                let detailsHtml = "";
                response.expenses.forEach(function(exp) {
                    detailsHtml += `
                        <tr data-id="${exp.id}">
                            <td>${exp.amount}</td>
                            <td>${exp.description || "ندارد"}</td>
                            <td>${exp.date}</td>
                            <td>
                                <button class="btn btn-danger delete-expense" data-id="${exp.id}">حذف</button>
                            </td>
                        </tr>
                    `;
                });

                $("#expenseDetailsBody").html(detailsHtml);
                let modal = new bootstrap.Modal(document.getElementById("expenseDetailsModal"));
                modal.show();
            } else {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
            alert("مشکلی در دریافت جزئیات هزینه پیش آمد.");
        }
    });
});

$(document).on("click", ".delete-expense", function() {
    let expenseId = $(this).data("id");
    let row = $(this).closest("tr");

    if (!confirm("آیا از حذف این هزینه مطمئن هستید؟")) {
        return;
    }

    $.ajax({
        url: `/detail/${expenseId}`,
        type: "DELETE",
        success: function(response) {
            alert(response.message);
            row.remove();
        },
        error: function(xhr) {
            alert("خطا در حذف هزینه: " + xhr.responseJSON.message);
        }
    });
});

// Add details button to income rows
function updateIncomeTable(response, totalIncome) {
    let incomeHtml = '<table class="table report-table income table-bordered">';
    incomeHtml += '<thead><tr><th>دسته‌بندی</th><th>مجموع درآمد</th><th>درصد از کل</th><th>عملیات</th></tr></thead><tbody>';

    response.income_report.forEach(function(item) {
        let percentage = (item.total_amount / totalIncome * 100).toFixed(2);
        incomeHtml += `
            <tr class="category-row">
                <td class="category-name">${item.category_name}</td>
                <td>${item.total_amount}</td>
                <td class="percentage">${percentage}%</td>
                <td><button class="btn btn-info btn-sm income-details-btn" data-category-id="${item.category_id}">جزئیات</button></td>
            </tr>
        `;
    });

    incomeHtml += '</tbody></table>';
    return incomeHtml;
}

// Handle income details button click
$(document).on("click", ".income-details-btn", function() {
    console.log($(this).data());
    let categoryId = $(this).data("categoryId");

    $.ajax({
        url: `/incomes/${categoryId}`,
        type: "GET",
        contentType: "application/json",
        success: function(response) {
            if (response.success) {
                let detailsHtml = "";
                response.incomes.forEach(function(inc) {
                    detailsHtml += `
                        <tr data-id="${inc.id}">
                            <td>${inc.amount}</td>
                            <td>${inc.description || "ندارد"}</td>
                            <td>${inc.date}</td>
                            <td>
                                <button class="btn btn-danger delete-income" data-id="${inc.id}">حذف</button>
                            </td>
                        </tr>
                    `;
                });

                $("#incomeDetailsBody").html(detailsHtml);
                let modal = new bootstrap.Modal(document.getElementById("incomeDetailsModal"));
                modal.show();
            } else {
                alert(response.message);
            }
        },
        error: function(xhr, status, error) {
            alert("مشکلی در دریافت جزئیات درآمد پیش آمد.");
        }
    });
});

// Handle income deletion
$(document).on("click", ".delete-income", function() {
    let incomeId = $(this).data("id");
    let row = $(this).closest("tr");

    if (!confirm("آیا از حذف این درآمد مطمئن هستید؟")) {
        return;
    }

    $.ajax({
        url: `/income-detail/${incomeId}`,
        type: "DELETE",
        success: function(response) {
            alert(response.message);
            row.remove();
        },
        error: function(xhr) {
            alert("خطا در حذف درآمد: " + xhr.responseJSON.message);
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    // تعریف متغیرهای گلوبال
    let expenseChart = null;
    const persianMonths = [
        'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
        'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
    ];

    // تنظیم اولیه صفحه
    function initializePage() {
        loadCategories();
        setupYearSelect();
        setupEventListeners();
    }

    // بارگذاری دسته‌بندی‌ها
    function loadCategories() {
        const categorySelect = document.getElementById('categorySelect');
        categorySelect.innerHTML = '<option value="">در حال بارگذاری...</option>';
        categorySelect.disabled = true;

        fetch('/get_categories')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    categorySelect.innerHTML = '<option value="">انتخاب کنید</option>';
                    data.categories.forEach(category => {
                        const option = document.createElement('option');
                        option.value = category.id;
                        option.textContent = category.name;
                        categorySelect.appendChild(option);
                    });
                } else {
                    throw new Error(data.message || 'خطا در دریافت لیست دسته‌بندی‌ها');
                }
            })
            .catch(error => {
                console.error('Error loading categories:', error);
                categorySelect.innerHTML = '<option value="">خطا در بارگذاری</option>';
            })
            .finally(() => {
                categorySelect.disabled = false;
            });
    }

    // تنظیم سال‌ها
    function setupYearSelect() {
        const yearSelect = document.getElementById('yearSelect');

        // تبدیل تاریخ میلادی به شمسی
        const today = new Date();
        const persianDate = new Intl.DateTimeFormat('fa-IR', {
            year: 'numeric'
        }).format(today);

        // تبدیل عدد فارسی به انگلیسی
        const currentYear = parseInt(persianDate.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)));

        yearSelect.innerHTML = '<option value="">انتخاب کنید</option>';

        // اضافه کردن 3 سال اخیر
        for (let year = currentYear; year >= currentYear - 2; year--) {
            const option = document.createElement('option');
            option.value = year;
            // تبدیل عدد به فارسی برای نمایش بدون جداکننده
            const persianYear = year.toString().replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹' [d]);
            option.textContent = persianYear;
            yearSelect.appendChild(option);
        }
    }

    // تنظیم event listeners
    function setupEventListeners() {
        document.getElementById('generateReport').addEventListener('click', generateReport);
    }

    // تولید گزارش
    function generateReport() {
        const categoryId = document.getElementById('categorySelect').value;
        const year = document.getElementById('yearSelect').value;

        if (!categoryId || !year) {
            alert('لطفاً دسته‌بندی و سال را انتخاب کنید');
            return;
        }

        showLoading(true);
        fetch(`/category_yearly_report?category_id=${categoryId}&year=${year}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateChart(data.monthly_data);
                    updateStats(data.stats);
                    updateTable(data.monthly_data);
                    showReportSections(true);
                } else {
                    throw new Error(data.message || 'خطا در دریافت اطلاعات');
                }
            })
            .catch(error => {
                console.error('Error generating report:', error);
                alert('خطا در دریافت اطلاعات: ' + error.message);
            })
            .finally(() => {
                showLoading(false);
            });
    }

    // به‌روزرسانی نمودار
    function updateChart(monthlyData) {
        const ctx = document.getElementById('expenseChart').getContext('2d');

        if (expenseChart) {
            expenseChart.destroy();
        }

        const amounts = new Array(12).fill(0);
        monthlyData.forEach(data => {
            amounts[data.month - 1] = data.amount;
        });

        expenseChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: persianMonths,
                datasets: [{
                    label: 'مبلغ هزینه (تومان)',
                    data: amounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return new Intl.NumberFormat('fa-IR').format(value) + ' تومان';
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return new Intl.NumberFormat('fa-IR').format(context.raw) + ' تومان';
                            }
                        }
                    }
                }
            }
        });
    }

    // به‌روزرسانی آمار
    function updateStats(stats) {
        document.getElementById('totalExpense').textContent =
            new Intl.NumberFormat('fa-IR').format(stats.total_amount) + ' تومان';
        document.getElementById('averageExpense').textContent =
            new Intl.NumberFormat('fa-IR').format(stats.average_monthly) + ' تومان';
        document.getElementById('expensePercentage').textContent =
            new Intl.NumberFormat('fa-IR').format(stats.percentage_of_total) + '%';
    }

    // به‌روزرسانی جدول
    function updateTable(monthlyData) {
        const tableBody = document.getElementById('expenseTable');
        tableBody.innerHTML = '';

        monthlyData.forEach(data => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${persianMonths[data.month - 1]}</td>
                <td>${new Intl.NumberFormat('fa-IR').format(data.amount)} تومان</td>
                <td>${new Intl.NumberFormat('fa-IR').format(data.percentage)}%</td>
                <td>${new Intl.NumberFormat('fa-IR').format(data.transaction_count)}</td>
            `;
            tableBody.appendChild(row);
        });
    }

    // نمایش/مخفی کردن بخش‌های گزارش
    function showReportSections(show) {
        const sections = ['chartSection', 'statsSection', 'tableSection'];
        sections.forEach(id => {
            document.getElementById(id).style.display = show ? 'block' : 'none';
        });
    }

    // نمایش/مخفی کردن لودینگ
    function showLoading(show) {
        document.getElementById('loading').style.display = show ? 'block' : 'none';
    }

    // شروع اجرای اسکریپت
    initializePage();
});