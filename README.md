# 🍋 Little Lemon Restaurant API

This is a Django REST Framework (DRF) project built for **Little Lemon**, a fictional restaurant. The project was developed as the **final assignment for the "APIs" course by Meta on Coursera**.

---

## 📌 Introduction

This API enables the Little Lemon restaurant to support web and mobile applications for various user roles. It covers menu management, user access, order tracking, and delivery crew assignment.

---

## 🎯 Scope

- Allow client applications to interact with restaurant data
- Role-based access control for managers, delivery crew, and customers
- Full CRUD functionality for menu items, cart, and order management
- Support for user registration (Djoser), authentication, throttling, and permissions

---

## 🧱 Project Structure

- **Project Name**: `LittleLemon`
- **App Name**: `LittleLemonAPI`
- **Dependencies**: Managed using [Pipenv](https://pipenv.pypa.io/en/latest/)
- **Views**: Implemented using **class-based views (CBVs)**

---

## 👥 User Roles

- **Manager**: Full access to menu, user, and order management
- **Delivery Crew**: Can view and update delivery status of assigned orders
- **Customer**: Can view menu, manage cart, and place/view orders

Users can be assigned to groups via the Django admin panel. Any user not in a group is treated as a **Customer**.

---

## 🚦 HTTP Status Codes

| Status Code | Meaning                              |
|-------------|--------------------------------------|
| 200         | OK (GET, PUT, PATCH, DELETE)         |
| 201         | Created (POST)                       |
| 400         | Bad Request (validation errors)      |
| 401         | Unauthorized (invalid token)         |
| 403         | Forbidden (access denied)            |
| 404         | Not Found (resource does not exist)  |

---

## 🔐 Authentication & User Management

Uses **Djoser** for authentication endpoints.

| Endpoint                    | Method | Access         | Purpose                                  |
|----------------------------|--------|----------------|------------------------------------------|
| `/auth/users/`              | POST   | Public         | Register new user                        |
| `/auth/users/me/`           | GET    | Authenticated  | Get current user info                    |
| `/auth/token/login/`        | POST   | Public         | Token generation for login               |

#### Register a new user
```bash
curl -X POST http://localhost:8000/auth/users/ \
-H "Content-Type: application/json" \
-d '{"username": "john", "email": "john@example.com", "password": "pass1234"}'
```

#### Login and get auth token
```bash
curl -X POST http://localhost:8000/auth/token/login/ \
-H "Content-Type: application/json" \
-d '{"username": "john", "password": "pass1234"}'
```

#### Get current user
```bash
curl -X GET http://localhost:8000/auth/users/me/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

---

## 🏷️ Menu Category Endpoints

### Manager only

| Endpoint                    | Method                  | Access        | Purpose                      |
|-----------------------------|-------------------------|---------------|------------------------------|
| `/api/categories/`          | GET                     | Manager       | View all menu categories     |
| `/api/categories/{id}`      | POST/PUT/PATCH/DELETE   | Manager       | View specific menu item      |

#### Get all menu categories
```bash
curl -X GET http://localhost:8000/api/categories/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

#### Create a menu category
```bash
curl -X POST http://localhost:8000/api/categories/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
-H "Content-Type: application/json" \
-d '{"title": "desserts"}'
```

#### Update a menu category (PUT/PATCH)
```bash
curl -X PUT http://localhost:8000/api/categories/1 \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
-H "Content-Type: application/json" \
-d '{"title": "desserts"}'
```

---

## 🍽 Menu Item Endpoints

### Customers & Delivery Crew

| Endpoint                     | Method | Access        | Purpose                      |
|-----------------------------|--------|---------------|------------------------------|
| `/api/menu-items`           | GET    | All           | View all menu items          |
| `/api/menu-items/{id}/`     | GET    | All           | View specific menu item      |
| POST/PUT/PATCH/DELETE       | —      | Forbidden     | Returns 403 Forbidden        |

#### Get all menu items
```bash
curl -X GET http://localhost:8000/api/menu-items
```

#### Get specific menu item
```bash
curl -X GET http://localhost:8000/api/menu-items/4/
```

#### View menu items by category
```bash
curl "localhost:8000/api/menu-items/?category=<category_name>"
curl "localhost:8000/api/menu-items/?category=main"
```

### Managers

| Endpoint                     | Method         | Purpose                            |
|-----------------------------|----------------|------------------------------------|
| `/api/menu-items`           | GET, POST      | List/create menu items             |
| `/api/menu-items/{id}/`     | GET, PUT, PATCH, DELETE | Retrieve/update/delete items     |

#### Create a menu item (Manager only)
```bash
curl -X POST http://localhost:8000/api/menu-items/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"title": "Pasta", "price": "12.99", "featured": false, "category_id": 1}'
```

#### Update a menu item (Manager only)
```bash
curl -X PATCH http://localhost:8000/api/menu-items/1/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"title": "Shrimp Pasta", "price": "14.99", "featured": true, "category_id": 1}'
```
---

## 👥 User Group Management (Managers Only)

| Endpoint                                      | Method   | Purpose                                |
|----------------------------------------------|----------|----------------------------------------|
| `/api/groups/manager/users/`                 | GET      | List all managers                      |
| `/api/groups/manager/users/`                 | POST     | Add user to manager group              |
| `/api/groups/manager/users/{userId}/`        | DELETE   | Remove user from manager group         |
| `/api/groups/delivery-crew/users/`           | GET      | List all delivery crew members         |
| `/api/groups/delivery-crew/users/`           | POST     | Add user to delivery crew group        |
| `/api/groups/delivery-crew/users/{userId}/`  | DELETE   | Remove user from delivery crew group   |

#### Assign a user to manager group
```bash
curl -X POST http://localhost:8000/api/groups/manager/users/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"username": "john"}'
```

#### Remove user from delivery crew group
```bash 
curl -X DELETE http://localhost:8000/api/groups/delivery-crew/users/3/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```
---

## 🛒 Cart Management (Customers Only)

| Endpoint                   | Method | Purpose                                      |
|---------------------------|--------|----------------------------------------------|
| `/api/cart/menu-items/`   | GET    | View current cart items                      |
| `/api/cart/menu-items/`   | POST   | Add item to cart                             |
| `/api/cart/menu-items/`   | DELETE | Clear cart                                   |

#### Add item to cart
```bash
curl -X POST http://localhost:8000/api/cart/menu-items/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"menuitem_name": "Beef Pasta", "quantity": 2}'
```

#### View cart
```bash
curl -X GET http://localhost:8000/api/cart/menu-items/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

#### Clear cart
```bash
curl -X DELETE http://localhost:8000/api/cart/menu-items/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```
---

## 📦 Order Management

### Customer

| Endpoint                  | Method      | Purpose                                                |
|--------------------------|-------------|--------------------------------------------------------|
| `/api/orders/`           | GET         | View all your orders                                  |
| `/api/orders/`           | POST        | Create order from current cart, clear cart            |
| `/api/orders/{orderId}/` | GET         | View specific order (if owned by user)                |
| `/api/orders/{orderId}/` | PUT/PATCH   | Update status (if user is manager)                    |

#### Create order from cart (Customer only)
```bash
curl -X POST http://localhost:8000/api/orders/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

#### Get current user's orders
```bash
curl -X GET http://localhost:8000/api/orders/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

#### Get specific order (if owned)
```bash
curl -X GET http://localhost:8000/api/orders/1/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

### Manager

| Endpoint                  | Method      | Purpose                                                |
|--------------------------|-------------|--------------------------------------------------------|
| `/api/orders/`           | GET         | View all orders across users                          |
| `/api/orders/{orderId}/` | PUT/PATCH   | Assign delivery crew and update status                |
| `/api/orders/{orderId}/` | DELETE      | Delete order                                           |

#### Manager assigns delivery crew and status
```bash
curl -X PATCH http://localhost:8000/api/orders/1/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"delivery_crew": "driver1", "status": 0}'
```

#### Delete an order (Manager only)
```bash
curl -X DELETE http://localhost:8000/api/orders/1/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

### Delivery Crew

| Endpoint                  | Method    | Purpose                                       |
|--------------------------|-----------|-----------------------------------------------|
| `/api/orders/`            | GET       | View orders assigned to delivery crew         |
| `/api/orders/{orderId}/`  | PATCH     | Update delivery status only                   |

#### Delivery crew view assigned orders
```bash
curl -X PATCH http://localhost:8000/api/orders/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN"
```

#### Delivery crew updates order status only
```bash
curl -X PATCH http://localhost:8000/api/orders/1/ \
-H "Authorization: Token YOUR_ACCESS_TOKEN" \
-H "Content-Type: application/json" \
-d '{"status": 1}'
```
---

## 🔎 Features

- **Filtering, Pagination, Sorting**:
  - Available for `/api/menu-items` and `/api/orders`
  - Supports search by name, category, price, and more

---

## 🛡 Throttling

| User Type         | Rate Limit         |
|-------------------|--------------------|
| Anonymous Users   | 2 requests/minute  |
| Authenticated     | 5 requests/minute  |

Configured using Django REST Framework's `DEFAULT_THROTTLE_RATES`.

---

## 🧪 Testing the API

You can use tools like **Postman** or **Insomnia**:

1. Register and obtain a token via `/api/users/` and `/token/login/`
2. Use the token in your requests:
3. Test each endpoint based on your role

---

## 🛠 Setup Instructions

```bash
# Clone the repo
git clone https://github.com/reconized/LittleLemon.git
cd LittleLemon

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations and start server
python manage.py migrate
python manage.py runserver
```

---

## 📬 Contact
Project developed as part of the [Meta Back-End Developer Professional Certificate](https://www.coursera.org/professional-certificates/meta-back-end-developer).

For questions, feel free to reach out on [GitHub Issues](https://github.com/reconized/LittleLemon/issues).
