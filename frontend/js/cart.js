document.addEventListener('DOMContentLoaded', function () {
  const STORAGE_KEY = 'vb_cart';
  const cartRow = document.querySelector('.cart-row');
  const totalEl = document.querySelector('.col2 h4 strong');

  function readCart() {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  }

  function saveCart(cart) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
  }

  function removeItem(id) {
    let cart = readCart();
    cart = cart.filter(item => item.id !== id);
    saveCart(cart);
    renderCart();
  }

  function updateQty(id, delta) {
    let cart = readCart();
    cart = cart.map(item => {
      if (item.id === id) {
        item.qty = Math.max(1, (item.qty || 1) + delta);
      }
      return item;
    });
    saveCart(cart);
    renderCart();
  }

  function renderCart() {
    const cart = readCart();
    cartRow.innerHTML = '';
    let total = 0;
    if (cart.length === 0) {
      cartRow.innerHTML = '<div class="empty-cart-message">The cart is empty</div>';
      if (totalEl) totalEl.textContent = '$0.00';
      return;
    }
    cart.forEach(item => {
      const priceNum = parseFloat(item.price.replace(/[^0-9.]/g, '')) || 0;
      total += priceNum * (item.qty || 1);
      const cartItem = document.createElement('div');
      cartItem.className = 'cart-item';
      cartItem.innerHTML = `
        <img src="${item.img.startsWith('assets/') ? '../' + item.img : item.img}" alt="${item.title}" />
        <div class="cart-item-details">
          <h3>${item.title}</h3>
          <span>${item.price}</span>
          <div class="cart-item-quantity">
            <button class="qty-btn" type="button" data-id="${item.id}" data-delta="-1">-</button>
            <span class="cart-qty-number">${item.qty}</span>
            <button class="qty-btn" type="button" data-id="${item.id}" data-delta="1">+</button>
          </div>
        </div>
        <button class="remove-btn" data-id="${item.id}">Remove</button>
      `;
      cartRow.appendChild(cartItem);
    });

    // Quantity buttons
    cartRow.querySelectorAll('.qty-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        updateQty(btn.dataset.id, parseInt(btn.dataset.delta));
      });
    });

    // Remove buttons
    cartRow.querySelectorAll('.remove-btn').forEach(btn => {
      btn.addEventListener('click', function () {
        removeItem(btn.dataset.id);
      });
    });

    if (totalEl) totalEl.textContent = `$${total.toFixed(2)}`;
  }

  renderCart();
});
