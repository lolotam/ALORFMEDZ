# Hospital Pharmacy Management System

A comprehensive web-based pharmacy management system for hospitals, built with Flask and Bootstrap 5. This system provides complete inventory management, patient tracking, and advanced reporting capabilities.

## Features

### Core Functionality
- **User Authentication**: Role-based access control (Admin/Department User)
- **Medicine Management**: Complete inventory tracking with low stock alerts
- **Patient Management**: Patient records and prescription tracking
- **Supplier Management**: Supplier information and performance tracking
- **Department Management**: Multi-department support with isolated inventory
- **Purchase Management**: Stock intake with automatic inventory updates
- **Consumption Tracking**: Medicine dispensing with stock validation
- **Inventory Transfers**: Inter-department stock transfers
- **Comprehensive Reporting**: Analytics and insights for decision making

### Advanced Features
- **AI Chatbot**: Intelligent assistant for system queries and operations
- **Photo Management**: Patient photo upload and gallery
- **Bulk Operations**: Batch delete functionality for efficient data management
- **Dark/Light Theme**: User-selectable interface themes
- **Export Functionality**: CSV export for all reports
- **Backup & Restore**: Complete system backup with CSV format support
- **Audit Trail**: Complete activity logging for compliance

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd ALORFMDZ
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the system**
   - Open browser: http://localhost:5000
   - Default credentials:
     - Admin: `username: admin`, `password: @Xx123456789xX@`
     - Department User: `username: pharmacy`, `password: pharmacy123`

## Docker Deployment

```bash
# Build the Docker image
docker build -t hospital-pharmacy .

# Run the container
docker run -p 5001:5001 hospital-pharmacy
```

Access at: http://localhost:5001

## Production Deployment

### Important Security Steps

1. **Change default passwords immediately**
2. **Enable HTTPS/SSL certificates**
3. **Set up proper environment variables**
4. **Configure firewall rules**
5. **Set up regular automated backups**

### Recommended Deployment Stack

- **Web Server**: Nginx (reverse proxy)
- **WSGI Server**: Gunicorn
- **Process Manager**: Supervisor or systemd
- **Database**: Consider migrating to PostgreSQL for production
- **Monitoring**: Set up application monitoring

### Environment Variables

Create a `.env` file with:
```env
FLASK_ENV=production
SECRET_KEY=<generate-strong-secret-key>
SESSION_TYPE=filesystem
DATABASE_BACKUP_SCHEDULE=daily
```

## Project Structure

```
ALORFMDZ/
├── app.py                  # Main application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── blueprints/            # Flask blueprints (modules)
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── utils/                 # Utility functions
├── data/                  # JSON database files
├── backups/               # System backups
├── uploads/               # User uploaded files
└── flask_session/         # Session storage
```

## Usage

### User Roles

**Administrator**
- Full system access
- User management
- Purchase orders
- System settings
- All reports

**Department User**
- Department-specific access
- Medicine dispensing
- Consumption tracking
- Limited reporting

### Key Workflows

1. **Initial Setup**
   - Add suppliers
   - Add medicines with low stock limits
   - Create departments (auto-creates users)
   - Add patients

2. **Daily Operations**
   - Record purchases (admin)
   - Dispense medicines (consumption)
   - Transfer stock between departments
   - Monitor low stock alerts

3. **Reporting**
   - View consumption reports
   - Check inventory status
   - Export data as CSV
   - Review audit logs

## API Integration

The system includes API endpoints for integration:
- `/api/medicines` - Medicine data
- `/api/inventory` - Stock levels
- `/api/patients` - Patient information

## Backup & Recovery

### Manual Backup
1. Go to Settings → Security
2. Click "Create Backup"
3. Download the ZIP file

### Restore from Backup
1. Go to Settings → Restore
2. Upload backup ZIP file
3. Confirm restoration

## Support & Maintenance

### System Requirements
- **RAM**: Minimum 2GB
- **Storage**: 10GB recommended
- **CPU**: 2 cores minimum
- **OS**: Windows/Linux/macOS

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes

- Implements session-based authentication
- Password hashing with Werkzeug
- Account lockout after failed attempts
- Complete audit trail
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

© 2025 Hospital Pharmacy Management System. All rights reserved.

## Contact

For support or inquiries, please contact the development team.

---

**Version**: 2.0.0
**Last Updated**: September 2025