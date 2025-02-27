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

                    response.report.forEach(function(item) {
                        let percentage = (item.total_amount / totalCosts * 100).toFixed(2);
                        reportHtml += `
                            <tr class="category-row">
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
                        <tr>
                            <td>${exp.amount}</td>
                            <td>${exp.description || "ندارد"}</td>
                            <td>${exp.date}</td>
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
