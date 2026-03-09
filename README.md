#  AI Learning Tracker Portal

A modern, full-stack web application built with Django and TailwindCSS for tracking daily AI/ML learning progress. Features a stunning UI with glassmorphism design, animated dashboards, GitHub-style activity heatmap, and Base64 file storage.

##  Features

###  Modern UI Design
- **Glassmorphism cards** with backdrop blur effects
- **Animated gradient backgrounds** that shift colors
- **Smooth page transitions** and hover effects
- **Responsive design** for mobile and desktop
- **Professional SaaS-style dashboard** inspired by Notion and Linear

###  Dashboard
- Personalized welcome message
- Current learning streak counter with animations
- GitHub-style contribution heatmap showing 365 days of activity
- Auto-refreshing motivational quotes (every 15 seconds)
- Recent learning logs preview
- Leaderboard comparing user streaks

###  Learning Entry System
- Auto-generated 6-digit unique record IDs
- Rich text notes documentation
- Code snippet editor with syntax highlighting (Prism.js)
- Tag system for categorization
- Base64 file upload and storage
- Date tracking with automatic streak calculation

###  Base64 Document Storage
- Upload any file type (PDF, images, documents)
- Files converted to Base64 and stored in database
- Secure download functionality that reconstructs original files
- No external file storage needed

###  Powerful Search
- Search by record ID, title, tags, or keywords
- Real-time filtering of learning entries
- Beautiful results display

###  Gamification
- Learning streak tracking
- Daily activity heatmap
- User leaderboard
- Progress statistics

###  Admin Panel
- User management
- View all learning logs
- Add/remove motivational quotes
- Analytics and statistics
- Full Django admin integration

##  Technology Stack

- **Backend**: Django 5.2.11
- **Frontend**: HTML5, TailwindCSS (CDN), JavaScript
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **Code Highlighting**: Prism.js
- **Authentication**: Django built-in auth system

##  Installation & Setup

### Prerequisites
- Python 3.11 or higher
- pip package manager

### Step 1: Activate Virtual Environment
```bash
cd LC
.\Scripts\activate
cd ..
```

### Step 2: Navigate to Project Directory
```bash
cd ai_learning_tracker
```

### Step 3: Database Setup (Already Done)
The database has been set up with:
-  All migrations applied
-  50 motivational quotes loaded
-  Test users created

### Step 4: Run Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

##  Login Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- Access to admin panel and all features

### User Accounts
**User 1:**
- **Username**: `user1`
- **Password**: `user123`

**User 2:**
- **Username**: `user2`
- **Password**: `user123`

##  Usage Guide

### Creating a Learning Entry
1. Login with your credentials
2. Click "New Entry" in the navigation
3. Fill in:
   - Title (What you learned)
   - Date (auto-filled with today)
   - Notes (detailed documentation)
   - Code snippet (optional, with syntax highlighting)
   - Tags (comma-separated)
   - Upload document (optional, stored as Base64)
4. Click "Save Entry"
5. Your streak will automatically update!

### Downloading Attached Files
1. View any learning entry
2. If a file is attached, click the "Download" button
3. The original file will be reconstructed from Base64 and downloaded

### Searching Logs
1. Click "Search" in navigation
2. Enter keywords, record ID, title, or tags
3. View matching results instantly

### Admin Functions
1. Login as admin
2. Click "Admin Panel" in navigation
3. Manage:
   - View user statistics
   - Add/remove motivational quotes
   - Access Django admin panel

##  Project Structure

```
ai_learning_tracker/
 ai_learning_tracker/          # Project settings
    settings.py              # Django configuration
    urls.py                  # Main URL routing
    wsgi.py                  # WSGI configuration
 tracker/                      # Main application
    models.py                # Database models
    views.py                 # View logic
    forms.py                 # Form definitions
    urls.py                  # App URL routing
    admin.py                 # Admin configuration
    management/commands/     # Custom commands
        populate_quotes.py   # Quote loader
        create_users.py      # User creator
 templates/tracker/            # HTML templates
    base.html               # Base template with styling
    dashboard.html          # Main dashboard
    login.html              # Login page
    create_log.html         # Entry creation form
    view_log.html           # Entry detail view
    search.html             # Search interface
    admin_dashboard.html    # Admin panel
    manage_quotes.html      # Quote management
 static/                       # Static files (CSS/JS)
 db.sqlite3                   # SQLite database
 manage.py                    # Django management script
```

##  Key Features Explained

### Auto-Generated Record IDs
Each learning entry gets a unique 6-digit numeric ID (e.g., `483921`) automatically generated on save.

### Streak Calculation
- Tracks consecutive days of learning entries
- Updates automatically when you log for the day
- Resets if you skip a day
- Displayed prominently on dashboard with fire emoji 

### GitHub-Style Heatmap
- Shows 365 days of learning activity
- Color intensity based on entries per day:
  - Light green: 1-2 entries
  - Medium green: 3-4 entries
  - Dark green: 5-6 entries
  - Brightest green: 7+ entries

### Base64 File Handling
**Upload Process:**
1. User selects file in form
2. File is read as binary
3. Converted to Base64 string
4. Stored in database with metadata

**Download Process:**
1. Retrieve Base64 string from database
2. Decode back to binary
3. Create HTTP response with correct content-type
4. Browser downloads reconstructed file

##  Management Commands

### Populate Quotes
```bash
python manage.py populate_quotes
```
Loads 50 inspirational quotes into the database.

### Create Users
```bash
python manage.py create_users
```
Creates admin and test users.

##  UI Components

### Glassmorphism Cards
```css
background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.2);
```

### Animated Gradients
```css
background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
animation: gradient-shift 15s ease infinite;
```

### Hover Effects
All interactive elements include smooth scale transitions and color changes.

##  Responsive Design

The application is fully responsive and works perfectly on:
- Desktop (1920px+)
- Laptop (1024px - 1920px)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

##  Production Deployment

For production deployment:

1. **Update settings.py:**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

2. **Use PostgreSQL/MySQL instead of SQLite**

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Use proper secret key**

5. **Set up HTTPS**

##  Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Issues
```bash
python manage.py migrate
```

### Missing Quotes
```bash
python manage.py populate_quotes
```

##  Notes

- **File Storage**: Files are stored as Base64 in the database. For production with large files, consider using cloud storage (AWS S3, Azure Blob).
- **Performance**: Current setup handles ~1000 entries efficiently. For larger scale, optimize queries and consider caching.
- **Security**: Default passwords are for development only. Change them in production!

##  Enjoy Your Learning Journey!

Start tracking your AI/ML learning progress with this beautiful, modern application. Stay motivated, maintain your streak, and watch your knowledge grow! 

---

**Built with  using Django & TailwindCSS**
