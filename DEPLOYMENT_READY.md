# tap-facebook - Ready for Hotglue Deployment! 🚀

## ✅ Status: READY TO DEPLOY

Your tap-facebook is fully prepared and tested for deployment to Hotglue.

## What's Been Completed

### ✅ Repository Setup
- **Repository:** https://github.com/halo-engineering/tap_facebook
- **Status:** Public, pushed, and accessible
- **Latest commit:** Update repository URL and add deployment files
- **Version:** v0.1.0

### ✅ Installation Tested
- Tested git installation: `pip install git+https://github.com/halo-engineering/tap_facebook.git`
- Verified executable: `tap-facebook` command works
- Confirmed entry point is correctly configured

### ✅ Documentation Created
- README.md with full tap documentation
- HOTGLUE_DEPLOYMENT.md with deployment guide
- hotglue_source_definition.json ready to submit
- HOTGLUE_SUBMISSION_EMAIL.md with email template

### ✅ Configuration Files
- setup.py correctly configured
- Entry point: `tap-facebook=tap_facebook.tap:main`
- All dependencies specified
- Public repository URL updated

## Next Steps: Deploy to Hotglue

You have **two options** for deployment:

### Option 1: Email Hotglue Support (Recommended)

**Email:** hello@hotglue.xyz

**Template:** See `HOTGLUE_SUBMISSION_EMAIL.md`

**Attach:** `hotglue_source_definition.json`

**Expected timeline:** 1-2 business days for Hotglue to add the source

### Option 2: Self-Service (If Available)

If Hotglue dashboard has a self-service option:

1. Navigate to Sources/Connectors section
2. Look for "Add Custom Source" or "Create Source Definition"
3. Upload or paste the JSON from `hotglue_source_definition.json`
4. Save and publish

## What Hotglue Will Do

When they receive your request, Hotglue will:

1. **Add source definition** to your workspace
2. **Install tap** using: `git+https://github.com/halo-engineering/tap_facebook.git`
3. **Create configuration UI** with the fields you specified:
   - Facebook App ID
   - Facebook App Secret
   - Access Token
   - Facebook Page ID
   - Start Date (optional)

## After Hotglue Adds the Source

### Step 1: Configure in HALO Connect

1. Go to your **HALO Connect** flow
2. Navigate to **Sources** tab
3. Find **"Facebook Pages"** in the connector list
4. Click to add it to your flow

### Step 2: Enter Credentials

You'll see a configuration form with these fields:

**Facebook App ID:** `YOUR_APP_ID`
- Get from: https://developers.facebook.com/apps/
- This is the App ID you created earlier

**Facebook App Secret:** `YOUR_APP_SECRET`
- Get from: Facebook App → Settings → Basic
- Click "Show" to reveal the secret

**Access Token:** `SHORT_LIVED_ACCESS_TOKEN`
- Get from: https://developers.facebook.com/tools/explorer/
- Select your app
- Click "Get Token" → "Get Page Access Token"
- Select your page
- Copy the token
- The tap will automatically exchange it for a long-lived token

**Facebook Page ID:** `123456789012345`
- Get from: Your Facebook Page → About → Page Transparency
- Or use numeric ID from page URL

**Start Date:** `2025-01-01T00:00:00Z` (optional)
- Controls how far back to sync historical data
- Leave as default or customize

### Step 3: Select Streams

Choose which data streams to sync:
- ✅ **posts** - Posts with engagement metrics (likes, comments, shares, reactions)
- ✅ **page_insights** - Page-level analytics and insights

### Step 4: Configure Destination

Select where to send the data:
- Database/Data warehouse
- Or another destination in your flow

### Step 5: Run Sync

Click **"Test"** or **"Run"** to start syncing data!

## Expected Streams Output

### posts Stream

Each record contains:
```json
{
  "id": "123456789_987654321",
  "message": "Post content here...",
  "created_time": "2025-01-02T10:30:00+0000",
  "updated_time": "2025-01-02T15:45:00+0000",
  "permalink_url": "https://www.facebook.com/...",
  "likes_count": 150,
  "comments_count": 25,
  "shares_count": 10,
  "reactions_count": 175,
  "reactions": {
    "like": 120,
    "love": 30,
    "wow": 15,
    "haha": 10
  }
}
```

### page_insights Stream

Each record contains:
```json
{
  "name": "page_impressions",
  "period": "day",
  "values": [
    {
      "value": 1234,
      "end_time": "2025-01-02T08:00:00+0000"
    }
  ],
  "title": "Daily Total Impressions",
  "description": "The number of times any content from your Page or about your Page entered a person's screen",
  "id": "123456789/insights/page_impressions/day"
}
```

## Features Your Tap Provides

### ✅ OAuth 2.0 Authentication
- Automatic token exchange (short-lived → long-lived)
- Token refresh handling
- No manual token management needed

### ✅ Incremental Syncing
- State-based replication
- Only syncs new/updated data after initial sync
- Uses `created_time` and `updated_time` for posts
- Uses `end_time` for insights

### ✅ Comprehensive Engagement Metrics
- Likes, comments, shares, reactions
- Detailed reaction breakdown (like, love, wow, haha, sad, angry)
- Total counts and summaries

### ✅ Rate Limit Handling
- Automatic retry with exponential backoff
- Respects Facebook API rate limits
- Cursor-based pagination for large datasets

## Troubleshooting

### If Tap Installation Fails

**Check:**
- Is repository public?
- Does `setup.py` exist at repo root?
- Can you install locally with pip?

**Test:**
```bash
pip install git+https://github.com/halo-engineering/tap_facebook.git
```

### If Authentication Fails

**Check:**
- Is App ID correct?
- Is App Secret correct?
- Is access token valid and not expired?
- Does token have access to the specified page?
- Does Facebook App have required permissions?

**Required Facebook Permissions:**
- pages_show_list
- pages_read_engagement
- pages_read_user_content
- read_insights

### If No Data Syncs

**Check:**
- Does the page have posts in the specified date range?
- Is the page ID correct?
- Does the access token have access to this page?
- Are the streams selected in Hotglue?

### If Sync Fails

**Check logs for:**
- API errors (check Facebook App status)
- Rate limiting (may need to slow down sync)
- Permission errors (verify Facebook App permissions)
- Token expiration (regenerate access token)

## Rate Limiting Considerations

Facebook heavily throttles API requests. Your tap includes:
- Exponential backoff retry logic
- Cursor-based pagination (reduces API calls)
- Request batching where possible

**Best practices:**
- Start with small date ranges
- Monitor sync performance
- Consider Facebook Business API for higher limits

## Maintenance

### Updating the Tap

To update the tap after Hotglue deploys it:

1. Make changes to your code
2. Commit and push to GitHub
3. Tag a new version: `git tag -a v0.2.0 -m "Description"`
4. Push tag: `git push origin v0.2.0`
5. Contact Hotglue to update install_uri to reference new version:
   ```
   git+https://github.com/halo-engineering/tap_facebook.git@v0.2.0
   ```

Or use `@main` to always get latest:
```
git+https://github.com/halo-engineering/tap_facebook.git@main
```

### Monitoring

Watch for:
- Facebook Graph API version updates (currently v24.0)
- Permission changes in Facebook App Review
- Token expiration (long-lived tokens expire after ~60 days)
- Rate limit changes

## Success Metrics

You'll know it's working when:
- ✅ Tap appears in Hotglue Sources list
- ✅ Configuration form shows custom fields
- ✅ Test connection succeeds
- ✅ Discovery finds `posts` and `page_insights` streams
- ✅ Sync runs successfully
- ✅ Data appears in destination
- ✅ Incremental sync maintains state correctly
- ✅ OAuth token refresh works automatically

## What's Next

After tap-facebook is deployed and working:

1. **Deploy tap-linkedin**
   - Same process
   - Repository ready at separate location
   - Source definition similar to Facebook

2. **Deploy tap-instagram**
   - Same process
   - Uses Facebook Graph API (like Facebook)
   - Similar OAuth flow

3. **Set up automated syncs**
   - Configure sync schedule in Hotglue
   - Monitor for errors
   - Set up alerting

## Repository Files

### Core Files
- `tap_facebook/` - Source code directory
- `setup.py` - Package configuration
- `README.md` - Tap documentation
- `LICENSE` - MIT License

### Configuration Examples
- `config.example.json` - Example configuration
- `catalog.example.json` - Example catalog
- `config_schema_facebook.json` - JSON schema for config

### Deployment Files
- `hotglue_source_definition.json` - Ready to submit to Hotglue
- `HOTGLUE_SUBMISSION_EMAIL.md` - Email template
- `HOTGLUE_DEPLOYMENT.md` - Deployment guide
- `DEPLOYMENT_READY.md` - This file

## Summary

**Status:** ✅ READY TO DEPLOY

**Repository:** https://github.com/halo-engineering/tap_facebook

**Install URI:** `git+https://github.com/halo-engineering/tap_facebook.git`

**Executable:** `tap-facebook`

**Next Action:** Email Hotglue support (hello@hotglue.xyz) with the source definition

**Expected Timeline:**
- Email sent: Today
- Hotglue response: 1-2 business days
- Source added: 1-2 business days
- Testing in HALO Connect: Same day after source is added
- Production sync: Same day

**Your advantage over pre-built connectors:**
- ✅ OAuth 2.0 with automatic token refresh
- ✅ Incremental syncing
- ✅ Detailed engagement metrics
- ✅ Full control and customization
- ✅ Open source and maintainable

You're ready to go! 🎉
