# Streamlit Deployment Guide

## Overview

This guide covers deploying the Gallery Image Search Agent Streamlit app to various platforms.

## Local Development

### Quick Start (3 steps)

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Ensure dependencies installed
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

**Access**: Open browser to `http://localhost:8501`

### Development Features

- **Hot Reload**: Changes auto-reload (set in .streamlit/config.toml)
- **Error Details**: Full error messages shown (runOnSave = true)
- **Debugging**: Use st.write() for debugging output
- **Session State**: Persists during development reloads

## Streamlit Cloud Deployment

### Prerequisites

1. GitHub repository with the code
2. Streamlit account (free tier available)
3. `.env` file with secrets

### Steps

#### 1. Push Code to GitHub

```bash
git add .
git commit -m "Add Streamlit deployment"
git push origin main
```

#### 2. Create Streamlit Cloud App

1. Go to https://share.streamlit.io/
2. Click "New app"
3. Select your GitHub repo
4. Set main file path: `app.py`
5. Click "Deploy"

#### 3. Add Secrets

In Streamlit Cloud dashboard:

1. Click on app → Settings
2. Go to "Secrets"
3. Add your API key:

```toml
GOOGLE_API_KEY = "your_gemini_api_key_here"
```

### Important Notes

- ✅ Free tier provides ~1GB memory
- ✅ App sleeps after 7 days of inactivity (can be woken by visiting)
- ⚠️ Don't commit `.env` to GitHub
- ✅ Use Secrets tab in Streamlit Cloud instead

### URL Format

After deployment, your app will be available at:
```
https://share.streamlit.io/username/repo-name/app.py
```

## Docker Deployment

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set environment
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py"]
```

### Docker Compose (Optional)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  streamlit-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./.env:/app/.env:ro
```

### Build and Run

```bash
# Build image
docker build -t gallery-agent .

# Run container
docker run -p 8501:8501 \
  -e GOOGLE_API_KEY="your_key_here" \
  gallery-agent

# Or with docker-compose
docker-compose up
```

**Access**: http://localhost:8501

### Cloud Docker Hosting

**Google Cloud Run**:
```bash
gcloud run deploy gallery-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=your_key
```

**AWS ECS**:
Push image to ECR and deploy with ECS service

**DigitalOcean App Platform**:
1. Connect GitHub repo
2. Set environment variables
3. Deploy

## Server Deployment (Self-Hosted)

### Using systemd

1. **Create service file** (`/etc/systemd/system/streamlit-agent.service`):

```ini
[Unit]
Description=Gallery Image Search Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/LAMForGallery
Environment="PATH=/path/to/LAMForGallery/.venv/bin"
Environment="GOOGLE_API_KEY=your_key_here"
ExecStart=/path/to/LAMForGallery/.venv/bin/streamlit run app.py --server.port=8501

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

2. **Enable and start**:

```bash
sudo systemctl enable streamlit-agent
sudo systemctl start streamlit-agent
```

3. **Monitor logs**:

```bash
sudo journalctl -u streamlit-agent -f
```

### Using Nginx as Reverse Proxy

```nginx
server {
    listen 80;
    server_name gallery-agent.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Using Apache

```apache
ProxyPreserveHost On
ProxyPass / http://localhost:8501/
ProxyPassReverse / http://localhost:8501/

RewriteEngine On
RewriteCond %{HTTP:Upgrade} websocket [NC]
RewriteCond %{HTTP:Connection} upgrade [NC]
RewriteRule ^/?(.*) "ws://localhost:8501/$1" [P,L]
```

## Performance Optimization

### 1. Caching Agent

The app already caches the agent:

```python
@st.cache_resource
def load_agent():
    agent = initialize_agent()
    return agent
```

This avoids reinitializing on every rerun.

### 2. Session State Optimization

```python
if 'messages' not in st.session_state:
    st.session_state.messages = []
```

Messages persist within a session.

### 3. Image Caching

```python
@st.cache_data
def load_image(image_path):
    return Image.open(image_path)
```

### 4. Database Connection (If Needed)

```python
@st.cache_resource
def get_db_connection():
    return sqlite3.connect("gallery.db")
```

## Security Considerations

### 1. API Key Management

**Local Development**:
- Use `.env` file (never commit)
- Load with `python-dotenv`

**Production**:
- Use environment variables
- Streamlit Cloud Secrets tab
- Docker environment variables
- systemd EnvironmentFile

### 2. Input Validation

The agent already validates inputs through LangChain tools.

### 3. HTTPS/TLS

**Local**: Use HTTP (localhost only)

**Production**:
- Enable HTTPS with Let's Encrypt
- Use reverse proxy (Nginx/Apache)
- Set secure cookies

### 4. Rate Limiting

Add to reverse proxy or middleware:

```nginx
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req zone=general burst=20;
```

### 5. Authentication (Optional)

For multi-user deployments:

```python
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    credentials,
    'cookie_name',
    'cookie_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login()

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    # Main app code
else:
    st.error('Username/password is incorrect')
```

## Troubleshooting

### App Won't Load

**Check 1**: Python dependencies
```bash
pip install -r requirements.txt
```

**Check 2**: API key configured
```bash
cat .env  # Should show GOOGLE_API_KEY=...
```

**Check 3**: Port availability
```bash
lsof -i :8501  # Linux/Mac
netstat -ano | findstr :8501  # Windows
```

### Slow Performance

- Check cache size
- Increase worker threads
- Optimize image loading
- Use CDN for static assets

### Memory Issues

- Streamlit Cloud free: 1GB limit
- Reduce image resolution
- Clear cache periodically
- Use paid tier for larger apps

### API Quota Errors

- Check daily limits on Google API Console
- Implement rate limiting
- Cache results aggressively
- Consider API quotas for team

## Monitoring

### Logs

**Local**:
```bash
streamlit run app.py --logger.level=debug
```

**Production**:
```bash
tail -f /var/log/streamlit-agent.log
```

### Metrics

Add monitoring:

```python
import time

start = time.time()
# Code here
duration = time.time() - start
st.metric("Query Time", f"{duration:.2f}s")
```

### Health Checks

```python
if st.button("Health Check"):
    try:
        agent = load_agent()
        st.success("✅ Agent loaded successfully")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
```

## Scaling

### For More Users

1. **Streamlit Cloud**: Upgrade to "Business" tier
2. **Docker + Kubernetes**: Scale replicas
3. **Load Balancer**: Distribute traffic
4. **Database**: Move to persistent storage

### For More Requests

1. **Agent Optimization**: Use cached tools
2. **API Quotas**: Upgrade Gemini API tier
3. **Caching Strategy**: Implement Redis for distributed cache
4. **Async Processing**: Use task queues for long operations

## Maintenance

### Regular Tasks

- [ ] Monitor logs weekly
- [ ] Update dependencies monthly
- [ ] Check API quotas
- [ ] Review performance metrics
- [ ] Update documentation
- [ ] Test deployment monthly

### Update Process

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Test locally
streamlit run app.py

# Deploy
git add .
git commit -m "Update dependencies"
git push origin main
```

## Cost Estimation

| Platform | Cost | Best For |
|----------|------|----------|
| Streamlit Cloud (Free) | $0 | Development, demos |
| Streamlit Cloud (Pro) | $25/month | Small teams |
| Docker + DigitalOcean | $5-12/month | Budget-conscious |
| AWS ECS | $10-50/month | Scalable deployment |
| Google Cloud Run | Pay-as-you-go | Variable traffic |

## Useful Commands

```bash
# Run with custom port
streamlit run app.py --server.port 8080

# Disable analytics
streamlit run app.py --server.gatherUsageStats false

# Full screen mode
streamlit run app.py --logger.level=debug

# Clear cache
rm -rf ~/.streamlit/
```

## Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Configuration](https://docs.streamlit.io/library/advanced-features/configuration)
- [Performance](https://docs.streamlit.io/library/advanced-features/caching)

## Next Steps

1. **Test Locally**: `streamlit run app.py`
2. **Deploy to Cloud**: Choose platform above
3. **Monitor Performance**: Check logs and metrics
4. **Optimize**: Implement caching and optimization
5. **Scale**: Add authentication and multi-user support

---

**Last Updated**: October 22, 2024
**Status**: Production Ready
