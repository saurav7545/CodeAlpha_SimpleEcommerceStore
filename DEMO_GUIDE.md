# ShopSphere Demo Guide

## Demo start karne ke liye

```powershell
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Website open karein: `http://127.0.0.1:8000/`

## Demo login

- Username: `demo_customer`
- Password: `DemoPass123!`

Ye account sirf local demonstration ke liye hai. Production deployment se pehle is demo account ko remove ya password change karna chahiye.

## Demo me kya check karein

1. Home page par categories aur product cards dekhein.
2. Products page me search karein, category filter karein aur sorting select karein.
3. Product detail page par quantity choose karke cart me item add karein.
4. Cart me quantity update, remove aur clear actions test karein.
5. Checkout form fill karke naya order place karein.
6. **My Orders** me order history dekhein.
7. **Track package** / **Track package button** se Pending, Processing, Shipped aur Delivered timeline dekhein.
8. `/admin/` me superuser se login karke kisi order ka status change karein; tracking event automatically add hoga.

## Demo limitations

- Checkout is a local order demo; no live payment is charged.
- Tracking is local order-status tracking; no courier API is called.
- Sample product images are local catalogue artwork. Admin panel se real licensed product photos upload ki ja sakti hain.
