import { NextRequest, NextResponse } from 'next/server';

// Conversion tracking endpoint
// Tracks important user actions like wallet creation, first investment, etc.
export async function POST(request: NextRequest) {
  try {
    const data = await request.json();
    const { event, timestamp, session } = data;

    // Validate
    if (!event || !timestamp) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    console.log('[Conversion Tracking]', {
      event,
      timestamp,
      session,
      ip: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip')
    });

    // TODO: Send to Queen AI backend for analysis
    // TODO: Store in database for admin dashboard
    // TODO: Trigger notifications for high-value conversions

    // Important conversion events:
    // - wallet_education_started: User wants to learn about wallets
    // - wallet_help_requested: User clicked "Get Help" from Teacher Bee
    // - get_wallet_clicked: User clicked "Get MetaMask"
    // - has_wallet: User said they have a wallet
    // - wallet_connected: User successfully connected wallet
    // - first_investment: User made their first investment
    // - otc_purchase_requested: User requested OTC purchase

    // High-value conversions (notify admin immediately)
    const highValueEvents = [
      'wallet_connected',
      'first_investment',
      'otc_purchase_requested'
    ];

    if (highValueEvents.includes(event)) {
      // TODO: Send real-time notification to admin
      console.log(`[HIGH VALUE CONVERSION] ${event}`);
    }

    // Crypto convert tracking (new users learning about wallets)
    const cryptoConvertEvents = [
      'wallet_education_started',
      'wallet_help_requested',
      'get_wallet_clicked'
    ];

    if (cryptoConvertEvents.includes(event)) {
      console.log(`[CRYPTO CONVERT] Potential new Web3 user: ${event}`);
      // This data is valuable - shows we're growing the crypto ecosystem!
    }

    // Forward to Queen AI for analysis
    try {
      const queenApiUrl = process.env.NEXT_PUBLIC_QUEEN_API_URL || 'http://localhost:8001';
      await fetch(`${queenApiUrl}/api/analytics/conversion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event,
          timestamp,
          session,
          source: 'frontend'
        })
      });
    } catch (queenError) {
      // Queen AI might be offline, don't fail the request
      console.error('[Conversion] Failed to forward to Queen AI:', queenError);
    }

    return NextResponse.json({
      success: true,
      message: 'Conversion tracked'
    });

  } catch (error) {
    console.error('[Conversion Tracking Error]', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// GET endpoint for admin dashboard to view conversion stats
export async function GET(request: NextRequest) {
  try {
    // TODO: Implement admin authentication
    // TODO: Query database for conversion stats
    // TODO: Return aggregated data

    return NextResponse.json({
      message: 'Conversion stats endpoint (admin only)',
      // Example data structure:
      stats: {
        wallet_education_started: 0,
        wallet_help_requested: 0,
        get_wallet_clicked: 0,
        has_wallet: 0,
        wallet_connected: 0,
        first_investment: 0,
        otc_purchase_requested: 0
      }
    });
  } catch (error) {
    console.error('[Conversion Stats Error]', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
