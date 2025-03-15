// Format numbers with thousands separator
function formatNumber(number) {
    return new Intl.NumberFormat('fa-IR').format(number);
}

// Format currency with تومان and thousands separator
function formatCurrency(amount) {
    return formatNumber(amount) + ' تومان';
}

// Remove formatting to get raw number
function unformatNumber(formattedNumber) {
    return formattedNumber.replace(/,/g, '');
} 