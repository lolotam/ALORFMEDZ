# Fresh Repository Setup Instructions

## Steps to Remove Git History and Create Fresh Repository

### 1. Clean Up Unnecessary Files

First, delete the folders you don't need:

```bash
# Remove unnecessary documentation and scripts
rm -rf "md files"
rm -rf unwanted
rm ALORFMDZ2.rar
```

### 2. Remove Git History (Start Fresh)

```bash
# Option A: Complete Fresh Start (RECOMMENDED)
# This removes ALL git history and creates a new repository

# Step 1: Delete the .git folder
rm -rf .git

# Step 2: Initialize new repository
git init

# Step 3: Add all files
git add .

# Step 4: Create initial commit
git commit -m "Initial commit: Hospital Pharmacy Management System v2.0"

# Step 5: Add your new remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_NEW_REPO_NAME.git

# Step 6: Push to new repository
git branch -M main
git push -u origin main
```

### 3. Alternative: Keep History but Clean Sensitive Data

```bash
# Option B: Keep history but remove sensitive files
# Use this if you want to keep some history

# Remove sensitive files from history
git filter-branch --force --index-filter \
  'git rm -r --cached --ignore-unmatch "md files" unwanted ALORFMDZ2.rar' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push to remote
git push origin --force --all
git push origin --force --tags
```

### 4. Setup for Production

After creating your fresh repository:

1. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Generate Secret Key**
   ```python
   # Run this Python script to generate a secure secret key
   import secrets
   print(secrets.token_hex(32))
   ```
   Copy the output and add to your .env file as SECRET_KEY

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the Application**
   ```bash
   python app.py
   ```

### 5. Important Security Steps

Before deploying to production:

1. ✅ Change all default passwords in the database
2. ✅ Update SECRET_KEY in .env
3. ✅ Enable HTTPS/SSL certificates
4. ✅ Set FLASK_ENV=production in .env
5. ✅ Configure firewall rules
6. ✅ Set up automated backups
7. ✅ Review and update user permissions

### 6. Deployment Options

#### Docker Deployment
```bash
docker build -t hospital-pharmacy .
docker run -d -p 5001:5001 --env-file .env hospital-pharmacy
```

#### Traditional Deployment with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### 7. Files/Folders Safe to Delete

Already ignored in .gitignore:
- `md files/` - Development documentation (DELETE)
- `unwanted/` - Old utility scripts (DELETE)
- `flask_session/` - Session files (AUTO-GENERATED)
- `__pycache__/` - Python cache (AUTO-GENERATED)
- `*.log` - Log files (AUTO-GENERATED)
- Backup files in `backups/` (KEEP FOLDER, DELETE OLD FILES)

### 8. Final Checklist

Before going live:
- [ ] All default passwords changed
- [ ] .env file configured with production values
- [ ] Secret key generated and set
- [ ] HTTPS configured
- [ ] Firewall rules set
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Error logging enabled
- [ ] Rate limiting configured (if needed)
- [ ] Database migration plan (if moving from JSON)

---

## Support

If you encounter any issues during setup, check:
1. Python version (3.7+ required)
2. All dependencies installed
3. Proper file permissions
4. .env file properly configured

Good luck with your deployment! 🚀