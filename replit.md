# Campus Sphere

## Overview

Campus Sphere is an integrated campus management platform designed for educational institutions. It provides a comprehensive suite of features including real-time bus tracking with live GPS updates, academic resource sharing, event management, alumni networking, faculty directory, student community forums, and club management. The platform serves students, faculty, drivers, and administrators with role-based access control.

## Recent Changes

**October 5, 2025** - Complete implementation of Campus Sphere platform:
- Built all database models with proper relationships and SQLAlchemy ORM
- Implemented authentication system with email verification, session management, and device tracking
- Created all frontend templates with vibrant gradients, glassmorphism effects, and responsive design
- Developed bus tracking with OpenStreetMap/Leaflet integration and real-time GPS updates
- Built driver interface for location sharing with geolocation API
- Implemented academic resources with file downloads and view tracking
- Created events, alumni network, faculty directory, community posts, and clubs management
- Developed admin panel with role-based access control
- Fixed CSS validation issues (replaced Tailwind-only properties with standard CSS)
- Fixed academic resource downloads to properly serve files using send_from_directory
- Secured all API endpoints with proper authentication decorators
- All features tested and working correctly

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: The frontend uses server-side rendered HTML templates with Jinja2, styled with Tailwind CSS (via CDN), and enhanced with vanilla JavaScript for interactivity. No frontend frameworks like React or Vue are used.

**Template Structure**: All pages extend a `base.html` template that provides common layout elements including flash message handling, CSS/JS imports, and responsive design foundation. Pages are organized by feature (dashboard, bus-tracking, academic-resources, events, alumni, faculty, community, clubs, profile) with a separate admin subdirectory for administrative interfaces.

**Styling Approach**: Uses Tailwind CSS utility classes combined with custom CSS variables for gradient themes. Implements a "glass morphism" design pattern with semi-transparent cards and backdrop blur effects for a modern aesthetic.

**Mapping Integration**: OpenStreetMap with Leaflet.js for live bus tracking visualization. The map displays bus locations in real-time and shows bus stops along routes.

### Backend Architecture

**Framework**: Flask (Python) handles all server-side logic, routing, and template rendering.

**Authentication System**: Cookie-based authentication using secure tokens. The system supports:
- Email verification for new signups via temporary user storage
- Session token validation for logged-in users
- Device-based login tracking with force logout capability
- Separate authentication flows for regular users, admins, and drivers
- Custom decorators (@login_required, @admin_required, @driver_required) for route protection

**Database ORM**: SQLAlchemy with SQLite as the database engine. Models include:
- User management (User, TempUser for unverified accounts)
- Transportation (Bus, BusStop, Driver with real-time location tracking)
- Academic (AcademicResource with file uploads)
- Social (Event, Alumni, Faculty, Club, ClubMembership, CommunityPost)
- Administration (Admin)

**File Upload Handling**: Supports document and image uploads (PDF, DOC, DOCX, PPT, PPTX, JPG, JPEG, PNG) with a 16MB file size limit. Uploaded files stored in `static/uploads/` directory.

**Security**: Password hashing using Werkzeug's security utilities, token-based verification, session management, and CSRF protection through Flask's built-in mechanisms.

### External Dependencies

**Email Service**: Flask-Mail integration for sending verification emails and notifications. Configured to use SMTP (defaults to Gmail's SMTP server) with credentials managed through environment variables. HTML email templates with gradient styling match the platform's design language.

**Mapping Service**: 
- OpenStreetMap tile servers for map rendering
- Leaflet.js library (v1.9.4) for interactive map controls
- Real-time GPS coordinate updates for bus tracking

**Database**: SQLite for development and lightweight deployment. Database file stored as `database.db` in the project root.

**Configuration Management**: Environment variables for sensitive credentials:
- SESSION_SECRET: Flask session encryption key
- MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS: Email server configuration
- MAIL_USERNAME, MAIL_PASSWORD: Email authentication
- MAIL_DEFAULT_SENDER: Default sender address

**Third-Party CDNs**:
- Tailwind CSS via CDN for styling
- Leaflet.js via CDN for mapping functionality

**Python Dependencies**:
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Flask-Mail: Email functionality
- Werkzeug: Password hashing and security utilities