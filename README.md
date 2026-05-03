# Job Portal

A , full-stack job portal built with Django.

## Project Structure

```
jobportal/
├── accounts/              # User authentication app
├── jobs/                  # Job posting & listing app
├── applications/          # Job application management app
├── templates/             # Django templates
│   ├── base.html
│   ├── navbar.html
│   ├── home.html
│   └── accounts/
├── static/css/            # Organized CSS structure
│   ├── global.css         # Design tokens & utilities
│   ├── components/        # Reusable components
│   │   └── components.css
│   └── pages/             # Page-specific styles
│       ├── accounts.css
│       └── home.css
├── jobportal/             # Django project settings
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
└── .gitignore             # Git ignore rules
```
