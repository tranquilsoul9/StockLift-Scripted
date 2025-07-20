# StockLift Render.com Deployment Guide

This guide will help you deploy StockLift on Render.com step by step.

## Prerequisites

- GitHub repository with your StockLift code (including model files)
- Render.com account (free tier available)
- Google API key (for location services)

## Step-by-Step Deployment

### 1. Prepare Your Repository
- Ensure your repo has:
  - `app.py` (Flask app)
  - `requirements.txt` (Python dependencies)
  - `models/` directory (with your ML model files)
  - `static/`, `templates/`, etc.

### 2. Push to GitHub
- Commit and push all your code and model files to your GitHub repository.

### 3. Create a New Web Service on Render
- Go to [render.com](https://render.com) and sign in with GitHub.
- Click **“New +”** → **“Web Service”**.
- Connect your GitHub repo and select your StockLift repository.

### 4. Configure the Service
- **Name:** (Anything you like)
- **Branch:** `main` (or your default branch)
- **Build Command:** (leave blank; Render auto-installs from `requirements.txt`)
- **Start Command:**
  ```bash
  gunicorn app:app
  ```

### 5. Set Environment Variables
- Click “Add Environment Variable”
- **Key:** `GOOGLE_API_KEY`
- **Value:** `your-google-api-key`

### 6. Deploy
- Click **“Create Web Service”**
- Wait for the build and deploy to finish (a few minutes).

### 7. Test Your App
- Visit the Render-provided URL (e.g., `https://stocklift.onrender.com`)
- Test all features, including ML model loading.

---

**Notes:**
- Render allows much larger deployments than Vercel (GBs, not MBs).
- Your model files in the repo will be available to the app.
- The free tier may sleep after inactivity.
- Check the “Logs” tab in Render dashboard for errors.

---

**Quick Start for Local:**
```bash
export GOOGLE_API_KEY=your-google-api-key
python app.py
``` 