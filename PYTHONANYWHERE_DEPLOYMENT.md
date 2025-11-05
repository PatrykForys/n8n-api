# PythonAnywhere Deployment Guide

## Step 1: Upload Files
1. Upload these files to your PythonAnywhere account:
   - `main.py` (your FastAPI application)
   - `wsgi.py` (WSGI wrapper - created above)
   - `requirements.txt` (dependencies)

## Step 2: Install Dependencies
In PythonAnywhere Bash console:
```bash
pip3.11 install --user -r requirements.txt
```

## Step 3: Configure Web App
1. Go to PythonAnywhere Web tab
2. Create new web app or reload existing one
3. Set these configurations:
   - **Source code**: `/home/ExtaZyyy/n8n-api`
   - **Working directory**: `/home/ExtaZyyy/n8n-api`
   - **WSGI configuration file**: `/home/ExtaZyyy/n8n-api/wsgi.py`
   - **Python version**: 3.11
   - **Virtualenv**: Leave empty (using --user install)

## Step 4: Test Endpoints
After reloading the web app, test these URLs:
- `https://extazyyy.pythonanywhere.com/` - Should show welcome message
- `https://extazyyy.pythonanywhere.com/nauczyciele` - Should return teacher names
- `https://extazyyy.pythonanywhere.com/akutalnosci` - Should return news with dates

## Troubleshooting

### 502 Backend Error
- Check error logs in PythonAnywhere Web tab
- Ensure all files are uploaded correctly
- Verify WSGI file path is correct

### Import Errors
- Make sure dependencies are installed with `--user` flag
- Check that file paths in wsgi.py match your actual paths

### Module Not Found
- Install missing packages: `pip3.11 install --user package_name`
- Check Python version compatibility

## Important Notes
- The WSGI file (`wsgi.py`) bypasses FastAPI and directly implements the endpoints
- This approach is more reliable on PythonAnywhere than trying to run FastAPI directly
- All endpoints return JSON responses as expected