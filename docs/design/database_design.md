# Database Design Document

## 1. Overview

This document outlines the database design for the pre-sales chatbot system. The database will store project estimates, lead information, and conversation history. The design focuses on simplicity, performance, and maintainability, using SQLite for the MVP with a structure that can be migrated to other database systems in the future.

## 2. Database Schema

### 2.1 Entity Relationship Diagram (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│                 │       │                 │       │                 │
│ ProjectEstimates│       │      Leads      │       │ ConversationLogs│
│                 │       │                 │       │                 │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         │                         │                         │
         │                         │ 1                       │ *
         │                         ├─────────────────────────┘
         │                         │
         │                         │
         │ *                       │ *
         └─────────────────────────┘
```

### 2.2 Tables

#### 2.2.1 ProjectEstimates

Stores predefined budget and timeline estimates for various project types.

```sql
CREATE TABLE project_estimates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_type TEXT NOT NULL UNIQUE,
    budget_range TEXT NOT NULL,
    typical_timeline TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster lookups by project_type
CREATE INDEX idx_project_estimates_project_type ON project_estimates(project_type);
```

#### 2.2.2 Leads

Stores information about potential clients collected during conversations.

```sql
CREATE TABLE leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    company TEXT,
    project_type TEXT,
    project_description TEXT,
    budget_range TEXT,
    timeline TEXT,
    status TEXT DEFAULT 'new',
    source TEXT DEFAULT 'chatbot',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_type) REFERENCES project_estimates(project_type)
);

-- Indexes for common queries
CREATE INDEX idx_leads_email ON leads(email);
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
```

#### 2.2.3 ConversationLogs

Stores the conversation history for each lead.

```sql
CREATE TABLE conversation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    sender TEXT NOT NULL, -- 'user' or 'bot'
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

-- Index for faster retrieval of conversation history
CREATE INDEX idx_conversation_logs_lead_id ON conversation_logs(lead_id);
CREATE INDEX idx_conversation_logs_timestamp ON conversation_logs(timestamp);
```

## 3. Initial Data

### 3.1 Project Estimates

The database will be initialized with the following project estimates:

| Project Type | Budget Range | Typical Timeline | Description |
|--------------|--------------|------------------|-------------|
| E-commerce website | $15,000-$50,000 | 2-4 months | Online store with product catalog, shopping cart, payment processing, and order management |
| Mobile restaurant app | $20,000-$60,000 | 3-5 months | Mobile application for restaurant ordering, reservations, and loyalty program |
| CRM system | $30,000-$100,000 | 4-8 months | Customer relationship management system with contact management, sales pipeline, and reporting |
| Chatbot integration | $10,000-$30,000 | 1-3 months | AI chatbot integration with existing website or application |
| Custom logistics software | $40,000-$120,000 | 5-9 months | Custom software for managing logistics, inventory, and supply chain |
| Corporate website | $8,000-$25,000 | 1-2 months | Professional company website with about, services, team, and contact pages |
| Blog/content platform | $12,000-$35,000 | 2-3 months | Content management system with user roles, categories, and commenting features |
| Real estate listing platform | $25,000-$80,000 | 3-6 months | Property listing website with search, filters, user accounts, and agent dashboards |
| Learning management system | $35,000-$90,000 | 4-7 months | Online education platform with courses, quizzes, progress tracking, and certificates |
| Healthcare patient portal | $40,000-$110,000 | 5-8 months | Secure patient portal with appointment scheduling, medical records, and messaging |
| Inventory management system | $30,000-$85,000 | 3-6 months | System for tracking inventory levels, orders, sales, and deliveries |
| Social media platform | $50,000-$150,000 | 6-12 months | Custom social network with user profiles, posts, comments, and messaging |
| Marketplace platform | $45,000-$130,000 | 5-10 months | Multi-vendor marketplace with listings, cart, payments, and vendor management |
| Mobile fitness app | $25,000-$70,000 | 3-6 months | Workout tracking, nutrition planning, progress monitoring, and social features |
| IoT dashboard | $20,000-$60,000 | 2-5 months | Real-time monitoring and control interface for IoT devices with data visualization |

```sql
INSERT INTO project_estimates (project_type, budget_range, typical_timeline, description)
VALUES 
    ('E-commerce website', '$15,000-$50,000', '2-4 months', 'Online store with product catalog, shopping cart, payment processing, and order management'),
    ('Mobile restaurant app', '$20,000-$60,000', '3-5 months', 'Mobile application for restaurant ordering, reservations, and loyalty program'),
    ('CRM system', '$30,000-$100,000', '4-8 months', 'Customer relationship management system with contact management, sales pipeline, and reporting'),
    ('Chatbot integration', '$10,000-$30,000', '1-3 months', 'AI chatbot integration with existing website or application'),
    ('Custom logistics software', '$40,000-$120,000', '5-9 months', 'Custom software for managing logistics, inventory, and supply chain'),
    ('Corporate website', '$8,000-$25,000', '1-2 months', 'Professional company website with about, services, team, and contact pages'),
    ('Blog/content platform', '$12,000-$35,000', '2-3 months', 'Content management system with user roles, categories, and commenting features'),
    ('Real estate listing platform', '$25,000-$80,000', '3-6 months', 'Property listing website with search, filters, user accounts, and agent dashboards'),
    ('Learning management system', '$35,000-$90,000', '4-7 months', 'Online education platform with courses, quizzes, progress tracking, and certificates'),
    ('Healthcare patient portal', '$40,000-$110,000', '5-8 months', 'Secure patient portal with appointment scheduling, medical records, and messaging'),
    ('Inventory management system', '$30,000-$85,000', '3-6 months', 'System for tracking inventory levels, orders, sales, and deliveries'),
    ('Social media platform', '$50,000-$150,000', '6-12 months', 'Custom social network with user profiles, posts, comments, and messaging'),
    ('Marketplace platform', '$45,000-$130,000', '5-10 months', 'Multi-vendor marketplace with listings, cart, payments, and vendor management'),
    ('Mobile fitness app', '$25,000-$70,000', '3-6 months', 'Workout tracking, nutrition planning, progress monitoring, and social features'),
    ('IoT dashboard', '$20,000-$60,000', '2-5 months', 'Real-time monitoring and control interface for IoT devices with data visualization');
```

### 3.2 Example Project Variations for Fuzzy Matching

The Budget & Timeline Tool will use fuzzy matching to handle variations in project type descriptions. Here are some examples of how different user inputs might map to the standard project types:

| User Input | Matched Project Type |
|------------|---------------------|
| "Online shop" | E-commerce website |
| "Web store" | E-commerce website |
| "E-commerce site" | E-commerce website |
| "Restaurant ordering app" | Mobile restaurant app |
| "Food delivery application" | Mobile restaurant app |
| "Customer management software" | CRM system |
| "Sales pipeline tool" | CRM system |
| "AI assistant for my website" | Chatbot integration |
| "Virtual assistant integration" | Chatbot integration |
| "Supply chain management system" | Custom logistics software |
| "Company website" | Corporate website |
| "Business website" | Corporate website |
| "Content management system" | Blog/content platform |
| "Property listing website" | Real estate listing platform |
| "Online course platform" | Learning management system |
| "E-learning system" | Learning management system |
| "Patient management system" | Healthcare patient portal |
| "Stock management software" | Inventory management system |
| "Community platform" | Social media platform |
| "Online marketplace" | Marketplace platform |
| "Exercise tracking app" | Mobile fitness app |
| "Smart device monitoring" | IoT dashboard |

## 4. Data Access Patterns

### 4.1 Common Queries

#### 4.1.1 Get Estimate by Project Type

```python
def get_estimate_by_project_type(project_type: str) -> dict:
    """
    Get budget and timeline estimate for a specific project type.
    Uses exact matching first, then falls back to fuzzy matching if needed.
    """
    # Implementation details in the Budget & Timeline Tool specification
```

#### 4.1.2 Store Lead Information

```python
def store_lead(lead_data: dict) -> int:
    """
    Store lead information collected during the conversation.
    Returns the ID of the newly created lead.
    """
    # Implementation details in the Python Backend specification
```

#### 4.1.3 Log Conversation

```python
def log_conversation(lead_id: int, message: str, sender: str) -> None:
    """
    Log a message in the conversation history.
    """
    # Implementation details in the Python Backend specification
```

#### 4.1.4 Get Leads by Status

```python
def get_leads_by_status(status: str) -> list:
    """
    Get all leads with a specific status.
    """
    # Implementation details in the Python Backend specification
```

## 5. Database Migration Strategy

### 5.1 Schema Versioning

The database schema will be versioned to support future migrations. Each migration will be stored in a separate SQL file with a version number.

```
migrations/
├── 001_initial_schema.sql
├── 002_add_description_to_project_estimates.sql
└── ...
```

### 5.2 Migration Process

1. Check current schema version
2. Apply any pending migrations in order
3. Update schema version

```python
def migrate_database():
    """
    Apply any pending database migrations.
    """
    # Implementation details in the Python Backend specification
```

## 6. Performance Considerations

### 6.1 Indexes

Indexes have been added to columns that will be frequently used in WHERE clauses or JOIN conditions to improve query performance.

### 6.2 Denormalization

For the MVP with SQLite, the schema is relatively normalized. If performance becomes an issue or when migrating to a different database system, consider denormalizing certain aspects of the schema.

### 6.3 Query Optimization

Complex queries should be optimized and tested with representative data volumes. Consider using query plans to identify potential performance issues.

## 7. Security Considerations

### 7.1 Data Encryption

Sensitive data (e.g., contact information) should be encrypted before storage. Consider using SQLite encryption extensions or application-level encryption.

### 7.2 Access Control

Implement proper access control to restrict database access to authorized users only. For the MVP, this can be simple authentication for admin access.

### 7.3 Input Validation

All user inputs must be validated and sanitized before being used in database queries to prevent SQL injection attacks.

## 8. Backup and Recovery

### 8.1 Backup Strategy

Regular backups of the database should be performed. For SQLite, this can be as simple as copying the database file.

### 8.2 Recovery Process

A documented recovery process should be in place to restore the database from backups in case of data loss or corruption.

## 9. Future Enhancements

### 9.1 Migration to Production Database

When moving beyond the MVP, consider migrating from SQLite to a more robust database system like PostgreSQL or MySQL.

### 9.2 Additional Tables

Future versions may include additional tables for:
- User authentication and authorization
- Analytics and reporting
- Marketing campaign tracking
- Integration with CRM systems

### 9.3 Performance Optimizations

As the system scales, consider:
- Implementing caching mechanisms
- Partitioning large tables
- Using read replicas for reporting queries

## 10. Conclusion

This database design provides a solid foundation for the pre-sales chatbot system. It balances simplicity with the ability to support the required functionality while allowing for future growth and enhancements. 