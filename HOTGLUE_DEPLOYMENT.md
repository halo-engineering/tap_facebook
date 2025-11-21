# Deploying tap-facebook to Hotglue

This guide shows you how to deploy the Facebook tap to Hotglue as a custom connector.

## Quick Start

### Install URI

```
git+https://github.com/halo-engineering/tap_facebook.git
```

Or use a specific version:

```
git+https://github.com/halo-engineering/tap_facebook.git@v0.1.0
```

## Step-by-Step Deployment

### Step 1: Access Hotglue Admin Panel

1. Log into your Hotglue account
2. Navigate to **Admin Panel**
3. Go to **Connector Settings** (or similar)

### Step 2: Add Custom Connector

Click **"Add Custom Connector"** and fill in:

```yaml
Connector Name: Facebook Engagement
Type: Source (tap)
Install URI: git+https://github.com/halo-engineering/tap_facebook.git
Entry Point: tap-facebook
Branch/Tag: main  # or v0.1.0 for pinned version
```

### Step 3: Upload Configuration Schema

Copy and paste the contents of [config_schema_facebook.json](./config_schema_facebook.json):

```json
{
  "type": "object",
  "title": "Facebook Engagement Configuration",
  "description": "Configuration for connecting to Facebook Pages",
  "properties": {
    "client_id": {
      "type": "string",
      "title": "Facebook App ID",
      "description": "Your Facebook App ID from developers.facebook.com",
      "order": 1
    },
    "client_secret": {
      "type": "string",
      "title": "Facebook App Secret",
      "description": "Your Facebook App Secret (kept secure)",
      "order": 2,
      "secret": true,
      "writeOnly": true
    },
    "page_id": {
      "type": "string",
      "title": "Facebook Page ID",
      "description": "The ID of the Facebook Page to sync data from",
      "order": 3,
      "examples": ["123456789012345"]
    },
    "start_date": {
      "type": "string",
      "format": "date-time",
      "title": "Start Date",
      "description": "Date to start syncing historical data from (ISO 8601 format)",
      "default": "2025-01-01T00:00:00Z",
      "order": 4,
      "examples": ["2025-01-01T00:00:00Z"]
    }
  },
  "required": ["page_id"],
  "secret": ["client_secret", "access_token", "refresh_token"],
  "oauth": {
    "provider": "facebook",
    "scopes": [
      "pages_show_list",
      "pages_read_engagement",
      "pages_read_user_content",
      "read_insights"
    ],
    "token_fields": {
      "access_token": "access_token",
      "refresh_token": "refresh_token"
    }
  }
}
```

### Step 4: Configure OAuth Provider

Navigate to **Admin Panel** → **OAuth Providers**:

Click **"Add OAuth Provider"** and configure:

```yaml
Provider Name: Facebook
Authorization URL: https://www.facebook.com/v18.0/dialog/oauth
Token URL: https://graph.facebook.com/v18.0/oauth/access_token
Scopes: pages_show_list,pages_read_engagement,pages_read_user_content,read_insights
```

Add your Facebook App credentials:
- **Client ID**: Your Facebook App ID
- **Client Secret**: Your Facebook App Secret

### Step 5: Link OAuth to Connector

1. Open the Facebook Engagement connector settings
2. Link to the Facebook OAuth provider
3. Map OAuth tokens:
   - `access_token` → `config.refresh_token`
   - `refresh_token` → `config.refresh_token`

### Step 6: Deploy/Activate

1. Click **"Deploy"** or **"Activate"** on the connector
2. Wait for Hotglue to:
   - Clone the repository
   - Install dependencies
   - Register the tap

### Step 7: Verify in Dashboard

Navigate to **Sources** in your Hotglue dashboard. You should see:

```
Custom Sources
  📘 Facebook Engagement     [Connect]
```

## Testing the Connector

### Test OAuth Flow

1. Click **"Connect"** on Facebook Engagement
2. You should be redirected to Facebook login
3. Grant permissions
4. Return to Hotglue with connected account

### Test Data Sync

1. After connecting, you'll see configuration form
2. Enter your Page ID
3. Select streams to sync:
   - ☑ posts
   - ☑ page_insights
   - ☑ post_insights
4. Click **"Test Connection"** or **"Run Sync"**
5. Verify data appears correctly

## Configuration Options for End Users

When customers connect Facebook Engagement in your Hotglue dashboard, they'll see a form with:

### Required Fields
- **Page ID**: Facebook Page ID to sync data from
  - Example: `123456789012345`
  - Find in: Page Settings → About → Page ID

### Optional Fields
- **Start Date**: Historical data start date
  - Default: `2025-01-01T00:00:00Z`
  - Format: ISO 8601 datetime

### Auto-filled by OAuth (Hidden)
- **Client ID**: Filled automatically from OAuth
- **Client Secret**: Filled automatically from OAuth
- **Access Token**: Obtained during OAuth flow
- **Refresh Token**: Obtained during OAuth flow

## Available Streams

| Stream | Type | Description |
|--------|------|-------------|
| **posts** | Incremental | Page posts with engagement metrics (likes, comments, shares, reactions) |
| **page_insights** | Incremental | Page-level insights and metrics |
| **post_insights** | Full Table | Post-level detailed analytics |

## Updating the Connector

When a new version is released:

### Option 1: Auto-Update (Latest)
If using `Branch/Tag: main`, Hotglue will automatically pull latest changes when you click "Redeploy"

### Option 2: Pinned Version
If using a version tag (e.g., `v0.1.0`):

1. Check for new releases: https://github.com/halo-engineering/tap_facebook/releases
2. Update `Branch/Tag` to new version (e.g., `v0.2.0`)
3. Click **"Redeploy"** or **"Update"**

## Monitoring

After deployment, monitor:

### In Hotglue Dashboard
- Sync success rates
- Error logs
- API usage
- Customer connections

### Key Metrics
- Number of connected sources
- Syncs per day
- Average sync duration
- Error rate by stream

## Troubleshooting

### Connector Not Appearing

**Check:**
- [ ] Install URI is correct
- [ ] Repository is public (or Hotglue has SSH access)
- [ ] Entry point is `tap-facebook` (not `tap_facebook`)
- [ ] Config schema is valid JSON

**Test locally:**
```bash
pip install git+https://github.com/halo-engineering/tap_facebook.git
tap-facebook --help
```

### OAuth Not Working

**Verify:**
- [ ] OAuth provider exists in Hotglue
- [ ] Client ID and Secret match your Facebook App
- [ ] Redirect URI is configured in Facebook App settings
- [ ] Scopes match tap requirements
- [ ] Token mapping is configured correctly

### Sync Failures

**Common Issues:**
1. **Invalid token**: Token expired or revoked
   - Solution: Reconnect account via OAuth
2. **Insufficient permissions**: Missing required scopes
   - Solution: Update Facebook App permissions
3. **Invalid Page ID**: Page doesn't exist or no access
   - Solution: Verify Page ID and user has admin access
4. **Rate limit exceeded**: Too many API calls
   - Solution: Reduce sync frequency or wait for reset

**Debug Steps:**
1. Check Hotglue sync logs
2. Download customer configuration
3. Test locally with same config:
   ```bash
   tap-facebook --config customer_config.json --discover
   ```

## Facebook App Requirements

Customers need:

1. **Facebook Developer Account**
   - Free at https://developers.facebook.com

2. **Facebook App** with permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `read_insights`

3. **Facebook Page** with:
   - Admin access
   - Active content (posts)

## API Rate Limits

Facebook Graph API limits:
- **App-level**: ~200 calls per hour per user
- **Page-level**: Varies by page size

The tap handles this with:
- Automatic retry with backoff
- Rate limit detection
- Efficient cursor-based pagination

## Support Resources

- **Tap Repository**: https://github.com/halo-engineering/tap_facebook
- **Issues**: https://github.com/halo-engineering/tap_facebook/issues
- **Documentation**: See README.md in repository
- **Facebook API Docs**: https://developers.facebook.com/docs/graph-api

## Configuration Schema Explained

The config schema defines the UI that customers see:

```json
{
  "properties": {
    "field_name": {
      "type": "string",           // Data type
      "title": "Display Name",    // Label shown to user
      "description": "Help text", // Tooltip/help text
      "order": 1,                 // Display order
      "secret": true,             // Hide input (passwords)
      "writeOnly": true,          // Never returned in API
      "default": "value",         // Pre-filled value
      "examples": ["example"]     // Placeholder examples
    }
  },
  "required": ["field"],          // Mandatory fields
  "oauth": {                      // OAuth configuration
    "provider": "facebook",
    "scopes": ["scope1"]
  }
}
```

## Summary

**Deployment URL:**
```
git+https://github.com/halo-engineering/tap_facebook.git
```

**Entry Point:**
```
tap-facebook
```

**Config Schema:**
[config_schema_facebook.json](./config_schema_facebook.json)

**OAuth Provider:**
- Provider: Facebook
- Auth URL: `https://www.facebook.com/v18.0/dialog/oauth`
- Token URL: `https://graph.facebook.com/v18.0/oauth/access_token`
- Scopes: `pages_show_list,pages_read_engagement,pages_read_user_content,read_insights`

**Status:** ✅ Ready for production deployment

---

For detailed tap documentation, see [README.md](./README.md)
