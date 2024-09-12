document.addEventListener('DOMContentLoaded', function() {
    const createWatchlistForm = document.getElementById('create-watchlist-form');
    const addToWatchlistForms = document.querySelectorAll('.add-to-watchlist-form');
    const removeFromWatchlistForms = document.querySelectorAll('.remove-from-watchlist-form');
    const removeWatchlistForms = document.querySelectorAll('.remove-watchlist-form');

    if (createWatchlistForm) {
        createWatchlistForm.addEventListener('submit', handleCreateWatchlist);
    }

    addToWatchlistForms.forEach(form => form.addEventListener('submit', handleAddToWatchlist));

    // Use event delegation for dynamically added elements
    document.body.addEventListener('click', function(e) {
        if (e.target && e.target.closest('.remove-from-watchlist-form')) {
            e.preventDefault();
            handleRemoveFromWatchlist(e.target.closest('.remove-from-watchlist-form'));
        }
    });

    removeWatchlistForms.forEach(form => form.addEventListener('submit', handleRemoveWatchlist));

    // Use setTimeout to ensure the DOM is fully rendered
    setTimeout(updateStockData, 100);
});

function handleCreateWatchlist(e) {
    e.preventDefault();
    const formData = new FormData(this);
    fetchRequest('/create-watchlist/', formData)
        .then(data => {
            if (data.success) {
                location.reload(); // Reload the page to show the new watchlist
            }
        });
}

function handleAddToWatchlist(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const watchlistId = data.watchlist.id;
            const watchlistUl = document.querySelector(`#watchlist-${watchlistId}`);
            if (watchlistUl) {
                const emptyMessage = watchlistUl.querySelector('li:only-child');
                if (emptyMessage && emptyMessage.textContent.trim() === 'This watchlist is empty.') {
                    emptyMessage.remove();
                }
                
                const newStockLi = document.createElement('li');
                newStockLi.id = `stock-${data.stock.id}-watchlist-${watchlistId}`;
                newStockLi.innerHTML = `
                    ${data.stock.ticker} - Close: <span class="stock-close">${data.stock.close}</span>
                    - 5d: <span class="stock-5d">${data.stock.d5 || 'N/A'}</span>
                    - 10d: <span class="stock-10d">${data.stock.d10 || 'N/A'}</span>
                    - 15d: <span class="stock-15d">${data.stock.d15 || 'N/A'}</span>
                    <form class="remove-from-watchlist-form" action="/remove-from-watchlist/${watchlistId}/${data.stock.id}/" method="post">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${formData.get('csrfmiddlewaretoken')}">
                        <button type="submit" data-stock-id="${data.stock.id}" data-watchlist-id="${watchlistId}">Remove from Watchlist</button>
                    </form>
                `;
                watchlistUl.appendChild(newStockLi);
            }
            alert(data.message);
        } else {
            alert(data.message || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while adding the stock to the watchlist.');
    });
}

function handleRemoveFromWatchlist(form) {
    const formData = new FormData(form);
    const url = form.action;
    const stock_id = form.querySelector('button').dataset.stockId;
    const watchlist_id = form.querySelector('button').dataset.watchlistId;

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const stockElement = document.querySelector(`#stock-${data.stock_id}-watchlist-${data.watchlist_id}`);
            if (stockElement) {
                stockElement.remove();
                console.log(`Removed stock ${data.stock_ticker} from watchlist ${data.watchlist_id}`);
                
                const watchlistUl = document.querySelector(`#watchlist-${data.watchlist_id}`);
                if (watchlistUl && watchlistUl.children.length === 0) {
                    watchlistUl.innerHTML = '<li>This watchlist is empty.</li>';
                }
            } else {
                console.error(`Could not find element #stock-${data.stock_id}-watchlist-${data.watchlist_id}`);
            }
        } else {
            console.error('Error removing stock:', data.error);
            alert(data.error || 'An error occurred while removing the stock from the watchlist.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while removing the stock from the watchlist.');
    });
}

function handleRemoveWatchlist(e) {
    e.preventDefault();
    const watchlistId = this.querySelector('button').dataset.watchlistId;
    fetchRequest(this.action)
        .then(data => {
            if (data.success) {
                document.querySelector(`#watchlist-container-${watchlistId}`).remove();
            } else {
                alert(data.error || 'An error occurred while removing the watchlist.');
            }
        });
}

function fetchRequest(url, formData = null) {
    const options = {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
    };

    if (formData) {
        options.body = formData;
    }

    return fetch(url, options)
        .then(response => response.json())
        .catch(error => {
            console.error('Fetch error:', error);
            alert('An error occurred while sending the request.');
        });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateStockData() {
    console.log('Fetching latest stock data...');
    fetch('/api/get_latest_stock_data/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received stock data:', data);
            data.forEach(stock => {
                const stockElements = document.querySelectorAll(`[id^="stock-${stock.id}-watchlist-"]`);
                console.log(`Updating ${stockElements.length} elements for stock ${stock.id}`);
                stockElements.forEach(element => {
                    element.querySelector('.stock-close').textContent = stock.close;
                    element.querySelector('.stock-5d').textContent = stock.d5;
                    element.querySelector('.stock-10d').textContent = stock.d10;
                    element.querySelector('.stock-15d').textContent = stock.d15;
                });
            });
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
        });
}

// Call updateStockData when the page loads
document.addEventListener('DOMContentLoaded', function() {
    updateStockData();
    // Optionally, set up periodic updates
    setInterval(updateStockData, 60000); // Update every minute
});
