# Vercel Deployment Guide - Astrologer MCP Server

## 📁 Files Created for Deployment

### Core Files:
- `vercel.json` - Vercel configuration for Python runtime
- `requirements.txt` - Python dependencies (FastMCP, FastAPI, OpenAI, etc.)
- `api/index.py` - Serverless function entry point that imports your existing MCP server
- `VERCEL_DEPLOYMENT.md` - This guide

### Your Existing Files (Used as-is):
- `mcp-bearer-token/puch-astro-mcp.py` - Your complete MCP server with FastAPI integration

## 🚀 Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Deploy
```bash
vercel --prod
```

### 4. Set Environment Variables
In Vercel dashboard, go to your project settings and add:

```
AUTH_TOKEN=astrology
MY_NUMBER=919337015103
OPENAI_API_KEY=your_openai_api_key_here
N8N_WEBHOOK_URL=https://automation.stemforindia.com/webhook/astrologer-storage
N8N_WEBHOOK_SECRET=astro15
```

## 🔗 Endpoints

After deployment, your MCP server will be available at:

- **Root**: `https://your-app.vercel.app/` (health check)
- **Health**: `https://your-app.vercel.app/health` (detailed status)
- **MCP**: `https://your-app.vercel.app/mcp/` (MCP server endpoint)

## 🔧 Configuration

### MCP Client Configuration
Update your MCP client (like Puch AI) to use the Vercel URL:
```json
{
  "url": "https://your-app.vercel.app/mcp/",
  "auth": {
    "type": "bearer",
    "token": "astrology"
  }
}
```

### Health Check
Visit `https://your-app.vercel.app/health` to verify:
- ✅ Auth configured
- ✅ Phone configured  
- ✅ OpenAI ready
- ✅ Storage type (persistent/in-memory)

## 🎯 How It Works

1. **Vercel Python Runtime**: Uses `@vercel/python` to run your Python MCP server
2. **FastAPI Integration**: Your existing FastAPI app is directly exported 
3. **Zero Code Changes**: Your `puch-astro-mcp.py` works unchanged
4. **Environment Variables**: Securely managed through Vercel dashboard
5. **Global Distribution**: Deployed to Vercel's edge network

## 🎯 Benefits

- **✅ Serverless**: Auto-scaling, pay-per-use
- **✅ HTTPS**: Built-in SSL certificates
- **✅ Global CDN**: Fast worldwide access
- **✅ Zero Config**: Automatic builds and deployments
- **✅ Environment Variables**: Secure secret management
- **✅ Python Native**: No TypeScript conversion needed

## 🔄 Updates

To deploy updates:
```bash
vercel --prod
```

Vercel will automatically:
1. Install Python dependencies from `requirements.txt`
2. Import your existing MCP server
3. Deploy with zero downtime

## 📊 Monitoring

Monitor your deployment:
- Vercel dashboard: Functions, logs, analytics
- Health endpoint: `/health` for status checks
- MCP endpoint: `/mcp/` for service availability

## 🐛 Troubleshooting

### Environment Variables Not Loading
- Check `.env` file is not deployed (Vercel ignores it)
- Set variables in Vercel dashboard Project Settings → Environment Variables

### Import Errors
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility (using 3.11)

### MCP Connection Issues
- Verify authentication token matches
- Check HTTPS is being used (required for MCP)
- Test health endpoints first

Your Python Astrologer MCP Server is now production-ready on Vercel! 🌟
