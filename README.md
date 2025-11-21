# tap-facebook

A [Singer](https://www.singer.io/) tap for extracting engagement data from Facebook Pages.

Built with the [Singer SDK](https://github.com/singer-io/singer-python) for the [Singer](https://www.singer.io/) specification.

## Features

- **OAuth 2.0 Authentication** - Automatic token refresh for long-lived access
- **Incremental Sync** - Efficiently sync only new/updated data using state bookmarks
- **Multiple Streams** - Posts, Page Insights, and Post Insights
- **Facebook Graph API v18.0** - Uses latest stable API version
- **Hotglue Compatible** - Deploy directly to Hotglue via git

## Streams

| Stream | Incremental | Replication Key | Description |
|--------|-------------|-----------------|-------------|
| `posts` | ✅ | `created_time` | Facebook page posts with engagement metrics (likes, comments, shares, reactions) |
| `page_insights` | ✅ | `end_time` | Page-level insights and metrics |
| `post_insights` | ❌ | N/A | Post-level insights and detailed analytics |

## Quick Start

### Installation

#### From GitHub (Recommended for Hotglue)

```bash
pip install git+https://github.com/halo-engineering/tap_facebook.git
```

#### From Source

```bash
git clone https://github.com/halo-engineering/tap_facebook.git
cd tap_facebook
pip install -e .
```

### Configuration

Create a `config.json` file:

```json
{
  "client_id": "your_facebook_app_id",
  "client_secret": "your_facebook_app_secret",
  "refresh_token": "your_refresh_token",
  "page_id": "your_page_id",
  "start_date": "2025-01-01T00:00:00Z"
}
```

See [config.example.json](./config.example.json) for a complete example.

### Usage

#### Discovery Mode

Discover available streams and their schemas:

```bash
tap-facebook --config config.json --discover > catalog.json
```

#### Sync Mode

Run a full or incremental sync:

```bash
tap-facebook --config config.json --catalog catalog.json
```

With state for incremental syncing:

```bash
tap-facebook --config config.json --catalog catalog.json --state state.json > output.json
```

The tap will output Singer-formatted messages to stdout.

## Facebook App Setup

### Prerequisites

- Facebook Developer account
- Facebook Page with admin access
- Facebook App with required permissions

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **"Create App"** → **Business** type
3. Enter app name and contact email
4. Note your **App ID** and **App Secret** (Settings → Basic)

### Step 2: Configure App Permissions

Add the following permissions in **App Review** → **Permissions and Features**:

- `pages_show_list` - List pages you manage
- `pages_read_engagement` - Read engagement data
- `pages_read_user_content` - Read page content
- `read_insights` - Read page insights

### Step 3: Get Page Access Token

#### Option A: Using Graph API Explorer (Testing)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click **Get Token** → **Get Page Access Token**
4. Select the page you want to sync
5. Copy the token (short-lived, 1 hour)

#### Option B: OAuth Flow (Production)

1. Redirect users to authorization URL:
   ```
   https://www.facebook.com/v18.0/dialog/oauth?
     client_id={app-id}&
     redirect_uri={redirect-uri}&
     scope=pages_show_list,pages_read_engagement,pages_read_user_content,read_insights
   ```

2. Exchange authorization code for access token:
   ```bash
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?
     client_id={app-id}&
     client_secret={app-secret}&
     redirect_uri={redirect-uri}&
     code={code}"
   ```

3. Exchange short-lived token for long-lived token (60 days):
   ```bash
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app-id}&
     client_secret={app-secret}&
     fb_exchange_token={short-lived-token}"
   ```

### Step 4: Get Page ID

Find your Page ID using Graph API Explorer:

```
GET /{page-name}?fields=id,name
```

Or find it in your Page's **About** section → **Page Transparency**.

### Complete Setup Guide

For detailed instructions, see [config.example.json](./config.example.json).

## Configuration Options

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `client_id` | string | Yes* | Facebook App ID |
| `client_secret` | string | Yes* | Facebook App Secret |
| `refresh_token` | string | Yes | Long-lived access token or refresh token |
| `page_id` | string | Yes | Facebook Page ID to sync data from |
| `start_date` | string | No | ISO 8601 datetime to start syncing historical data (default: 30 days ago) |

\* Required for token refresh. If using a long-lived token that won't expire during sync, these can be omitted.

## Stream Schemas

### Posts Stream

```json
{
  "id": "123456789_987654321",
  "message": "Post content...",
  "created_time": "2025-01-15T10:30:00+0000",
  "updated_time": "2025-01-15T12:00:00+0000",
  "permalink_url": "https://facebook.com/...",
  "likes_count": 42,
  "comments_count": 7,
  "shares_count": 3,
  "reactions_count": 50,
  "page_id": "123456789"
}
```

### Page Insights Stream

```json
{
  "id": "123456789/insights/page_impressions/day",
  "name": "page_impressions",
  "period": "day",
  "title": "Daily Total Impressions",
  "description": "The number of times any content from your Page...",
  "value": 1234,
  "end_time": "2025-01-15T08:00:00+0000"
}
```

### Post Insights Stream

```json
{
  "id": "123456789_987654321/insights/post_impressions",
  "post_id": "123456789_987654321",
  "name": "post_impressions",
  "title": "Lifetime Post Total Impressions",
  "value": 567,
  "page_id": "123456789"
}
```

## Deploying to Hotglue

### Using Git URI (Recommended)

In Hotglue Connector Settings:

```yaml
Connector Name: Facebook Engagement
Type: Source (tap)
Install URI: git+https://github.com/halo-engineering/tap_facebook.git
Entry Point: tap-facebook
Branch/Tag: main  # or specific version like v1.0.0
```

### Configuration Schema

Upload [config_schema_facebook.json](./config_schema_facebook.json) in Hotglue to define the configuration UI.

### OAuth Setup in Hotglue

1. Navigate to **Admin Panel** → **OAuth Providers**
2. Create Facebook OAuth provider:
   ```yaml
   Provider Name: Facebook
   Authorization URL: https://www.facebook.com/v18.0/dialog/oauth
   Token URL: https://graph.facebook.com/v18.0/oauth/access_token
   Scopes: pages_show_list,pages_read_engagement,pages_read_user_content,read_insights
   ```
3. Link OAuth provider to your Facebook connector
4. Map tokens:
   - `access_token` → `config.refresh_token`
   - `refresh_token` → `config.refresh_token`

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests (when implemented)
pytest
```

### Local Testing

```bash
# Test discovery
tap-facebook --config config.json --discover | jq

# Test sync with pretty output
tap-facebook --config config.json --catalog catalog.json | jq -c 'select(.type == "RECORD")'

# Count records per stream
tap-facebook --config config.json --catalog catalog.json | \
  jq -c 'select(.type == "RECORD") | .stream' | \
  sort | uniq -c
```

### Updating the Tap

When making changes:

```bash
# Update version in setup.py
vim setup.py  # Change version='0.1.0' to version='0.2.0'

# Commit and tag
git add .
git commit -m "Add new feature"
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main --tags

# Hotglue will automatically pull updates if configured,
# or manually redeploy in Hotglue admin panel
```

## Rate Limits

Facebook Graph API has rate limits:

- **App-level**: 200 calls per hour per user
- **Page-level**: Varies by page size and ad spend

The tap implements:
- Automatic retry with exponential backoff
- Rate limit detection and handling
- Cursor-based pagination to minimize API calls

## Troubleshooting

### "Invalid OAuth access token"

**Cause**: Token expired or invalid

**Solution**:
1. Generate new long-lived token (see OAuth setup)
2. Ensure `client_id` and `client_secret` are correct for automatic refresh
3. Check token permissions include all required scopes

### "Unsupported get request"

**Cause**: Page ID is incorrect or page not accessible

**Solution**:
1. Verify Page ID in config.json
2. Ensure token has access to the page
3. Check page visibility settings

### "API rate limit exceeded"

**Cause**: Too many requests in short time

**Solution**:
1. Reduce sync frequency
2. Select fewer streams in catalog
3. Wait for rate limit window to reset (1 hour)

### No data returned

**Cause**: `start_date` may be too recent or page has no activity

**Solution**:
1. Adjust `start_date` to include data range
2. Verify page has posts/activity
3. Check stream selection in catalog.json

## API Version

This tap uses **Facebook Graph API v18.0** (released November 2023).

API changelog: https://developers.facebook.com/docs/graph-api/changelog

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-metric`)
3. Commit your changes (`git commit -am 'Add new metric'`)
4. Push to the branch (`git push origin feature/new-metric`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/halo-engineering/tap_facebook/issues)
- **Discussions**: [GitHub Discussions](https://github.com/halo-engineering/tap_facebook/discussions)

## Related Projects

- [tap-linkedin](https://github.com/halo-engineering/tap_linkedin) - LinkedIn engagement tap
- [tap-instagram](https://github.com/halo-engineering/tap_instagram) - Instagram engagement tap
- [Singer Spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md) - Singer specification
- [Hotglue](https://hotglue.com/) - Embedded iPaaS platform

## Changelog

### [0.1.0] - 2025-01-21

#### Added
- Initial release
- Posts stream with engagement metrics
- Page insights stream
- Post insights stream
- OAuth 2.0 with automatic token refresh
- Incremental syncing support
- Hotglue deployment configuration

---

Built with ❤️ by [Halo Engineering](https://github.com/halo-engineering)
