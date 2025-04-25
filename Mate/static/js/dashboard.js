// Function to load today's expenses
function loadTodayExpenses() {
    console.log('Loading today expenses...');
    fetch('/today_expenses')
        .then(response => response.json())
        .then(expenses => {
            console.log('Received expenses:', expenses);
            const tbody = document.getElementById('todayExpensesList');
            console.log('Found tbody element:', tbody);

            if (!tbody) {
                console.error('Could not find todayExpensesList element');
                return;
            }

            tbody.innerHTML = '';

            if (!expenses || expenses.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">هیچ هزینه‌ای برای امروز ثبت نشده است.</td></tr>';
                return;
            }

            expenses.forEach(expense => {
                console.log('Processing expense:', expense);
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${expense.category || '-'}</td>
                    <td>${new Intl.NumberFormat('fa-IR').format(expense.amount)} تومان</td>
                    <td>${expense.description || '-'}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="deleteExpense(${expense.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            console.log('Finished loading expenses');
        })
        .catch(error => {
            console.error('Error loading today expenses:', error);
            const tbody = document.getElementById('todayExpensesList');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-danger text-center">خطا در بارگذاری هزینه‌های امروز</td></tr>';
            }
        });
}

// Function to load today's incomes
function loadTodayIncomes() {
    console.log('Loading today incomes...');
    fetch('/today_incomes')
        .then(response => response.json())
        .then(incomes => {
            console.log('Received incomes:', incomes);
            const tbody = document.getElementById('todayIncomesList');
            console.log('Found tbody element:', tbody);

            if (!tbody) {
                console.error('Could not find todayIncomesList element');
                return;
            }

            tbody.innerHTML = '';

            if (!incomes || incomes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-center">هیچ درآمدی برای امروز ثبت نشده است.</td></tr>';
                return;
            }

            incomes.forEach(income => {
                console.log('Processing income:', income);
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${income.category || '-'}</td>
                    <td>${new Intl.NumberFormat('fa-IR').format(income.amount)} تومان</td>
                    <td>${income.description || '-'}</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="deleteIncome(${income.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            console.log('Finished loading incomes');
        })
        .catch(error => {
            console.error('Error loading today incomes:', error);
            const tbody = document.getElementById('todayIncomesList');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="4" class="text-danger text-center">خطا در بارگذاری درآمدهای امروز</td></tr>';
            }
        });
}

// Add event listeners for the modals
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded');
    const todayExpensesModal = document.getElementById('todayExpensesModal');
    console.log('Found todayExpensesModal:', todayExpensesModal);

    if (todayExpensesModal) {
        todayExpensesModal.addEventListener('show.bs.modal', function() {
            console.log('Today expenses modal shown');
            loadTodayExpenses();
        });
    }

    const todayIncomesModal = document.getElementById('todayIncomesModal');
    console.log('Found todayIncomesModal:', todayIncomesModal);

    if (todayIncomesModal) {
        todayIncomesModal.addEventListener('show.bs.modal', function() {
            console.log('Today incomes modal shown');
            loadTodayIncomes();
        });
    }
});