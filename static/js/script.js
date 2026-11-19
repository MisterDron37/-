function calculateRenralPrice(){
    const start = new Date(
        document.getElementById('start_date').value
    );

    const end = new Date(
        document.getElementById('end_date').value
    );

    const price = Number(
        document.getElementById('price').value
    );

    if (
        isNaN(start.getTime()) ||
        isNaN(end.getTime()) ||
        start >= end ||
        !Number.isFinite(price) ||
        price < 0
    ) {
        document.getElementById('total').textContent = 'Проверьте введенные данные';
        return;
    }
    
    const days = Msth.round(
        (end - start) / (1000 * 60 * 60 * 24)
    );

    const total = days * price;

document.getElementById('total').textContent = 'Стоимость аренды: ' + total + 'руб.';
}