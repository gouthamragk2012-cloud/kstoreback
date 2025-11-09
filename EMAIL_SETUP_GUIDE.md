# Email Verification Setup Guide

## Step 1: Set Up Gmail App Password

1. **Go to your Google Account**: https://myaccount.google.com/
2. **Enable 2-Step Verification** (if not already enabled):
   - Go to Security → 2-Step Verification
   - Follow the steps to enable it

3. **Create App Password**:
   - Go to Security → 2-Step Verification → App passwords
   - Or directly: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or Other)
   - Click "Generate"
   - **Copy the 16-character password** (you'll need this)

## Step 2: Update .env File

Add these lines to your `KstoreBack/.env` file:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `your-16-char-app-password` with the App Password you generated

## Step 3: Restart Backend Server

After updating .env, restart your Flask server:
```bash
python app.py
```

## API Endpoints Created

### 1. Send Verification Code
```
POST /api/verification/send-code
Headers: Authorization: Bearer <JWT_TOKEN>
```

### 2. Verify Code
```
POST /api/verification/verify-code
Headers: Authorization: Bearer <JWT_TOKEN>
Body: { "code": "123456" }
```

### 3. Check Verification Status
```
GET /api/verification/status
Headers: Authorization: Bearer <JWT_TOKEN>
```

## Testing

1. Register a new user
2. Login to get JWT token
3. Call `/api/verification/send-code` - Check your email
4. Enter the 6-digit code in `/api/verification/verify-code`
5. User is now verified!

## Troubleshooting

**Email not sending?**
- Check if 2-Step Verification is enabled
- Verify App Password is correct (no spaces)
- Check Gmail account allows less secure apps
- Check spam folder

**Code expired?**
- Codes expire after 15 minutes
- Request a new code using `/api/verification/send-code`

## Next Steps

Now we need to create the frontend pages:
1. Verification page (/verify-email)
2. Update registration flow
3. Add verification check on login
