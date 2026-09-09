# ShopSphere - Simple E-commerce Store

CodeAlpha Full Stack Development Internship - Task 1

ShopSphere ek fully functional Django e-commerce website hai. Isme user products browse kar sakta hai, cart me item add kar sakta hai, checkout karke order place kar sakta hai aur order tracking dekh sakta hai.

## Project me kya kya complete hua hai

### User account

- User registration with first name, last name, username, email aur password validation
- Secure login aur logout
- User profile update: name, email, phone aur address details
- Har user sirf apne orders aur cart ko access kar sakta hai

### Products

- Home page me hero section, categories, featured products aur latest products
- Product listing, search, category filter aur pagination
- Product detail page me price, available stock, quantity selector aur Add to Cart button
- Out-of-stock product par Add to Cart disabled rehta hai
- INR (₹) me 8 sample products available hain
- Har sample product ke liye local PNG catalogue image attached hai
- Admin se real product image upload karne par wahi image display hogi

### Shopping cart

- Add to cart, quantity update, item remove aur clear cart
- Cart total aur item subtotal automatic calculate hote hain
- Stock se zyada quantity add/update nahi ho sakti
- Navbar me current cart item count dikhta hai

### Checkout aur orders

- Shipping form ke saath checkout
- Database transaction ke through order create hota hai
- Successful checkout par product stock reduce hota hai aur cart clear hota hai
- My Orders page aur detailed order page
- Users doosre user ke orders nahi dekh sakte

### Order tracking

- Order place hote hi initial Pending tracking event create hota hai
- Customer Track Package page par order timeline dekh sakta hai
- Estimated delivery date dikhti hai
- Admin order status ko Pending, Processing, Shipped, Delivered ya Cancelled me update kar sakta hai
- Admin status update karte hi customer timeline me naya tracking event automatic add hota hai

### Admin panel

- Categories, products, carts aur orders manage karne ke liye Django Admin configured hai
- Product search, filters, stock aur availability controls
- Product image preview
- Order items aur tracking events order ke andar visible hain

## Technology stack

- Python
- Django
- SQLite
- HTML5, CSS3, Bootstrap 5
- Vanilla JavaScript
- Pillow for local catalogue images

## Installation aur run commands

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_store
python manage.py runserver
```

Website: `http://127.0.0.1:8000/`  
Admin panel: `http://127.0.0.1:8000/admin/`

## Local demo mode

```powershell
python manage.py seed_demo
```

Demo login, sample orders aur tracking workflow ke liye [DEMO_GUIDE.md](DEMO_GUIDE.md) dekhein.

`seed_store` command categories, INR sample products aur local product images automatically create karta hai.

Real demo product photos are assigned with `python manage.py assign_real_images`. Their local source record is in [IMAGE_SOURCES.md](IMAGE_SOURCES.md).

## Testing

```powershell
python manage.py check
python manage.py test
```

Tests me cart stock validation, checkout, stock reduction, order privacy aur order tracking check kiya gaya hai.

## Important folders

- `accounts/` - authentication aur profile
- `products/` - products, categories, search aur images
- `cart/` - cart management
- `orders/` - checkout, order history aur tracking
- `templates/` - Django HTML templates
- `static/` - CSS aur JavaScript
- `media/` - uploaded aur generated product images

## Future improvements

- Online payment gateway integration
- Email/SMS order notifications
- Product reviews aur wishlists
- Live courier API integration
- Production deployment settings
