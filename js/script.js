// Home page js

document.addEventListener('DOMContentLoaded', () => {
  // CATEGORY buttons
  // CATEGORY filter logic
  const categoryButtons = document.querySelectorAll('.category-btn');
  const productCards = document.querySelectorAll('.pro');
  const categoryTitle = document.querySelector('.product1-title');

  categoryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      // Remove active from all, set active on clicked
      categoryButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update title
      if (categoryTitle) categoryTitle.textContent = btn.textContent.trim();

      // Get selected category
      const selected = btn.dataset.category;

      // Show/hide products
      productCards.forEach(card => {
        const span = card.querySelector('.des span');
        const cardCategory = span ? span.textContent.trim().toLowerCase().replace(/\s+/g, '-') : '';
        if (!selected || selected === '' || cardCategory === selected) {
          card.style.display = '';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  const STORAGE_KEY = 'vb_cart'
  const headerCountEl = document.querySelector('a.cart-btn .cart-count')

  // CART functionality
  const readCart = () => JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  const saveCart = (cart) => localStorage.setItem(STORAGE_KEY, JSON.stringify(cart))

  const updateHeaderCount = () => {
    const cart = readCart()
    const total = cart.reduce((s, item) => s + (item.qty || 1), 0)
    if (headerCountEl) headerCountEl.textContent = total
    if (headerCountEl) {
      headerCountEl.classList.add('cart-updated')
      setTimeout(() => headerCountEl.classList.remove('cart-updated'), 300)
    }
  }

  const addToCart = (product) => {
    const cart = readCart()
    const idx = cart.findIndex(i => i.id === product.id)
    if (idx > -1) {
      cart[idx].qty = (cart[idx].qty || 1) + (product.qty || 1)
    } else {
      cart.push(Object.assign({ qty: 1 }, product))
    }
    saveCart(cart)
    updateHeaderCount()
  }

  // ...existing code...
  document.querySelectorAll('.pro a').forEach(a => {
    if (!a.querySelector('.cart')) return
    a.addEventListener('click', (e) => {
      e.preventDefault()
      const pro = a.closest('.pro')
      if (!pro) return
      const id = pro.id || pro.dataset.id || (pro.querySelector('h5')?.textContent.trim()) || Date.now().toString()
      const title = pro.querySelector('.des h5')?.textContent.trim() || ''
      const price = pro.querySelector('.des h4')?.textContent.trim() || ''
      const img = pro.querySelector('img')?.getAttribute('src') || '';
      addToCart({ id, title, price, img, qty: 1 });
    })
  })

  // init
  updateHeaderCount()
})