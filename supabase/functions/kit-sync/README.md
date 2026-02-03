# Kit-Sync Edge Function

Automatically subscribes new users to your Kit (ConvertKit) mailing list when they sign up.

## Prerequisites

1. Get your Kit Form ID from: https://app.convertkit.com/forms
2. Get your Kit API Secret from: https://app.convertkit.com/account_settings/developer_settings

## CLI Commands

### 1. Login to Supabase (if not already)

```bash
supabase login
```

### 2. Link your project

```bash
cd /Users/agu/Desktop/holt
supabase link --project-ref zyyuwsvnkhpmvoftlljb
```

### 3. Set the secrets

```bash
# Replace with your actual values
supabase secrets set KIT_API_SECRET="your_kit_api_secret"
supabase secrets set KIT_FORM_ID="your_kit_form_id"
```

### 4. Deploy the function

```bash
supabase functions deploy kit-sync
```

### 5. Verify deployment

```bash
supabase functions list
```

## Database Webhook SQL

Run this in your Supabase SQL Editor to create the webhook trigger:

```sql
-- Enable the pg_net extension (required for webhooks)
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Create the webhook trigger function
CREATE OR REPLACE FUNCTION public.handle_new_user_kit_sync()
RETURNS TRIGGER AS $$
DECLARE
  payload JSONB;
  function_url TEXT;
BEGIN
  -- Build the payload
  payload := jsonb_build_object(
    'type', TG_OP,
    'table', TG_TABLE_NAME,
    'schema', TG_TABLE_SCHEMA,
    'record', row_to_json(NEW),
    'old_record', CASE WHEN TG_OP = 'UPDATE' THEN row_to_json(OLD) ELSE NULL END
  );

  -- Get your function URL (replace with your actual project ref)
  function_url := 'https://zyyuwsvnkhpmvoftlljb.supabase.co/functions/v1/kit-sync';

  -- Call the edge function
  PERFORM net.http_post(
    url := function_url,
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
    ),
    body := payload
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create the trigger on the users table
DROP TRIGGER IF EXISTS on_user_created_kit_sync ON public.users;

CREATE TRIGGER on_user_created_kit_sync
  AFTER INSERT ON public.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user_kit_sync();
```

## Alternative: Using Supabase Dashboard

1. Go to **Database > Webhooks** in your Supabase dashboard
2. Click **Create Webhook**
3. Configure:
   - **Name**: `kit-sync`
   - **Table**: `users`
   - **Events**: `INSERT`
   - **Type**: `Supabase Edge Function`
   - **Edge Function**: `kit-sync`

## Testing

Test the function manually:

```bash
curl -X POST \
  'https://zyyuwsvnkhpmvoftlljb.supabase.co/functions/v1/kit-sync' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_ANON_KEY' \
  -d '{
    "type": "INSERT",
    "table": "users",
    "schema": "public",
    "record": {
      "id": "test-123",
      "email": "test@example.com",
      "name": "Test User"
    },
    "old_record": null
  }'
```

## Logs

View function logs:

```bash
supabase functions logs kit-sync
```
