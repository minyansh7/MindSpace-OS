# DNS hardening — `mindspaceos.com`

Copy-paste records for the Cloudflare DNS panel after the domain is registered and attached to the `mindspace-os` Pages project. Total time to set up: ~10 min.

Dashboard:
> https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/mindspaceos.com/dns/records

---

## 1. Custom domain → Pages (auto-created when you attach)

When you click **Set up a custom domain** in the Pages dashboard and enter `mindspaceos.com`, Cloudflare auto-creates this:

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| CNAME | `mindspaceos.com` | `mindspace-os.pages.dev` | Proxied (orange cloud) | Auto |
| CNAME | `www.mindspaceos.com` | `mindspace-os.pages.dev` | Proxied | Auto |

**You don't have to add these manually** — CF Pages does it. Verify they exist after clicking the Pages dashboard "Set up a custom domain" button.

---

## 2. Force HTTPS (one toggle)

> https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/mindspaceos.com/ssl-tls/edge-certificates

Toggle **Always Use HTTPS** ON. CF redirects every `http://` request to `https://` at the edge.

---

## 3. DNSSEC (one toggle)

> https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/mindspaceos.com/dns/settings

Toggle **DNSSEC** ON.

If domain registered via **Cloudflare Registrar**: DS record is published automatically. Done.

If domain registered **elsewhere** (Namecheap, Porkbun, etc.): CF gives you a DS record. Copy it to your registrar's DNSSEC panel. Propagation: a few hours.

---

## 4. Null MX — block email phishing as `@mindspaceos.com`

You're not running email on this domain (yet). A null MX explicitly tells the world "no mail accepted here," so spoofers can't send `from:noreply@mindspaceos.com` and have it pass basic checks.

Add **one MX record**:

| Type | Name | Mail server | Priority | TTL |
|------|------|-------------|----------|-----|
| MX | `@` | `.` (just a single dot) | 0 | Auto |

The `.` (dot) as mail server is the RFC 7505 null-MX standard. Most registrars validate it as a real entry.

---

## 5. SPF — declare "no one can send mail as this domain"

Add **one TXT record**:

| Type | Name | Content | TTL |
|------|------|---------|-----|
| TXT | `@` | `v=spf1 -all` | Auto |

The `-all` (hard-fail) tells receiving servers: reject anything claiming to be from `mindspaceos.com`. Combined with null MX, this kills brand impersonation cold.

---

## 6. DMARC `p=reject` — enforce SPF + report attempts

Add **one TXT record**:

| Type | Name | Content | TTL |
|------|------|---------|-----|
| TXT | `_dmarc` | `v=DMARC1; p=reject; rua=mailto:takedown@mindspaceos.com; ruf=mailto:takedown@mindspaceos.com; fo=1` | Auto |

`p=reject` = mail servers should drop spoofed messages outright. `rua`/`ruf` = aggregate + forensic reports of spoofing attempts get sent to the reporting inbox (so you'll see attacks in real time).

⚠️ **You need a working `takedown@mindspaceos.com` inbox** for the reports to land somewhere. Set it up via Cloudflare Email Routing (free):

> https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/mindspaceos.com/email/routing

Add a routing rule: `takedown@mindspaceos.com` → forward to your real inbox (e.g., Gmail).

---

## 7. (Optional) Brand routing addresses

Same Email Routing panel — add forwarding addresses you'll publish:

- `takedown@mindspaceos.com` → your real inbox (already required for DMARC above)
- `hello@mindspaceos.com` → your real inbox (Substack-friendly contact)
- `press@mindspaceos.com` → your real inbox (for outreach replies)

---

## Verification

After you save all records, run these from any terminal:

```bash
# 1. Site loads on the canonical domain over HTTPS
curl -sI https://mindspaceos.com | head -1
# Expect: HTTP/2 200

# 2. http:// redirects to https://
curl -sI http://mindspaceos.com | grep -i "location"
# Expect: location: https://mindspaceos.com/

# 3. SPF record present
dig +short TXT mindspaceos.com | grep spf1
# Expect: "v=spf1 -all"

# 4. DMARC record present
dig +short TXT _dmarc.mindspaceos.com
# Expect: "v=DMARC1; p=reject; ..."

# 5. Null MX present
dig +short MX mindspaceos.com
# Expect: 0 .

# 6. DNSSEC active
dig +dnssec mindspaceos.com | grep -i "RRSIG"
# Expect: at least one RRSIG line (presence = signed)
```

If all six pass, the domain is hardened.

---

## Then ping me

Once the domain is live and verified, I can:

1. Run a `curl -I https://mindspaceos.com` smoke check
2. Update README + CLAUDE.md to drop the "(Cloudflare Pages preview at … as fallback)" note (clean to canonical domain only)
3. Verify the OG image URLs in `dist/` resolve to absolute `https://mindspaceos.com/og/*.png` (Astro should already do this since `astro.config.mjs:site` is set)
4. Submit `https://mindspaceos.com/sitemap-index.xml` to Google Search Console for indexing

That last step matters for the niche-research distribution strategy — Google Dataset Search needs to crawl the canonical URL, not the Pages preview.
