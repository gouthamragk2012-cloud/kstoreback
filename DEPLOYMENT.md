# Deployment Guide

## Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/gouthamragk2012-cloud/kstoreback.git
cd kstoreback
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your actual database credentials
```

5. **Create database tables**
```bash
python reset_tables.py
```

6. **Run the application**
```bash
python app.py
```

Server will start on `http://localhost:5000`

## Production Deployment

### Using Gunicorn (Linux/Mac)

1. **Install Gunicorn**
```bash
pip install gunicorn
```

2. **Run with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Render.com

1. **Create `render.yaml`** (already included)
2. Connect your GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy!

### Using Railway.app

1. Connect GitHub repo
2. Add PostgreSQL database
3. Set environment variables
4. Deploy automatically

### Using Heroku

1. **Create Procfile**
```
web: gunicorn app:app
```

2. **Deploy**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku master
```

## Environment Variables for Production

Make sure to set these in your hosting platform:

- `DB_HOST` - Database host
- `DB_PORT` - Database port (usually 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `SECRET_KEY` - Strong random string (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `JWT_SECRET_KEY` - Strong random string (use: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `CORS_ORIGINS` - Allowed origins (e.g., `https://yourdomain.com`)

## Security Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY to strong random values
- [ ] Set proper CORS_ORIGINS (not *)
- [ ] Use HTTPS in production
- [ ] Keep .env file out of version control
- [ ] Use environment variables for all sensitive data
- [ ] Enable database SSL connection
- [ ] Set up database backups
- [ ] Monitor logs and errors
- [ ] Rate limiting (consider Flask-Limiter)
- [ ] Input validation on all endpoints

## Database Migrations

For schema changes, create migration scripts in a `migrations/` folder:

```python
# migrations/001_add_column.py
def upgrade(cursor):
    cursor.execute("ALTER TABLE users ADD COLUMN new_field VARCHAR(100)")

def downgrade(cursor):
    cursor.execute("ALTER TABLE users DROP COLUMN new_field")
```

## Monitoring

Consider adding:
- Sentry for error tracking
- New Relic for performance monitoring
- CloudWatch/DataDog for logs
- Uptime monitoring (UptimeRobot, Pingdom)

## Backup Strategy

1. **Database backups**: Daily automated backups
2. **Code backups**: Git repository
3. **Environment configs**: Secure vault (1Password, AWS Secrets Manager)

## Scaling

For high traffic:
1. Use connection pooling (already implemented)
2. Add Redis for caching
3. Use CDN for static assets
4. Horizontal scaling with load balancer
5. Database read replicas
6. Queue system for async tasks (Celery + Redis)
