# Parking Management System

## Project Details

- **Project Title:** Parking Management System
- **Author:** Ektor Vastakis
- **GitHub Username:** ektorvastakis
- **edX Username:** ektorvastakis
- **City:** Athens
- **Country:** Greece
- **Date Recorded:** November 14, 2024

## Video Demo:

- [Video Demo](https://www.youtube.com/watch?v=Y7NqYSFZBGw&ab_channel=EktwrVastakis)

## Overview

As a new developer, I'm proud to present my Parking Management System - a robust web application built with Flask that streamlines parking operations for businesses. The project implements role-based access control, real-time slot availability checking, and an intuitive booking interface.

## Core Features

- Role-based access control (Manager, Guard, Lobby staff)
- Real-time parking slot availability checking
- Dynamic booking system with time slot validation
- Responsive dashboard for different user roles
- System configuration and management tools
- Secure user authentication and session management

## Technical Architecture

### Backend Structure

The application follows a modular architecture with clear separation of concerns:

#### `app.py` - Application Core

The heart of the application, handling:

- Route definitions and request processing
- Business logic implementation
- Error handling with custom AppError class
- Session management
- Database operations

Key routes include:

#### `config.py` - Configuration Management

I implemented a flexible configuration system using environment variables for different deployment environments:

- Development configuration for local development
- Testing configuration for automated tests
- Production configuration with enhanced security settings

The decision to use environment variables makes deployment more secure and flexible:

#### `helpers.py` - Utility Functions

Contains reusable functions and decorators:

### Frontend Architecture

The frontend uses a template-based approach with Jinja2, Bootstrap 5, and custom CSS:

#### Templates Structure

- `layout.html`: Base template with common elements
- `index.html`: Landing page with feature highlights
- `staff_dashboard.html`: Role-specific dashboard
- `bookings_table.html`: Reusable booking display component
- `reserve.html`: Booking interface
- `settings.html`: System configuration interface

## Design Decisions

### 1. Role-Based Access Control

I implemented three distinct roles to ensure proper separation of duties:

- Managers: Can make and manage reservations
- Guards: View and verify bookings
- Lobby Staff: Monitor overall parking status

This design decision enhances security and maintains clear responsibility boundaries.

### 2. Real-Time Availability Checking

Instead of static slot assignment, I implemented dynamic checking:

```python:app.py
startLine: 276
endLine: 305
```

This prevents double-booking and ensures accurate availability information.

### 3. Database Design

I chose SQLite with CS50's library for several reasons:

- Simplified deployment process
- Built-in transaction support
- No need for external database server
- Sufficient for expected load

### 4. Error Handling

Implemented a custom AppError class for consistent error handling:

```python:app.py
startLine: 56
endLine: 60
```

### 5. Frontend Architecture

I chose server-side rendering over a SPA architecture because:

- Simpler deployment and maintenance
- Better initial page load performance
- Reduced complexity
- Better SEO capabilities
- Faster development cycle

## Security Measures

- Password hashing for user credentials
- Session-based authentication
- CSRF protection
- Input validation
- Parameterized SQL queries
- Environment-based configuration

## Future Improvements

1. API Documentation
2. Mobile application development
3. Payment gateway integration
4. Email notification system
5. Advanced analytics dashboard
6. Automated testing suite

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Quick Start

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variables or create .env file
5. Initialize database:
   ```bash
   flask init-db
   ```
6. Run the application:
   ```bash
   flask run
   ```
