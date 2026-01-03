# Self-Service Deployment to Hotglue - tap-facebook

## ✅ You're Right! No Email Needed

Based on the Hotglue documentation at https://docs.hotglue.com/key-concepts/connectors/v1-sources/settings, you can configure custom Singer taps yourself using `availableSources.json`.

## How It Works

Hotglue allows you to override source settings (including `install_uri`) through configuration files in your project.

## Deployment Process

### Step 1: Create availableSources.json

I've created `availableSources.json` in this repository with the following configuration:

```json
[
  {
    "tap": "tap-facebook",
    "label": "Facebook Pages",
    "icon": "https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg",
    "domain": "facebook.com",
    "type": "api",
    "install_uri": "git+https://github.com/halo-engineering/tap_facebook.git",
    "connect_ui_params": {
      "client_id": {
        "label": "Facebook App ID",
        "description": "Your Facebook App ID from developers.facebook.com",
        "type": "text",
        "required": true
      },
      "client_secret": {
        "label": "Facebook App Secret",
        "description": "Your Facebook App Secret (kept secure)",
        "type": "password",
        "required": true
      },
      "refresh_token": {
        "label": "Access Token",
        "description": "Facebook access token (automatically exchanged for long-lived token)",
        "type": "password",
        "required": true
      },
      "page_id": {
        "label": "Facebook Page ID",
        "description": "The ID of the Facebook Page to sync data from",
        "type": "text",
        "required": true
      },
      "start_date": {
        "label": "Start Date",
        "description": "Date to start syncing historical data (ISO 8601 format)",
        "type": "text",
        "required": false
      }
    }
  }
]
```

### Step 2: Deploy via Hotglue Dashboard/CLI

#### Option A: Via Hotglue Dashboard (if using JupyterLab Workspace)

1. **Place file** in root directory of your Hotglue JupyterLab workspace
2. **Navigate** to Hotglue tab in toolbar
3. **Click** "Deploy ETL"
4. **Verify** that tap-facebook appears in available sources

#### Option B: Via Hotglue CLI

If you're using the Hotglue CLI:

```bash
# Install Hotglue CLI (if not already installed)
npm install -g @hotglue/cli

# Login to Hotglue
hotglue login

# Navigate to your project directory
cd /path/to/your/hotglue/project

# Copy availableSources.json to project root
cp /Users/tim/Development/Labs/tap_facebook/availableSources.json ./

# Deploy
hotglue deploy
```

#### Option C: Via Flow Configuration

According to the documentation, you can also configure this at the flow level:

1. **Navigate** to your HALO Connect flow in Hotglue dashboard
2. **Look for** "Sources" or "Connectors" configuration
3. **Add** the availableSources.json configuration through the UI
4. **Save** and apply changes

### Step 3: Verify Configuration

After deployment:

1. Go to your **HALO Connect** flow
2. Click **"Add Source"** or **"Sources"** tab
3. Look for **"Facebook Pages"** in the connector list
4. It should now appear with your custom configuration

## Key Configuration Fields Explained

### install_uri

```json
"install_uri": "git+https://github.com/halo-engineering/tap_facebook.git"
```

This tells Hotglue to install your custom tap from GitHub instead of using a default/built-in connector.

**Variations you can use:**

**Specific version/tag:**
```json
"install_uri": "git+https://github.com/halo-engineering/tap_facebook.git@v0.1.0"
```

**Specific branch:**
```json
"install_uri": "git+https://github.com/halo-engineering/tap_facebook.git@main"
```

**Private repository:**
```json
"install_uri": "git+https://github.com/halo-engineering/tap_facebook.git",
"is_private_repo": true
```
(Requires git access token configured in Hotglue)

### type

```json
"type": "api"
```

Since you're not using OAuth through Hotglue's built-in OAuth flow (your tap handles OAuth internally), use `"api"` type. This shows a simple form for credentials.

**Alternative:** If you wanted Hotglue to handle OAuth flow:
```json
"type": "oauth",
"tap_url": "https://www.facebook.com/v24.0/dialog/oauth",
"auth_url": "https://graph.facebook.com/v24.0/oauth/access_token"
```

But since your tap already handles OAuth internally, `"api"` is correct.

### connect_ui_params

These define the form fields users see when connecting the source:

- **type: "text"** - Regular text input
- **type: "password"** - Password/secret input (hidden characters)
- **type: "boolean"** - Checkbox
- **type: "select"** - Dropdown menu
- **type: "list"** - Array of values

## After Deployment

Once deployed, when users add the "Facebook Pages" source to their flow, they'll see a form with:

1. **Facebook App ID** (text field)
2. **Facebook App Secret** (password field)
3. **Access Token** (password field)
4. **Facebook Page ID** (text field)
5. **Start Date** (text field, optional)

These values get passed to your tap's config.

## Testing the Configuration

### 1. Check Source Appears

```
HALO Connect → Sources → Add Source → Should see "Facebook Pages"
```

### 2. Add Source to Flow

Click "Facebook Pages" and you should see the custom form with your fields.

### 3. Fill in Credentials

Use test credentials:
- App ID from developers.facebook.com
- App Secret from your Facebook App
- Access token from Graph API Explorer
- Your test page ID

### 4. Run Discovery

Hotglue should run:
```bash
tap-facebook --config config.json --discover
```

### 5. Select Streams

You should see:
- posts
- page_insights

### 6. Run Sync

Test a sync with a small date range to verify data flows correctly.

## Troubleshooting

### "Source not found" after deployment

**Check:**
- Is `availableSources.json` in the correct location?
- Did deployment succeed?
- Is the tap name correct (`tap-facebook`)?

**Solution:**
- Verify file location in project root
- Check deployment logs
- Ensure tap name matches exactly

### "Failed to install tap"

**Check:**
- Is repository public?
- Is `install_uri` correct?
- Does repository have valid `setup.py`?

**Solution:**
- Verify repo URL: https://github.com/halo-engineering/tap_facebook
- Test installation locally: `pip install git+https://github.com/halo-engineering/tap_facebook.git`

### "Executable not found"

**Check:**
- Entry point in setup.py correct?
- Executable name matches?

**Solution:**
- Verify setup.py has: `'tap-facebook=tap_facebook.tap:main'`
- Ensure tap name in availableSources.json matches

### Custom fields don't appear

**Check:**
- Did you redeploy after changing availableSources.json?
- Is the structure valid JSON?

**Solution:**
- Validate JSON syntax
- Redeploy configuration
- Clear browser cache and reload

## Documentation References

- **Source Settings:** https://docs.hotglue.com/key-concepts/connectors/v1-sources/settings
- **Custom Params:** https://docs.hotglue.com/docs/custom-params
- **Singer SDK:** https://docs.hotglue.com/custom-connectors/taps

## Alternative: Contact Support

If self-service deployment doesn't work or you can't find where to place `availableSources.json`:

**Email:** hello@hotglue.xyz

**Message:**
```
Hi Hotglue Team,

I'm trying to deploy a custom Singer tap (tap-facebook) using availableSources.json as described in your documentation.

Could you please clarify:
1. Where should I place the availableSources.json file in my workspace?
2. How do I deploy it to make the tap available in my HALO Connect flow?
3. Is there a UI or CLI command for this?

Repository: https://github.com/halo-engineering/tap_facebook
Install URI: git+https://github.com/halo-engineering/tap_facebook.git

Thank you!
```

## Summary

**What you need:**
1. ✅ `availableSources.json` (created)
2. ✅ Public GitHub repository (ready)
3. ✅ Working tap with setup.py (tested)

**Next step:**
- Deploy `availableSources.json` to your Hotglue workspace
- OR contact Hotglue support to clarify the deployment process

**Advantage of this approach:**
- Self-service (no waiting for support)
- Full control over configuration
- Easy to update (just redeploy)

The exact deployment method depends on your Hotglue workspace setup (JupyterLab, CLI, or dashboard UI).
