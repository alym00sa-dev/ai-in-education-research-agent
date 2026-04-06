import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { password } = await request.json();

  // Get password from environment variable
  const correctPassword = process.env.DASHBOARD_PASSWORD || 'changeme';

  if (password === correctPassword) {
    const response = NextResponse.json({ success: true });

    // Set authentication cookie that expires in 7 days
    response.cookies.set('auth', 'authenticated', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 7, // 7 days
      path: '/',
    });

    return response;
  }

  return NextResponse.json({ success: false }, { status: 401 });
}
