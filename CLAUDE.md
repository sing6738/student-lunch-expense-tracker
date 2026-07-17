# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Thai lunch expense tracking web application that helps students record and analyze their daily food expenses. The application features user authentication, expense management, restaurant and menu management, analytics, and budget tracking.

## Technology Stack

- **Framework**: Flask (Python)
- **Database**: SQLite (with PostgreSQL support for production)
- **ORM**: SQLAlchemy
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: Bootstrap 5, Chart.js, jQuery
- **Security**: Werkzeug password hashing, security headers, CSRF protection
- **Deployment**: Gunicorn, Render

## Project Structure

```
lunch_expense_app/
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy models
├── forms.py                  # Flask-WTF forms
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── templates/               # HTML templates
│   ├── base.html            # Main layout
│   ├── login.html           # Login form
│   ├── register.html        # Registration form
│   ├── dashboard.html       # Main dashboard
│   ├── add_expense.html     # Add/edit expense form
│   ├── history.html         # Expense history
│   ├── analytics.html       # Analytics page
│   └── budget.html          # Budget settings
├── static/                  # Static assets
│   ├── css/                # CSS files
│   ├── js/                # JavaScript files
│   └── images/            # Images
├── database.db              # SQLite database (created automatically)
└── templates/errors/       # Error templates
```

## Key Components

### 1. Authentication
- User registration and login with session management
- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Login-required decorator for protected routes

### 2. Expense Management
- Add/edit/delete expense records
- Dynamic restaurant and menu selection
- Expense categorization (categories are defined in models.py)
- Date filtering and search functionality
- Export to CSV

### 3. Restaurant and Menu Management
- Pre-seeded data for common Thai restaurants
- CRUD operations for restaurants and menus
- Dynamic menu loading via AJAX
- Menu pricing management

### 4. Analytics and Dashboard
- 7-day expense trend chart
- Monthly and weekly expense summaries
- Expense categorization analytics
- Calendar view of expenses
- Monthly budget tracking

### 5. Budget Management
- Daily budget settings per user
- Monthly budget system with income and fixed expenses
- Budget progress tracking
- Savings calculations

### 6. Online Orders
- Track online food orders from various platforms
- Integration with expense tracking
- Status management (ordered, shipping, delivered, cancelled)

## Common Commands

### Development

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
# or
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
flask --app app run --debug
# or
python app.py

# Access the app
http://127.0.0.1:5000
```

### Database

```bash
# Check database
sqlite3 database.db

# Export data
# Use the export feature in the UI or query directly
```

### Code Navigation

```bash
# List Python files
find . -name "*.py" -not -path "./.venv/*" -not -path "./__pycache__/*"

# Check for syntax errors
python -m py_compile app.py

# Linting (if configured)
# flake8 app.py models.py forms.py
```

## Running Tests

The application includes a test script:

```bash
# Run database tests
python test_db.py
```

Note: The application doesn't have a comprehensive test suite yet, but includes basic database tests.

## Configuration

### .env Variables (for production)
```
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:password@host:port/database
```

### Configuration Options (in config.py)
- `SECRET_KEY`: Flask secret key
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `ITEMS_PER_PAGE`: Pagination setting
- `DEBUG`: Debug mode

## Deployment

### Production (Render)
1. Push to git repository
2. Connect Render account
3. Select this repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn --config gunicorn.conf.py app:create_app`
6. Set environment variables for secrets

### Local Production
```bash
# Use PostgreSQL
export DATABASE_URL=postgresql://user:password@localhost/lunch_expense
python app.py
```

## Code Patterns

### Database Models
- Uses SQLAlchemy ORM
- Relationships: User ↔ Expense ↔ Menu ↔ Restaurant
- Soft delete pattern for restaurants and menus (cannot delete if referenced)
- Monthly budget system with automatic month-over-month carryover

### Forms
- Flask-WTF with CSRF protection
- Client-side and server-side validation
- Dynamic field population based on user selections

### Security
- CSRF protection on all forms
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- Password hashing with Werkzeug
- Input validation and escaping

### API Endpoints
- REST-like routes for expense management
- JSON APIs for dynamic menu loading
- CSV export endpoint

## Development Guidelines

### Adding New Restaurants/Menus
1. Use the web interface at `/manage-menus` (requires login)
2. Use the seed data in `app.py` as reference for initial setup
3. Ensure menu prices are realistic for Thai context

### Adding New Features
1. Follow existing patterns in app.py for route registration
2. Use existing form classes as templates
3. Ensure proper authentication with `@login_required` decorator
4. Implement error handling and user feedback (flash messages)
5. Follow Thai locale conventions (dates, currency format)

### Database Migrations
For SQLite:
- Schema changes take effect after restart
- Use `migrate_db.py` and `migrate_category.py` for specific migrations

For PostgreSQL (production):
- Use Alembic for proper migrations
- Set up `DATABASE_URL` environment variable

## Troubleshooting

### Common Issues
1. **CSRF Errors**: Clear browser cookies and try again
2. **Database locked**: Close other SQLite connections, restart application
3. **Import errors**: Ensure all dependencies are installed
4. **Session issues**: Check browser settings for cookies

### Debugging
```bash
# Enable debug logging
export FLASK_DEBUG=1
python app.py

# Check Flask logs
# Flask logs to stdout by default
```

## Localization

The application uses Thai language for:
- User interface
- Expense categories
- Date formatting
- Currency formatting (Baht)

Numbers are formatted with commas as thousands separators (e.g., 1,234.56).

## Performance Considerations

1. **Database**: Use index-friendly queries in models
2. **Caching**: Simple in-memory caching for menu data
3. **Images**: Optimize static assets for production
4. **Session**: Use secure cookies in production

## Future Enhancements

1. Multi-user support with different permissions
2. Expense splitting among users
3. Integration with meal delivery services
4. Mobile app
5. Advanced analytics and reporting
6. API for third-party integrations

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/getting-started/introduction/)
- [Chart.js](https://www.chartjs.org/)
- [Render Deployment Guide](https://render.com/docs)