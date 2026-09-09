document.addEventListener('DOMContentLoaded', function() {

    // ===== Mobile Menu Toggle =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navbarNav = document.getElementById('navbarNav');

    if (mobileMenuBtn && navbarNav) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenuBtn.classList.toggle('active');
            navbarNav.classList.toggle('active');
        });

        // Close mobile menu when clicking a link
        const navLinks = navbarNav.querySelectorAll('a');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth <= 768) {
                    mobileMenuBtn.classList.remove('active');
                    navbarNav.classList.remove('active');
                }
            });
        });
    }

    // ===== Close mobile menu on resize =====
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && mobileMenuBtn && navbarNav) {
            mobileMenuBtn.classList.remove('active');
            navbarNav.classList.remove('active');
        }
    });

    // ===== CSRF Token for AJAX =====
    function getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        // Fallback: try cookie
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('csrftoken=')) {
                return decodeURIComponent(cookie.substring('csrftoken='.length));
            }
        }
        return '';
    }

    function sendAjax(url, data, method) {
        method = method || 'POST';
        return fetch(url, {
            method: method,
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            credentials: 'same-origin',
            body: data
        });
    }

    // ===== Cart Quantity Controls =====
    const qtyButtons = document.querySelectorAll('.qty-btn');
    const qtyInputs = document.querySelectorAll('.qty-input');

    qtyButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const stock = parseInt(this.getAttribute('data-stock'));
            const price = parseFloat(this.getAttribute('data-price'));
            const delta = this.classList.contains('plus') ? 1 : -1;
            const input = this.parentNode.querySelector('.qty-input');
            let currentValue = parseInt(input.value);
            let newValue = currentValue + delta;

            if (newValue < 1) {
                newValue = 1;
            }
            if (newValue > stock) {
                newValue = stock;
            }

            if (newValue === currentValue) {
                return;
            }

            input.value = newValue;

            // Send AJAX update
            const formData = new URLSearchParams();
            formData.append('quantity', newValue);

            sendAjax(`/cart/update/${itemId}/`, formData.toString())
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        updateCartTotals(data);
                    } else {
                        alert(data.message);
                        input.value = currentValue;
                    }
                })
                .catch(function(err) {
                    console.error('Cart update error:', err);
                    input.value = currentValue;
                });
        });
    });

    // Handle manual input change on quantity
    qtyInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const stock = parseInt(this.getAttribute('data-stock'));
            let value = parseInt(this.value);

            if (isNaN(value) || value < 1) {
                value = 1;
            }
            if (value > stock) {
                value = stock;
            }
            this.value = value;

            // Send AJAX update
            const formData = new URLSearchParams();
            formData.append('quantity', value);

            sendAjax(`/cart/update/${itemId}/`, formData.toString())
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    if (data.success) {
                        updateCartTotals(data);
                    } else {
                        alert(data.message);
                    }
                })
                .catch(function(err) {
                    console.error('Cart update error:', err);
                });
        });
    });

    function updateCartTotals(data) {
        // Update item total
        const row = document.querySelector(`tr.cart-item[data-item-id="${data.item_id || ''}"]`);

        // Update all item totals
        const rows = document.querySelectorAll('tr.cart-item');
        rows.forEach(function(row) {
            const priceCell = row.querySelector('td.cart-price');
            const qtyInput = row.querySelector('.qty-input');
            if (priceCell && qtyInput) {
                const price = parseFloat(priceCell.textContent.replace('$', ''));
                const qty = parseInt(qtyInput.value);
                const itemTotal = (price * qty).toFixed(2);
                const totalCell = row.querySelector('.item-total');
                if (totalCell) {
                    totalCell.textContent = '$' + itemTotal;
                }
            }
        });

        // Update cart subtotal and grand total
        const subtotalElement = document.querySelector('.cart-subtotal span:last-child');
        const grandTotalElement = document.querySelector('.cart-grand-total span:last-child');

        if (data.cart_total !== undefined) {
            if (subtotalElement) subtotalElement.textContent = '$' + data.cart_total.toFixed(2);
            if (grandTotalElement) grandTotalElement.textContent = '$' + data.cart_total.toFixed(2);
        }

        // Update cart count in navbar
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement && data.cart_count !== undefined) {
            cartCountElement.textContent = '(' + data.cart_count + ')';
        }
    }

    // ===== Remove Item Confirmation =====
    window.confirmRemove = function() {
        return confirm('Are you sure you want to remove this item from your cart?');
    };

    // ===== Message Close Button =====
    window.removeMessage = function(button) {
        const message = button.closest('.message');
        if (message) {
            message.style.display = 'none';
            setTimeout(function() {
                message.remove();
            }, 300);
        }
    };

    // ===== Auto-hide messages after 5 seconds =====
    const messages = document.querySelectorAll('.message');
    messages.forEach(function(msg) {
        setTimeout(function() {
            if (msg.style.display !== 'none') {
                msg.style.display = 'none';
                setTimeout(function() {
                    msg.remove();
                }, 300);
            }
        }, 5000);
    });

    // ===== Registration Form Validation =====
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password1 = document.getElementById('id_password1');
            const password2 = document.getElementById('id_password2');

            if (password1 && password2) {
                if (password1.value !== password2.value) {
                    e.preventDefault();
                    alert('Passwords do not match. Please try again.');
                    return false;
                }
                if (password1.value.length < 8) {
                    e.preventDefault();
                    alert('Password must be at least 8 characters long.');
                    return false;
                }
            }
        });
    }

    // ===== Search Form Enhancement =====
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(function() {
                    // Could add live search here
                }, 300);
            });
        }
    }

    // ===== Loading States =====
    function showLoading(element) {
        if (element) {
            element.classList.add('loading');
            element.setAttribute('disabled', 'true');
        }
    }

    function hideLoading(element, originalText) {
        if (element) {
            element.classList.remove('loading');
            element.removeAttribute('disabled');
        }
    }

    // ===== Add to Cart Button Loading State =====
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.setAttribute('data-original-text', submitBtn.textContent);
                submitBtn.textContent = 'Adding...';
                submitBtn.disabled = true;
            }
        });
    });

});
