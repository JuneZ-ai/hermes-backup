---
name: cross-border-payments
description: "Set up cross-border payment infrastructure for Chinese content creators monetizing overseas audiences. Covers payment channel selection, PayPal China registration, AliPay withdrawal, and alternative payment rails."
tags:
  - payment
  - cross-border
  - monetization
  - paypal
  - china
  - creator-economy
---

# Cross-Border Payments for Chinese Creators

## When to use this skill

- User needs to receive payments from overseas audiences (TikTok, Instagram, YouTube)
- User asks about PayPal, Stripe, LemonSqueezy, or cross-border payment setup
- User is a Chinese creator/platform operator with a Chinese bank account
- Evaluating which payment channels to offer on a landing page or Link in Bio

## Core principles

1. **Start simple, grow later** — PayPal China handles 80% of use cases day 1
2. **提现比收款更重要** — the real bottleneck isn't receiving money, it's getting it into your Chinese bank account. Always verify the withdrawal path before launching.
3. **Know the AliPay-PayPal relationship** — they're "connected" for withdrawal only (PayPal → AliPay), NOT for receiving. AliPay cannot receive overseas payments on your behalf.
4. **Avoid half-setup** — registration without bank binding leaves the account able to receive but unable to withdraw, creating frustration when the first payment arrives.
5. **Email ≠ identity** — PayPal identifies you by ID number + phone, not email. If your email is taken, use a new one (Outlook/ProtonMail), not your old credentials.

## User preferences (for this class of task)

- **Give exact URLs and concrete steps**, not overviews or descriptions. User will say "你要给我网址" if you describe instead of giving the link.
- **Make decisive recommendations**, not "should I do X or leave it?" — say "do it now, 5 minutes, no reason to delay."
- **Short confirmation messages work fine.** User communicates in single-line status updates ("注册成功给你", "也绑定了银行卡") and expects you to acknowledge and move on.
- **Blockers → pivot.** If a step is blocked (email hijacked, document not ready), recommend skipping and coming back, not dwelling or escalating.
- **Minimize clarifying questions.** One clarify per topic max. If user doesn't respond in 10 minutes, summarize and let them pick it up later.

## Payment channel quick comparison

| Channel | Best for | Withdrawal to China | Setup time |
|---------|----------|---------------------|------------|
| **PayPal China** | General overseas payments, any country | ✅ AliPay direct / 银联卡 | ~20 min |
| **WeChat Pay** | Mainland Chinese users | ✅ (domestic, no cross-border) | ~5 min |
| **LemonSqueezy** | Digital products, tax-compliant auto-handling | ✅ Bank transfer to China | ~30 min |
| **Stripe** | Western businesses, high volume | ❌ Need HK or US entity | Weeks |
| **Crypto (USDT/USDC)** | Privacy, no KYC, any geography | ✅ Via Chinese exchanges | ~15 min |

## Decision flow

```
Q: Who are your customers?
  ├─ Chinese mainland users → WeChat Pay QR code
  ├─ Overseas Chinese → PayPal China + WeChat (dual)
  └─ Western / non-Chinese → PayPal China + LemonSqueezy
       └─ Need digital product auto-delivery? → LemonSqueezy
       └─ Selling services (consultation)? → PayPal only
```

## Workflow

1. **Confirm user's identity docs** — Chinese ID holder? → PayPal China route. HK ID? → different rules.
2. **Verify email usability** — check if email is taken on PayPal. If taken → recommend fresh Outlook/ProtonMail.
3. **Walk through registration** — see `references/paypal-china-registration.md` for the full walkthrough.
4. **Don't leave half-setup** — ensure bank card is bound and withdrawal (AliPay/bank) is configured before declaring "done."
5. **Generate paypal.me link** — user shares this with customers.
6. **Revisit after first payment** — alert user about 21-day hold on new accounts, recommend starting small.

## Common pitfalls

- **Email already used by someone else**: Don't fight to reclaim it. Use a new email. PayPal identifies by ID+phone, not email. The hijacked account belongs to someone else's identity.
- **New account receives large payment**: Gets flagged for fraud review. Upload ID photo → ~24h unlock. Start with small amounts.
- **"绑卡扣款" confusion**: Verification charge is ¥1-10 pre-auth, refunded within 24h. Not a real charge.
- **One person, one account**: PayPal China allows only one personal account per ID. Multiple accounts → permanent ban.
- **AliPay withdrawal FX rate**: PayPal's FX margin is ~2-3% worse than market. Acceptable for small volumes (<$5k/mo); above that, consider withdrawing to bank card or alternative rails.
