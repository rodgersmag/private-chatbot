# Dynamic CORS Management System

This document describes the dynamic CORS management system implemented for SelfDB, which allows administrators to manage CORS origins without server restarts.

## Overview

The hybrid CORS management system combines three sources of origins:

1. **Environment Variable Configuration** - Static origins defined in `.env`
2. **Database-backed Dynamic Origins** - Origins managed via API endpoints  
3. **Default System Origins** - Hardcoded localhost and development origins

## Configuration

### Environment Variable Setup

Add CORS origins to your `.env` file:

```bash
# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://app.selfdb.io
```

Multiple origins should be comma-separated. Whitespace is automatically trimmed.

### Default Origins

The system always includes these default origins:
- `http://localhost`
- `http://localhost:3000`  
- `http://frontend:3000`
- `https://opd.selfdb.io`

## API Endpoints

All CORS management endpoints require superuser privileges and are prefixed with `/api/v1/cors/origins`.

### List Origins
```
GET /api/v1/cors/origins
```
Returns all configured CORS origins with metadata.

Query Parameters:
- `active_only` (boolean, default: true) - Only return active origins

### Create Origin
```
POST /api/v1/cors/origins
```
Creates a new CORS origin.

Request Body:
```json
{
  "origin": "https://app.example.com",
  "description": "Main application frontend",
  "extra_metadata": {"environment": "production"}
}
```

### Get Origin by ID
```
GET /api/v1/cors/origins/{origin_id}
```

### Update Origin
```
PUT /api/v1/cors/origins/{origin_id}
```

Request Body (all fields optional):
```json
{
  "origin": "https://new-domain.com",
  "description": "Updated description",
  "is_active": true,
  "extra_metadata": {"updated": true}
}
```

### Delete Origin
```
DELETE /api/v1/cors/origins/{origin_id}
```

Query Parameters:
- `hard_delete` (boolean, default: false) - Permanently delete vs soft delete

### Validate Origin URL
```
POST /api/v1/cors/origins/validate
```

Request Body:
```json
{
  "origin": "https://app.example.com"
}
```

Returns validation result with error details if invalid.

### Refresh Cache
```
POST /api/v1/cors/origins/refresh-cache
```

Manually refreshes the CORS origins cache. Useful for troubleshooting.

## Origin Validation Rules

Valid origins must:
- Use `http://` or `https://` protocol
- Have a valid domain name with TLD (except `localhost`)
- Optionally include a port number
- Not include paths, query parameters, or fragments

Examples:
- ✅ `https://app.example.com`
- ✅ `http://localhost:3000`
- ✅ `https://subdomain.domain.co.uk:8080`
- ❌ `ftp://example.com` (wrong protocol)
- ❌ `https://domain.com/path` (path included)
- ❌ `https://invalid..domain.com` (invalid domain)

## Caching and Performance

### Cache Behavior
- Database origins are cached for 5 minutes
- Cache is automatically invalidated when origins are modified
- Environment and default origins are always included (no caching needed)

### Performance Impact
- Minimal impact on request handling
- Cache hits avoid database queries
- Graceful fallback if database is unavailable

## Security Features

### Access Control
- All CORS management endpoints require superuser privileges
- Non-superusers cannot view, create, modify, or delete origins

### Audit Trail
- All origins track who created them (`created_by` field)
- Timestamps for creation and modification
- Soft delete preserves audit history

### Validation
- Strict URL format validation
- Prevention of duplicate origins
- Protection against malicious origin patterns

## Migration

### From Hardcoded Origins
1. Add your existing hardcoded origins to `CORS_ALLOWED_ORIGINS` environment variable
2. Run the database migration: `alembic upgrade head`
3. Gradually move origins from environment variable to database via API
4. Remove origins from environment variable once migrated

### Database Migration
The system includes an Alembic migration that creates the `cors_origins` table:

```bash
# Apply the migration
alembic upgrade head
```

The migration creates:
- `cors_origins` table with proper indexes
- Foreign key relationship to `users` table
- UUID primary keys for security

## Troubleshooting

### Cache Issues
If origins aren't updating as expected:
1. Check if cache invalidation is working
2. Use the manual cache refresh endpoint
3. Verify database connectivity

### Database Connectivity
If the database is unavailable:
- System falls back to environment variable and default origins
- No disruption to CORS functionality
- Error logged but requests continue

### Origin Not Working
1. Verify origin is in the allowed list via API
2. Check origin format matches exactly (including protocol and port)
3. Ensure origin is marked as `is_active: true`
4. Check browser developer tools for CORS error details

## Example Usage

### Adding a Production Domain
```bash
curl -X POST https://api.selfdb.io/api/v1/cors/origins \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "https://production-app.com",
    "description": "Production application frontend"
  }'
```

### Listing All Origins
```bash
curl -X GET https://api.selfdb.io/api/v1/cors/origins \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Disabling an Origin
```bash
curl -X PUT https://api.selfdb.io/api/v1/cors/origins/{origin_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'
```

This dynamic CORS management system provides a secure, scalable way to manage CORS origins in production without requiring server restarts or code deployments.