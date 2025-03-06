# API Documentation

This document provides detailed information about the API endpoints available in the pre-sales chatbot backend.

## Base URL

All endpoints are relative to the base URL:

```
http://{API_HOST}:{API_PORT}
```

Where `API_HOST` and `API_PORT` are defined in your environment variables.

## Endpoints

### Health Check

Check if the API is running.

```
GET /api/health
```

#### Response

```json
{
  "status": "ok"
}
```

### Get Budget and Timeline Estimates

Get budget and timeline estimates for a specific project type.

```
GET /api/estimates?project_type={project_type}
```

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| project_type | string | The type of project (e.g., e-commerce website, mobile app) |

#### Response

```json
{
  "project_type": "e-commerce website",
  "budget_range": "$3k-$6k",
  "typical_timeline": "2-3 months"
}
```

#### Error Response

```json
{
  "error": "Missing project_type parameter",
  "status_code": 400
}
```

```json
{
  "project_type": "unknown",
  "budget_range": "Requires more information",
  "typical_timeline": "Requires more information",
  "message": "We need more details about your project to provide an accurate estimate."
}
```

### Store Lead Information

Store lead information in the database.

```
POST /api/leads
```

#### Request Body

```json
{
  "name": "John Doe",
  "contact": "john.doe@example.com",
  "project_type": "e-commerce website",
  "project_details": "An online store for selling handmade crafts",
  "estimated_budget": "$3k-$6k",
  "estimated_timeline": "2-3 months",
  "follow_up_consent": true
}
```

#### Required Fields

- name
- contact
- project_type

#### Response

```json
{
  "id": 1,
  "status": "success"
}
```

#### Error Response

```json
{
  "error": "Missing required field: name",
  "status_code": 400
}
```

### Get All Leads (Admin Only)

Get all leads from the database.

```
GET /api/leads
```

#### Response

```json
{
  "leads": [
    {
      "id": 1,
      "name": "John Doe",
      "contact": "john.doe@example.com",
      "project_type": "e-commerce website",
      "project_details": "An online store for selling handmade crafts",
      "estimated_budget": "$3k-$6k",
      "estimated_timeline": "2-3 months",
      "follow_up_consent": true,
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "contact": "jane.smith@example.com",
      "project_type": "mobile restaurant app",
      "project_details": "A mobile app for a restaurant",
      "estimated_budget": "$5k-$8k",
      "estimated_timeline": "3-4 months",
      "follow_up_consent": false,
      "created_at": "2023-01-02T12:00:00Z",
      "updated_at": "2023-01-02T12:00:00Z"
    }
  ]
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:

- 200: Success
- 400: Bad Request (missing or invalid parameters)
- 404: Not Found
- 500: Internal Server Error

Error responses include an error message and status code:

```json
{
  "error": "Error message",
  "status_code": 400
}
```

## Authentication

Currently, there is no authentication for the API endpoints. This will be added in a future update.

## Rate Limiting

Currently, there is no rate limiting for the API endpoints. This will be added in a future update.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for all endpoints.

## Versioning

The API is currently at version 1.0.0. Future versions will be announced in the changelog. 