function convertPersianToEnglishNumbers(str) {
    return str.replace(/[۰-۹]/g, function(d) {
        return d.charCodeAt(0) - 1776;
    });
}

$(document).ready(function() {
    $("#date").persianDatepicker({
        format: 'YYYY-MM-DD'
    });

    $("#expenseForm").submit(function(event) {
        event.preventDefault();

        let amount = $("#amount").val().trim();
        let category = $("#category").val();
        let description = $("#description").val().trim();
        let date = $("#date").val().trim();
        date = convertPersianToEnglishNumbers(date);

        if (amount === "" || category === "") {
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
                $("#amount").val("");
                $("#category").val("");
                $("#description").val("");

                let newExpense = response.expense;
                let expenseRow = `<tr>
                    <td>${newExpense.id}</td>
                    <td>${newExpense.amount}</td>
                    <td>${newExpense.category}</td>
                    <td>${newExpense.description}</td>
                    <td>${newExpense.date}</td>
                </tr>`;

                $("#expensesTable tbody").append(expenseRow);
            },
            error: function(xhr, status, error) {
                console.log("Error:", error);
                alert("مشکلی در ثبت هزینه پیش آمده است. لطفاً دوباره تلاش کنید.");
            }
        });
    });

    // ارسال دسته‌بندی هزینه جدید
    $("#categoryForm").submit(function(event) {
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
                $("#categoryModal").modal("hide");
                $("#categoryName").val("");
                $("#category").append(`<option value="${response.category_id}">${response.category_name}</option>`);
            },
            error: function(xhr, status, error) {
                console.log("Error:", xhr.responseText);
                alert("مشکلی در ثبت دسته‌بندی پیش آمده: " + xhr.responseText);
            }
        });
    });

    // ارسال دسته‌بندی درآمد جدید
    $("#incomeCategoryForm").submit(function(event) {
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
                $("#incomeCategoryModal").modal("hide");
                $("#incomeCategoryName").val("");
                $("#incomeCategory").append(`<option value="${response.category_id}">${response.category_name}</option>`);
            },
            error: function(xhr, status, error) {
                alert("مشکلی در ثبت دسته‌بندی درآمد پیش آمده: " + xhr.responseText);
            }
        });
    });

    $("#incomeForm").submit(function(event) {
        event.preventDefault();
        let incomeAmount = $("#incomeAmount").val().trim();
        let incomeCategory = $("#incomeCategory").val();
        let incomeDescription = $("#incomeDescription").val().trim();
        if (incomeAmount === "" || incomeCategory === "") {
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
                incomeDescription: incomeDescription
            }),
            success: function(response) {
                alert(response.message);
                $("#incomeAmount").val("");
                $("#incomeCategory").val("");
                $("#incomeDescription").val("");
                let newIncome = response.income;
                let incomeRow = `<tr>
                    <td>${newIncome.id}</td>
                    <td>${newIncome.amount}</td>
                    <td>${newIncome.category}</td>
                    <td>${newIncome.description}</td>
                    <td>${newIncome.date}</td>
                </tr>`;
                $("#incomeTable tbody").append(incomeRow);
            },
            error: function(xhr, status, error) {
                alert("مشکلی در ثبت درآمد پیش آمده است. لطفاً دوباره تلاش کنید.");
            }
        });
    });
});
