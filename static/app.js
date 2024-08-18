document.addEventListener('DOMContentLoaded', function() {
    const materialForm = document.getElementById('material-form');
    const materialsList = document.getElementById('materials');
    const stockForm = document.getElementById('stock-form');
    const materialSelect = document.getElementById('material-select');
    const withdrawForm = document.getElementById('withdraw-form');
    const withdrawMaterialSelect = document.getElementById('withdraw-material-select');
    const stockCheckForm = document.getElementById('stock-check-form');
    const stockMaterialSelect = document.getElementById('stock-material-select');
    const stockResult = document.getElementById('stock-result');

    const reportForm = document.getElementById('report-form');
    const reportResult = document.getElementById('report-result');
    const listAllStockButton = document.getElementById('list-all-stock');
    const allStockResult = document.getElementById('all-stock-result');

    // Malzeme ekleme işlevi
    materialForm.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const name = document.getElementById('name').value;
        const description = document.getElementById('description').value;
        const initial_stock = document.getElementById('initial_stock').value;
        const unit = document.getElementById('unit').value;

        fetch('/materials', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                description: description,
                initial_stock: parseInt(initial_stock),
                unit: unit  // Birimi gönderiyoruz
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Malzeme eklendi!');
            loadMaterials();
        })
        .catch(error => console.error('Error:', error));
    });

    // Mevcut malzemeleri yükleme
    function loadMaterials() {
        fetch('/materials')
        .then(response => response.json())
        .then(data => {
            materialsList.innerHTML = '';
            materialSelect.innerHTML = '';
            withdrawMaterialSelect.innerHTML = '';
            stockMaterialSelect.innerHTML = '';
            data.forEach(material => {
                const li = document.createElement('li');
                li.textContent = `${material.name} - ${material.description} (Stok: ${material.initial_stock} ${material.unit})`;  // Birimi gösteriyoruz
                materialsList.appendChild(li);

                const option = document.createElement('option');
                option.value = material.id;
                option.textContent = `${material.name} (${material.unit})`;  // Birimi ekrana getiriyoruz
                materialSelect.appendChild(option);

                const withdrawOption = document.createElement('option');
                withdrawOption.value = material.id;
                withdrawOption.textContent = `${material.name} (${material.unit})`;
                withdrawMaterialSelect.appendChild(withdrawOption);

                const stockOption = document.createElement('option');
                stockOption.value = material.id;
                stockOption.textContent = `${material.name} (${material.unit})`;
                stockMaterialSelect.appendChild(stockOption);
            });
        })
        .catch(error => console.error('Error:', error));
    }

    // Stok kaydı ekleme işlevi
    stockForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const material_id = materialSelect.value;
        const date = document.getElementById('date').value;
        const produced = document.getElementById('produced').value;
        const sold = document.getElementById('sold').value;

        fetch('/stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                material_id: parseInt(material_id),
                date: date,
                produced: parseInt(produced),
                sold: parseInt(sold)
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Stok kaydı eklendi!');
            loadMaterials();
        })
        .catch(error => console.error('Error:', error));
    });

    // Stoktan malzeme çıkışı yapma işlevi
    withdrawForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const material_id = withdrawMaterialSelect.value;
        const quantity = document.getElementById('quantity').value;

        fetch('/stock/withdraw', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                material_id: parseInt(material_id),
                quantity: parseInt(quantity)
            })
        })
        .then(response => response.json())
        .then(data => {
            alert('Stoktan malzeme çıkışı yapıldı!');
            loadMaterials();
        })
        .catch(error => console.error('Error:', error));
    });

    // Güncel stok durumunu görüntüleme işlevi
    stockCheckForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const material_id = stockMaterialSelect.value;

        fetch(`/stock/${material_id}`)
        .then(response => response.json())
        .then(data => {
            stockResult.textContent = `${data.material} - Güncel Stok: ${data.current_stock}`;
        })
        .catch(error => console.error('Error:', error));
    });

    // Tarih aralığında üretilen ve satılan malzemeleri gösterme
    reportForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const startDate = document.getElementById('start_date').value;
        const endDate = document.getElementById('end_date').value;

        fetch(`/report?start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            reportResult.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name} - Üretilen: ${item.total_produced} ${item.unit}, Satılan: ${item.total_sold} ${item.unit}`;
                reportResult.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
    });

    // Stoktaki tüm malzemeleri listeleme
    listAllStockButton.addEventListener('click', function() {
        fetch('/stock/all')
        .then(response => response.json())
        .then(data => {
            allStockResult.innerHTML = '';
            data.forEach(item => {
                const li = document.createElement('li');
                li.textContent = `${item.name} - Mevcut Stok: ${item.current_stock} ${item.unit}`;
                allStockResult.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
    });

    loadMaterials();
});
