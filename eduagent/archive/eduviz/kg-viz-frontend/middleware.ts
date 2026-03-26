import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check if user is authenticated
  const authCookie = request.cookies.get('auth');

  // If accessing the auth API route, allow it
  if (request.nextUrl.pathname === '/api/auth') {
    return NextResponse.next();
  }

  // If authenticated, allow access
  if (authCookie?.value === 'authenticated') {
    return NextResponse.next();
  }

  // If not authenticated, redirect to login page
  if (request.nextUrl.pathname !== '/login') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
