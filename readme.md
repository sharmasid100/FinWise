# 🪙 **FinWise – Personal Financial Dashboard**

> A full-stack web application to help users track, analyze, and optimize their finances with insightful visualizations and an intuitive interface.

---

## 📖 **Overview**

**FinWise** is a personal financial dashboard built with a robust backend and dynamic frontend to empower users in managing their finances.
It allows users to register, log in, record transactions, view transaction history, and gain actionable insights through interactive graphs and charts.
The platform leverages data analytics to help users make informed decisions about their spending and saving habits.

---

## 🚀 **Features**

* 🔐 User authentication (login/register/logout) with secure sessions.
* ➕ Add, edit, and delete transactions (income & expenses) seamlessly.
* 📜 View transaction history with filters and pagination.
* 📊 Interactive data visualization:

  * Bar charts for category-wise spending
  * Pie charts for overall distribution
  * Time-based trends
* 📁 Persistent data storage with PostgreSQL & SQLAlchemy ORM.
* 💡 Clean and responsive UI for both desktop & mobile users.

---

## 🛠️ **Tech Stack**

| Layer           | Technology Used                 |
| --------------- | ------------------------------- |
| **Frontend**    | HTML, CSS, JavaScript, Chart.js |
| **Backend**     | Python Flask                    |
| **Database**    | PostgreSQL, SQLAlchemy          |
| **Server-side** | Jinja2 templating               |

---

## 🏗️ **Architecture**

* Flask server serving dynamic web pages with Jinja2.
* RESTful endpoints for CRUD operations on transactions.
* PostgreSQL database managed via SQLAlchemy.
* Frontend renders interactive graphs using Chart.js and consumes server data dynamically.

---

## 🔧 **Setup Instructions**

1️⃣ Clone the repository:

```
git clone https://github.com/yourusername/finwise.git
cd finwise
```

2️⃣ Create & activate a virtual environment:

```
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3️⃣ Install dependencies:

```
pip install -r requirements.txt
```

4️⃣ Set up your PostgreSQL database:

```
CREATE DATABASE finwise_db;
```

Update your `.env` file with the database URI and secret key.

5️⃣ Run the application:

```
flask run
```

Navigate to `http://127.0.0.1:5000` to use the app.

---

## 🧠 **Motivation**

With personal finance becoming increasingly complex, many people struggle to understand where their money goes. 
**FinWise** was built to address this gap — offering individuals a simple yet powerful platform to visualize, analyze, and optimize their finances effectively.

---

## 📜 **License**

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♂️ **Author**

👤 S Sidhart Sharma(https://github.com/sharmasid100)
📧 [sharmasidharth100@gmail.com](mailto:sharmasidharth100@gmail.com)

---

