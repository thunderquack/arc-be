# Database diagram

```mermaid
erDiagram
    User {
        UUID id PK
        String username
        String password_hash
    }
    
    Role {
        UUID id PK
        String name
    }
    
    Permission {
        UUID id PK
        String name
    }
    
    Document {
        UUID id PK
        String title
        DateTime created_at
        DateTime updated_at
        UUID created_by FK
    }
    
    Page {
        UUID id PK
        UUID document_id FK
        Integer page_number
        LargeBinary image_data
        DateTime created_at
    }
    
    Attribute {
        UUID id PK
        String name
        Text description
    }
    
    DocumentAttribute {
        UUID id PK
        UUID document_id FK
        UUID attribute_id FK
        Text value
    }

    user_roles {
        UUID user_id PK FK
        UUID role_id PK FK
    }
    
    role_permissions {
        UUID role_id PK FK
        UUID permission_id PK FK
    }
    
    document_permissions {
        UUID document_id PK FK
        UUID permission_id PK FK
    }

    document_roles {
        UUID document_id PK FK
        UUID role_id PK FK
    }

    User ||--o{ Document : "created_by"
    User ||--o{ user_roles : ""
    Role ||--o{ user_roles : ""
    Role ||--o{ role_permissions : ""
    Permission ||--o{ role_permissions : ""
    Document ||--o{ Page : "pages"
    Document ||--o{ DocumentAttribute : "attributes"
    Document ||--o{ document_permissions : ""
    Page }o--|| Document : "document_id"
    Attribute ||--o{ DocumentAttribute : "document_attributes"
    DocumentAttribute }o--|| Document : "document_id"
    DocumentAttribute }o--|| Attribute : "attribute_id"
    Permission ||--o{ document_permissions : ""

```