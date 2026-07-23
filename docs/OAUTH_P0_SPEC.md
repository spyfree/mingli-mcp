# MCP OAuth P0

## Goal

Make `https://mcp.lee.locker/mcp` connectable by mainstream MCP clients through
standard OAuth, while preserving the existing paid `ML-XXXX-XXXX-XXXX-XXXX`
license-key workflow.

## Required behavior

1. Serve OAuth authorization-server metadata, protected-resource metadata, a
   token endpoint, and dynamic client registration.
2. Require OAuth 2.1 authorization code flow with S256 PKCE.
3. Show a mobile-friendly consent page where a customer enters an existing MCP
   license key. Never put that key in a URL or a readable OAuth storage record.
4. Validate the key against the shared `LICENSES` KV store and issue OAuth
   tokens whose encrypted grant properties identify the license.
5. Keep raw `Authorization: Bearer ML-...` and the internal master key working.
6. Keep MCP handshake/discovery methods free; require authorization for
   `tools/call`.
7. Return an RFC 9728 `WWW-Authenticate` challenge for unauthorized protected
   calls.
8. Apply the existing daily quota to both OAuth and raw-license tool calls.
9. Keep all non-OAuth HTTP routes proxied to the existing Python container.
10. Cover discovery, legacy authorization, consent security, PKCE exchange, and
    quota behavior with Worker-level automated tests.

## Compatibility and exclusions

- No change to astrology calculations or Python transport behavior.
- No account/password system is introduced in P0; the purchased license is the
  proof of entitlement used during consent.
- Existing MCP clients using a raw license do not need to migrate immediately.
- Quota remains a Cloudflare KV soft limit in P0.

