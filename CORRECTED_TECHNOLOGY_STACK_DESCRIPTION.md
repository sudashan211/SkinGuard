# Corrected Technology Stack Description for SkinGuard

## ❌ OLD (INCORRECT) - What Your Past Report Said:
- Firebase (NoSQL database)
- Laravel (PHP framework)

## ✅ NEW (CORRECT) - What You Actually Built:
- **React** (Frontend framework)
- **FastAPI** (Python backend framework)
- **PostgreSQL** (Relational database)

---

## CORRECTED SECTIONS FOR YOUR REPORT

### 2.5.1 React

React is an open-source JavaScript library developed by Meta (formerly Facebook) for building interactive and dynamic user interfaces, particularly for single-page applications (SPAs). React follows a component-based architecture, where the UI is broken down into reusable, self-contained components that manage their own state and render efficiently. This modular approach promotes code reusability, maintainability, and scalability across large applications.

React's Virtual DOM enables high performance by minimizing direct manipulation of the actual DOM. When a component's state changes, React updates only the affected parts of the UI, rather than re-rendering the entire page. This results in faster rendering and a smoother user experience, which is crucial for healthcare applications like SkinGuard that require real-time feedback and responsive interfaces.

React's declarative syntax makes it easier for developers to design complex interfaces by describing what the UI should look like for any given state. Combined with modern tooling like React Hooks (for state and lifecycle management) and React Router (for navigation), React provides a robust foundation for building scalable, maintainable web applications.

In the context of SkinGuard, React powers the patient-facing web application where users upload skin lesion images, view AI-generated analysis results, manage their health profiles, book appointments with dermatologists, and access hospital location services via Google Maps integration. React's component-based structure allows for seamless integration of complex features such as multi-step symptom wizards, real-time form validation, and dynamic data visualization.

**Key React Features Used in SkinGuard:**
- **Component-Based Architecture**: Modular UI components for upload forms, dashboards, and reports
- **React Hooks**: State management with `useState`, side effects with `useEffect`, and custom hooks for API calls
- **React Router**: Client-side routing for navigation between patient dashboard, upload page, and hospital locator
- **Tanstack Query (React Query)**: Efficient data fetching, caching, and synchronization with backend APIs
- **Vite**: Modern build tool providing fast development server and optimized production builds

---

### 2.5.2 FastAPI

FastAPI is a modern, high-performance web framework for building APIs with Python, designed for speed, ease of use, and automatic interactive documentation. Developed by Sebastián Ramírez, FastAPI is built on top of Starlette (for web routing) and Pydantic (for data validation), combining the best features of both to deliver a developer-friendly yet production-ready framework.

FastAPI follows the **ASGI (Asynchronous Server Gateway Interface)** standard, enabling asynchronous request handling. This makes it ideal for I/O-bound applications like healthcare systems that perform concurrent operations such as image processing, database queries, and AI model inference. FastAPI's async capabilities allow the server to handle thousands of concurrent requests efficiently without blocking, making it suitable for applications with high traffic and real-time requirements.

One of FastAPI's standout features is its **automatic generation of OpenAPI documentation** (Swagger UI and ReDoc), which provides an interactive interface for testing API endpoints without writing additional documentation code. This accelerates development and testing workflows, especially when integrating frontend and backend teams.

FastAPI leverages **Python type hints** for automatic request validation, serialization, and editor support. By using Pydantic models, developers can define strict data schemas that are automatically validated at runtime, reducing bugs and ensuring data integrity. This is particularly important in healthcare applications like SkinGuard, where patient data, medical reports, and AI predictions must conform to strict formats.

**Key FastAPI Features Used in SkinGuard:**
- **Async/Await Support**: Handles multiple concurrent image uploads, AI model inference, and database operations efficiently
- **Pydantic Models**: Strict data validation for patient profiles, medical reports, and symptom data (age limits, risk levels, Fitzpatrick scale)
- **Dependency Injection**: Reusable dependencies for authentication (JWT tokens), database sessions, and audit logging
- **CORS Middleware**: Enables cross-origin requests from the React frontend running on a different port
- **File Upload Handling**: Processes multipart/form-data for skin lesion image uploads (up to 10MB)
- **RESTful API Design**: Clean endpoint structure (`/api/analyze-skin`, `/api/reports`, `/api/appointments`)

**FastAPI Architecture in SkinGuard:**
```
frontend (React:3000) → HTTP Request → backend (FastAPI:8001)
                                            ↓
                                    ┌───────────────┐
                                    │  API Routers  │
                                    ├───────────────┤
                                    │ • /auth       │
                                    │ • /patient    │
                                    │ • /doctors    │
                                    │ • /reports    │
                                    │ • /appointments│
                                    └───────┬───────┘
                                            ↓
                        ┌───────────────────┴───────────────────┐
                        ↓                                       ↓
                ┌───────────────┐                   ┌──────────────────┐
                │  AI Pipeline  │                   │  Database Layer  │
                ├───────────────┤                   ├──────────────────┤
                │• NSFW Filter  │                   │  PostgreSQL DB   │
                │• Quality Check│                   │  • users         │
                │• ViT Model    │                   │  • patient_data  │
                │• Risk Assessment│                 │  • medical_reports│
                └───────────────┘                   │  • appointments  │
                                                    └──────────────────┘
```

---

### 2.5.3 PostgreSQL

PostgreSQL is a powerful, open-source relational database management system (RDBMS) know for its robustness, extensibility, and SQL standards compliance. Originally developed at the University of California, Berkeley, PostgreSQL has evolved into one of the most advanced and reliable databases for enterprise applications, including healthcare systems requiring strict data integrity, complex queries, and ACID (Atomicity, Consistency, Isolation, Durability) compliance.

Unlike NoSQL databases, PostgreSQL uses a **structured, table-based schema** with predefined relationships between entities. This relational model is ideal for healthcare applications like SkinGuard, where patient data, medical reports, appointments, and user profiles have clear relationships that must be maintained consistently. For example, every medical report is linked to a specific patient (via `patient_id` foreign key), and every appointment is linked to both a patient and a doctor/hospital.

PostgreSQL supports **JSONB data types**, which combine the benefits of relational structure with the flexibility of NoSQL-style document storage. In SkinGuard, this is used to store complex AI predictions and symptom data as JSON within the `medical_reports` table, eliminating the need for additional tables while maintaining relational integrity for user and appointment data.

**Key PostgreSQL Features Used in SkinGuard:**
- **Relational Schema**: Enforces data integrity through foreign keys, constraints, and normalized tables
- **JSONB Columns**: Stores AI predictions (`ai_prediction` column) and symptom data (`symptoms` column) as flexible JSON while maintaining relational structure for core entities
- **ACID Compliance**: Ensures data consistency for critical operations like appointment bookings and medical report creation
- **Advanced Queries**: Supports complex JOIN operations to retrieve patient data with associated reports and appointments in a single query
- **Indexing**: Improves query performance for frequently accessed data (e.g., searching reports by patient ID or risk level)
- **Triggers and Constraints**: Enforces business rules (e.g., valid Fitzpatrick scale values, age limits, unique email addresses)

**Database Schema in SkinGuard:**
```sql
users
├── id (UUID, PRIMARY KEY)
├── email (UNIQUE)
├── full_name
├── role (patient | doctor)
└── password_hash

patient_data
├── id (UUID, PRIMARY KEY)
├── user_id (FOREIGN KEY → users.id)
├── age (INTEGER, 1-120)
├── skin_type (Fitzpatrick I-VI)
└── family_history (TEXT)

medical_reports
├── id (UUID, PRIMARY KEY)
├── patient_id (FOREIGN KEY → users.id)
├── image_url (TEXT)
├── ai_prediction (JSONB) ← Vision Transformer predictions
├── symptoms (JSONB) ← Patient symptom data
├── risk_level (low | medium | high | urgent)
├── status (pending | reviewed | urgent)
└── created_at (TIMESTAMP)

appointments
├── id (UUID, PRIMARY KEY)
├── patient_id (FOREIGN KEY → users.id)
├── doctor_id (FOREIGN KEY → users.id)
├── report_id (FOREIGN KEY → medical_reports.id)
├── status (pending | confirmed | completed | cancelled)
└── scheduled_at (TIMESTAMP)
```

**Why PostgreSQL Instead of Firebase for SkinGuard:**

| Feature | PostgreSQL (Used) | Firebase (Old Report) |
|---------|-------------------|----------------------|
| **Data Model** | Relational (structured, normalized) | NoSQL (flexible, denormalized) |
| **Relationships** | Native foreign keys and JOINs | Manual relationship management |
| **Complex Queries** | Advanced SQL with JOINs, subqueries, aggregations | Limited querying capabilities |
| **ACID Compliance** | ✅ Full ACID guarantees | ⚠️ Limited transaction support |
| **Healthcare Suitability** | ✅ Ideal (structured medical data) | ⚠️ Better for real-time messaging |
| **Data Integrity** | ✅ Enforced by constraints | ❌ Application-level only |
| **Scalability** | ✅ Vertical and horizontal scaling | ✅ Automatic horizontal scaling |
| **Cost** | ✅ Free and open-source | 💰 Pay-per-operation beyond free tier |

For SkinGuard, PostgreSQL was chosen because:
1. **Medical data is inherently relational** (patients have reports, reports have appointments)
2. **Data integrity is critical** (patient records must be accurate and consistent)
3. **Complex queries are required** (e.g., "Find all urgent reports for doctors with pending appointments")
4. **Cost-effective** (no per-operation charges, runs on local server or affordable hosting)
5. **Industry standard** (widely used in healthcare for EHR systems and medical databases)

---

## Summary of Actual Technology Stack

### Frontend
- **React 18**: Component-based UI framework
- **Vite**: Fast build tool and development server
- **Tanstack Query**: Data fetching and state management
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first styling

### Backend
- **FastAPI**: Python-based async web framework
- **Uvicorn**: ASGI server for running FastAPI
- **Pydantic**: Data validation and serialization
- **Python 3.11**: Core programming language

### Database
- **PostgreSQL**: Relational database (local or cloud)
- **SQLAlchemy** (optional): ORM for database interactions
- **Supabase** (optional): PostgreSQL hosting with built-in auth

### AI/ML
- **Vision Transformer (ViT)**: Skin cancer classification model
- **Hugging Face Transformers**: Model loading and inference
- **PyTorch**: Deep learning framework
- **TensorFlow**: Alternative ML framework (if needed)

### Infrastructure
- **Google Maps API**: Hospital location services
- **Render/Railway**: Cloud hosting options
- **Docker** (optional): Containerization

---

## Corrected Reference Format

**Correct citation for your current stack:**

React Team. (2023). *React: A JavaScript library for building user interfaces*. Meta Open Source. https://react.dev/

Ramírez, S. (2023). *FastAPI: Modern, fast (high-performance), web framework for building APIs with Python 3.8+*. https://fastapi.tiangolo.com/

PostgreSQL Global Development Group. (2023). *PostgreSQL: The world's most advanced open source relational database*. https://www.postgresql.org/

**Remove these incorrect citations:**

~~Firebase. (2022). *Firebase: Google's mobile and web application development platform*.~~ ❌ NOT USED

~~Otwell, T. (2023). *Laravel: The PHP framework for web artisans*.~~ ❌ NOT USED

---

## Action Required

**You MUST update your report to replace:**
1. ❌ Section 2.5.2 Firebase → ✅ Section 2.5.1 React
2. ❌ Section 2.5.3 Laravel → ✅ Section 2.5.2 FastAPI
3. ➕ Add new Section 2.5.3 PostgreSQL

This correction is **critical** because your current report describes technologies you **did not use**, which would be:
- ❌ Academically dishonest
- ❌ Factually incorrect
- ❌ Easily discovered during demo/defense (your code is React + FastAPI!)

---

**Do you want me to create a full replacement section you can copy-paste into your report?**
