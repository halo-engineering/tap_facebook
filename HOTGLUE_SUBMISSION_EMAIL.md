# Email to Hotglue Support - Add Custom tap-facebook

## To: hello@hotglue.xyz

**Subject:** Add Custom Singer Tap - Facebook Pages (tap-facebook)

---

**Body:**

Hi Hotglue Team,

I'd like to add a custom Singer tap to our Hotglue workspace (prod.hg.haloforall.com).

## Tap Details

**Name:** Facebook Pages
**Tap Name:** tap-facebook
**Repository:** https://github.com/halo-engineering/tap_facebook
**Install URI:** `git+https://github.com/halo-engineering/tap_facebook.git`
**Executable:** `tap-facebook`
**Description:** Extract engagement data from Facebook Pages with OAuth 2.0 authentication

## Features

- ✅ OAuth 2.0 authentication with automatic token refresh
- ✅ Incremental syncing with state management
- ✅ Facebook Graph API v24.0
- ✅ Singer specification compliant

## Streams

1. **posts** - Posts with full engagement metrics (likes, comments, shares, reactions)
2. **page_insights** - Page-level analytics and insights

## Configuration Fields

The tap requires the following configuration fields:

1. **client_id** (string, required)
   - Label: "Facebook App ID"
   - Description: "Your Facebook App ID from developers.facebook.com"

2. **client_secret** (string, required, sensitive)
   - Label: "Facebook App Secret"
   - Description: "Your Facebook App Secret (kept secure)"

3. **refresh_token** (string, required, sensitive)
   - Label: "Access Token"
   - Description: "Facebook access token (will be automatically exchanged for long-lived token)"

4. **page_id** (string, required)
   - Label: "Facebook Page ID"
   - Description: "The ID of the Facebook Page to sync data from"

5. **start_date** (string, optional)
   - Label: "Start Date"
   - Default: "2025-01-01T00:00:00Z"
   - Description: "Date to start syncing historical data (ISO 8601 format)"

## Capabilities

- `discover` - Stream discovery
- `state` - Incremental sync support
- `catalog` - Stream catalog support

## Source Definition JSON

I've attached the complete source definition JSON file (hotglue_source_definition.json) that contains all the configuration details.

Alternatively, here's the JSON inline:

```json
{
  "name": "Facebook Pages",
  "tap_name": "tap-facebook",
  "install_uri": "git+https://github.com/halo-engineering/tap_facebook.git",
  "executable": "tap-facebook",
  "description": "Extract engagement data from Facebook Pages with OAuth 2.0 authentication",
  "capabilities": ["discover", "state", "catalog"],
  "settings": [
    {
      "name": "client_id",
      "label": "Facebook App ID",
      "type": "string",
      "required": true,
      "description": "Your Facebook App ID from developers.facebook.com"
    },
    {
      "name": "client_secret",
      "label": "Facebook App Secret",
      "type": "string",
      "required": true,
      "sensitive": true,
      "description": "Your Facebook App Secret (kept secure)"
    },
    {
      "name": "refresh_token",
      "label": "Access Token",
      "type": "string",
      "required": true,
      "sensitive": true,
      "description": "Facebook access token (will be automatically exchanged for long-lived token)"
    },
    {
      "name": "page_id",
      "label": "Facebook Page ID",
      "type": "string",
      "required": true,
      "description": "The ID of the Facebook Page to sync data from"
    },
    {
      "name": "start_date",
      "label": "Start Date",
      "type": "string",
      "required": false,
      "default": "2025-01-01T00:00:00Z",
      "description": "Date to start syncing historical data (ISO 8601 format)"
    }
  ]
}
```

## Testing

I've verified that:
- ✅ Repository is public
- ✅ Tap installs successfully via `pip install git+https://github.com/halo-engineering/tap_facebook.git`
- ✅ Executable `tap-facebook` works correctly
- ✅ Discovery mode works
- ✅ Syncing works with proper credentials

## Additional Context

I'm planning to add two more custom taps after this one (tap-linkedin and tap-instagram) using the same approach. If there's a self-service way to add source definitions, I'd be happy to use that instead!

Please let me know if you need any additional information or if I should make any changes to the tap or configuration.

Thank you!

---

**Attachment:** hotglue_source_definition.json

---

## Alternative: If Self-Service Is Available

If you have a self-service option, please point me to:
- API endpoint for creating source definitions
- Dashboard UI for adding custom sources
- Documentation on the process

I'm familiar with your documentation at https://docs.hotglue.com/key-concepts/connectors/v1-sources/settings and ready to configure this myself if that's an option.
