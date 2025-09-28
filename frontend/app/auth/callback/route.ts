import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const error = requestUrl.searchParams.get('error')

  // If there's an error, redirect back to the main page with error parameters
  if (error) {
    return NextResponse.redirect(`${requestUrl.origin}/?auth_error=${encodeURIComponent(error)}`)
  }

  // If there's a code, redirect back to main page - the client-side code will handle the exchange
  if (code) {
    return NextResponse.redirect(`${requestUrl.origin}/?code=${code}`)
  }

  // Default redirect to main page
  return NextResponse.redirect(requestUrl.origin)
}