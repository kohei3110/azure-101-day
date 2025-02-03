```mermaid
graph TD
    A[Start] --> B[Call upload_data with valid file]
    B --> C[File uploaded successfully]
    C --> D[Return filename]

    A --> E[Call upload_data with invalid file]
    E --> F[File upload failed]
    F --> G[Return error message]

```
