// Supabase Edge Function: kit-sync
// Subscribes new users to Kit (ConvertKit) mailing list
// Triggered by database webhook on INSERT to public.users

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const KIT_API_BASE = "https://api.convertkit.com/v3";

interface WebhookPayload {
  type: "INSERT" | "UPDATE" | "DELETE";
  table: string;
  record: {
    id: string;
    email: string;
    name?: string;
    first_name?: string;
    confirmed?: boolean;
  };
  schema: string;
  old_record: null | Record<string, unknown>;
}

serve(async (req: Request) => {
  // Only allow POST requests
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Get secrets from environment
  const KIT_API_SECRET = Deno.env.get("KIT_API_SECRET");
  const KIT_FORM_ID = Deno.env.get("KIT_FORM_ID");

  if (!KIT_API_SECRET || !KIT_FORM_ID) {
    console.error("Missing required environment variables: KIT_API_SECRET or KIT_FORM_ID");
    return new Response(
      JSON.stringify({ error: "Server configuration error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  try {
    // Parse the webhook payload
    const payload: WebhookPayload = await req.json();
    
    console.log(`Received ${payload.type} event for table: ${payload.table}`);

    // Only process INSERT events
    if (payload.type !== "INSERT") {
      console.log(`Skipping non-INSERT event: ${payload.type}`);
      return new Response(
        JSON.stringify({ message: "Skipped: not an INSERT event" }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      );
    }

    const { email, name, first_name } = payload.record;

    if (!email) {
      console.error("No email found in record");
      return new Response(
        JSON.stringify({ error: "No email in payload" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    // Use name or first_name field
    const subscriberName = first_name || name || "";

    console.log(`Subscribing ${email} (${subscriberName}) to Kit form ${KIT_FORM_ID}`);

    // Subscribe to Kit form
    const kitResponse = await fetch(
      `${KIT_API_BASE}/forms/${KIT_FORM_ID}/subscribe`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          api_secret: KIT_API_SECRET,
          email: email,
          first_name: subscriberName,
        }),
      }
    );

    const kitData = await kitResponse.json();

    if (!kitResponse.ok) {
      console.error(`Kit API error: ${JSON.stringify(kitData)}`);
      return new Response(
        JSON.stringify({ 
          error: "Kit subscription failed", 
          details: kitData 
        }),
        { status: kitResponse.status, headers: { "Content-Type": "application/json" } }
      );
    }

    console.log(`Successfully subscribed ${email} to Kit. Subscriber ID: ${kitData.subscription?.subscriber?.id}`);

    return new Response(
      JSON.stringify({
        success: true,
        message: `Subscribed ${email} to Kit`,
        subscriber_id: kitData.subscription?.subscriber?.id,
      }),
      { status: 200, headers: { "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error(`Error processing webhook: ${error.message}`);
    return new Response(
      JSON.stringify({ error: "Internal server error", details: error.message }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }
});
