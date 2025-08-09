# Render Deployment Guide - Astrologer MCP Server

## 📁 Files Created for Deployment

### Core Files:
- `render.yaml` - Render configuration for Python web service
- `requirements.txt` - Python dependencies (FastMCP, FastAPI, OpenAI, uvicorn)
- `render_start.py` - Web service entry point that starts the FastAPI server
- `RENDER_DEPLOYMENT.md` - This guide

### Your Existing Files (Used as-is):
- `mcp-bearer-token/puch_astro_mcp.py` - Your complete MCP server with FastAPI integration

## 🚀 Deployment Steps

### Option 1: Deploy with render.yaml (Recommended)

1. **Connect your repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub/GitLab repository
   - Render will automatically detect the `render.yaml` file

2. **Set Environment Variables**
   In Render dashboard, add these environment variables:
   ```
   AUTH_TOKEN=astrology
   MY_NUMBER=919337015103
   OPENAI_API_KEY=your_openai_api_key_here
   N8N_WEBHOOK_URL=https://automation.stemforindia.com/webhook/astrologer-storage
   N8N_WEBHOOK_SECRET=astro15
   ```

3. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Option 2: Manual Setup

1. **Create Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure Service**
   - **Name**: astrologer-mcp-server
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python render_start.py`
   - **Plan**: Starter (or higher)

3. **Set Environment Variables**
   Add the same environment variables as above.

## 🔗 Endpoints

After deployment, your MCP server will be available at:

- **Root**: `https://your-app.onrender.com/` (health check)
- **Health**: `https://your-app.onrender.com/health` (detailed status)
- **MCP**: `https://your-app.onrender.com/mcp/` (MCP server endpoint)

## 🔧 Configuration

### MCP Client Configuration
Update your MCP client (like Puch AI) to use the Render URL:
```json
{
  "url": "https://your-app.onrender.com/mcp/",
  "auth": {
    "type": "bearer",
    "token": "astrology"
  }
}
```

### Health Check
Visit `https://your-app.onrender.com/health` to verify:
- ✅ Auth configured
- ✅ Phone configured  
- ✅ OpenAI ready
- ✅ Storage type (persistent/in-memory)

## 🎯 How It Works

1. **Render Web Service**: Runs your Python FastAPI app as a persistent web service
2. **Auto-scaling**: Automatically scales based on traffic
3. **Zero Downtime**: Automatic deployments with health checks
4. **Environment Variables**: Securely managed through Render dashboard
5. **HTTPS**: Built-in SSL certificates and custom domains

## 🎯 Benefits

- **✅ Persistent Service**: Always-on web service (not serverless)
- **✅ Auto-scaling**: Handles traffic spikes automatically
- **✅ HTTPS**: Built-in SSL certificates
- **✅ Custom Domains**: Easy to add custom domains
- **✅ Environment Variables**: Secure secret management
- **✅ Python Native**: No runtime conversion needed
- **✅ Free Tier**: Generous free tier for small projects

## ⚡ Performance

### Free Tier Limitations:
- Service spins down after 15 minutes of inactivity
- ~30-second cold start when service wakes up
- 512MB RAM, shared CPU

### Upgrade for Production:
- **Starter Plan ($7/month)**: No spinning down, 512MB RAM, shared CPU
- **Standard Plan ($25/month)**: 2GB RAM, 1 CPU core
- **Pro Plan ($85/month)**: 4GB RAM, 2 CPU cores

## 🔄 Updates

To deploy updates:
1. Push changes to your connected repository
2. Render automatically detects changes and redeploys
3. Zero-downtime deployment with health checks

## 📊 Monitoring

Monitor your deployment:
- **Render Dashboard**: Logs, metrics, deployment history
- **Health Endpoint**: `/health` for status checks
- **MCP Endpoint**: `/mcp/` for service availability
- **Built-in Metrics**: CPU, memory, response times

## 🐛 Troubleshooting

### Environment Variables Not Loading
- Set variables in Render dashboard under "Environment"
- Variables are case-sensitive
- Restart service after adding new variables

### Service Won't Start
- Check build logs in Render dashboard
- Ensure all dependencies are in `requirements.txt`
- Verify `render_start.py` imports work correctly

### MCP Connection Issues
- Verify authentication token matches
- Check HTTPS is being used (required for MCP)
- Test health endpoints first: `/` and `/health`

### Slow Cold Starts (Free Tier)
- Upgrade to Starter plan ($7/month) to eliminate spinning down
- Or use a service like UptimeRobot to ping your service regularly

### Memory Issues
- Monitor memory usage in Render dashboard
- Upgrade to higher plan if needed
- Check for memory leaks in application code

## 🌟 Production Tips

1. **Custom Domain**: Add your own domain in Render dashboard
2. **Monitoring**: Set up health check endpoints for monitoring services
3. **Logging**: All logs are available in Render dashboard
4. **Scaling**: Enable auto-scaling for production workloads
5. **Backups**: Regular database backups (if using Render databases)

## 🔐 Security

- **HTTPS**: Automatically enforced
- **Environment Variables**: Encrypted at rest
- **Network Isolation**: Services run in isolated containers
- **DDoS Protection**: Built-in protection
- **RBAC**: Team access controls available

Your Python Astrologer MCP Server is now production-ready on Render! 🌟

## ℹ️ Need Help?

- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
