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
                    incomeHtml += '<thead><tr><th>دسته‌بندی</th><th>مجموع درآمد</th><th>درصد از کل</th></tr></thead><tbody>';

                    response.income_report.forEach(function(item) {
                        let percentage = (item.total_amount / totalIncome * 100).toFixed(2);
                        incomeHtml += `
                            <tr class="category-row">
                                <td class="category-name">${item.category_name}</td>
                                <td>${item.total_amount}</td>
                                <td class="percentage">${percentage}%</td>
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
            row.remove(); // حذف ردیف از جدول
        },
        error: function(xhr) {
            alert("خطا در حذف هزینه: " + xhr.responseJSON.message);
        }
    });
});