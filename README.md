# ASF OAUSTECH - Tabernacle of Faith

The official web portal for the Anglican Students' Fellowship (ASF), OAUSTECH Branch. A platform for community engagement, discipleship resources, events, and alumni networking.

## Features
- **Dynamic Blog & News**: Categorized testimonies and teachings.
- **Interactive Prayer Wall**: Submit and join in prayers silently.
- **Event Management**: Live countdowns and flyer displays.
- **Leadership & Mentorship**: Professional profiles with social integration.
- **Alumni Network**: Directory for graduates to stay connected.

## Tech Stack
- **Backend**: Django (Python)
- **Primary Database**: SQLite (Relational data & Auth)
- **Secondary Database**: MongoDB (Archive & Collections)
- **Template Engine**: Jinja2
- **Frontend**: CSS Variable-based Theme (Light/Dark Mode), Vanilla JS (AJAX)

## Deployment on Render
1. Create a new Web Service on Render.
2. Connect your GitHub repository: `ASFOAUSTECH`.
3. Set Build Command to: `./build.sh`
4. Set Start Command to: `gunicorn config.wsgi:application`
5. Add Environment Variables:
   - `DJANGO_SECRET_KEY`: Your production secret
   - `DJANGO_DEBUG`: 0
   - `MONGO_URI`: Your MongoDB Atlas connection string

---
Develop by SegzyWeb Developer - Ogunniyi Oluwasegun Adebayo
---
© 2026 Anglican Students' Fellowship (ASF), OAUSTECH. Arise, Shine.
