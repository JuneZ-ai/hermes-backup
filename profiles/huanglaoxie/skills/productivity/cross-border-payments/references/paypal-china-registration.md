# PayPal China Registration Guide

## Correct URL

**https://www.paypal.com/c2/**

- `/c2/` = China region (simplified Chinese) — this is the right URL for mainland users
- `paypal.com/hk/` = Hong Kong (HKD, different rules, not for mainland users)
- Bare `paypal.com/` = international (English, may auto-redirect)
- If user lands on English page → tell them to manually navigate to `/c2/`

## Registration steps

### Step 1: Account creation
1. Open `https://www.paypal.com/c2/`
2. Click **注册** → **个人账户** (Personal Account)
3. Fill in:
   - **Email**: QQ / Gmail / Outlook / ProtonMail all work. **But** if the email is already taken by someone else on PayPal, you cannot use it — use a fresh email instead.
   - **Mobile**: +86 number (China mainland)
   - **Password**: Separate password from your email (don't reuse)
4. Check inbox, click verification link

### Step 2: Identity info
- **Name must match 身份证 (Chinese ID card) exactly** — Chinese characters, no nicknames, no English names
- **Address**: Any valid mainland China address
- **ID type**: 身份证 (Chinese ID)
- **Phone**: Already verified in Step 1

### Step 3: Bank card binding
Location: **钱包 (Wallet)** → **关联卡或银行 (Link a card or bank)**

1. Enter your **银联储蓄卡 (UnionPay debit card)** number
2. PayPal sends a small verification charge (¥1-10, auto-refunded within 24h)
3. Enter the SMS code from your bank to confirm

**Important**: This is a pre-authorization hold, NOT a real charge. It falls off automatically.

Without this step: account can RECEIVE money but CANNOT WITHDRAW.

### Step 4: Set up AliPay withdrawal
Location: **设置 (Settings)** → **钱包 (Wallet)** → **提现 (Withdraw)**

1. Select **提现到支付宝 (Withdraw to Alipay)**
2. Enter the phone number linked to your AliPay account
3. Confirm via SMS code

This completes the loop: receive USD → withdraw to AliPay → CNY arrives in your Alipay balance → transfer to bank card.

PayPal handles the USD→CNY conversion at their FX rate (~2-3% worse than market).

### Step 5: Generate paypal.me link
1. Go to `paypal.me` or find it in the PayPal app menu
2. Create: `paypal.me/YourName`
3. User shares this link with overseas customers

## Pitfall: "我的邮箱被抢注了"

Someone else used your Gmail/QQ email to register their own PayPal account.

**Don't waste time recovering it.** Here's why:
- PayPal identifies the account owner by ID 身份证 number + phone, NOT by email
- The hijacker's ID is different from yours — the account is legally theirs, not yours
- Trying to "recover" an account that isn't yours by ID will fail at identity verification

**Fix**: Register a new email (Outlook / ProtonMail / iCloud hide-my-email) and use that. The new email + your ID + your phone = your new PayPal account, fully functional.

## Verification gotchas

| Symptom | Cause | Fix |
|---------|-------|-----|
| Account "limited" after signup | New account flag, ~30% of China registrations | Upload ID card photo → wait ~24h |
| First payment >¥500 held for 21 days | New account risk control | Start with small amounts |
| Bank card binding fails | Card may not support online payments | Call bank to enable; try a different card |
| "This email is already registered" | Someone used your email | Use a new email (see above) |
| AliPay withdrawal not showing up | Account may not be fully verified yet | Complete Steps 1-3 first |

## Withdrawal limits

- Max per withdrawal (AliPay): ~$10,000 USD equivalent
- Multiple withdrawals per day: Supported
- FX rate: PayPal's rate has ~2-3% margin over market. Acceptable for low volume; for >$5k/mo consider bank transfer withdrawal instead
- Bank transfer to 银联卡: Also available as alternative to AliPay

## When PayPal isn't enough

- Selling digital products with auto-delivery → add **LemonSqueezy** (handles tax, VAT, GST)
- Only have Chinese mainland customers → skip PayPal, just use **WeChat Pay**
- Need recurring subscriptions → **LemonSqueezy** supports subscriptions natively
