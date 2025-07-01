# Quote Management System

## Description
A comprehensive web application for managing service quotes and estimates. This system allows businesses to create, modify, track, and manage quotes with different user roles and permissions. Built with Django backend using HTML/CSS frontend and SQLite database.

## 🎯 Project Objectives
Develop a web application that enables users to efficiently manage service quotes with features including creation, modification, deletion, consultation, search, filtering, and export capabilities.

## 🚀 Key Features

### 👥 For Non-Authenticated Users
- **Quote Consultation**: View available quotes list
- **Search & Filter**: Search quotes by client, service, amount, or date
- **Public Quote Access**: Browse publicly available quotes

### 🔐 For Authenticated Users
- **Account Management**: Create account with email and password
- **Authentication**: Secure login/logout functionality
- **Quote Operations**:
  - Create new quotes (client, amount, service, date)
  - Modify own quotes
  - Delete own quotes
  - Update quote status (pending, accepted, rejected)
- **Export Functionality**: Export quotes to PDF or Excel formats

### 👨‍💼 For Administrators
- **User Management**: Create, modify, and delete user accounts
- **Complete Quote Management**: Full CRUD operations on all quotes
- **Service Management**: Add, modify, or remove company services
- **Dashboard**: Statistics overview (quote count, total amount, acceptance rates)

### 🔥 Advanced Features
- **Notifications**: System alerts for quote status changes
- **Modification History**: Track all changes with timestamps and user info
- **Quote Sharing**: Share quotes via email or unique links
- **Real-time Updates**: Live notifications for status changes

## 🛠️ Technology Stack

### Backend
- **Django**: Python web framework
- **Django REST Framework (DRF)**: API development
- **SQLite**: Lightweight database (development/small scale)
- **JWT Authentication**: Secure token-based authentication

### Frontend
- **HTML5**: Markup structure
- **CSS3**: Styling and responsive design
- **Vanilla JavaScript**: Interactive functionality
- **Bootstrap** (optional): UI components and layout

### Additional Libraries
- **ReportLab**: PDF generation
- **openpyxl**: Excel export functionality
- **PyJWT**: JWT token handling

## 📋 Prerequisites
- Python 3.8+
- pip (Python package manager)
- Web browser

## 🚀 Installation

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/quote-management-system.git
   cd quote-management-system
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup (SQLite)**
   ```bash
   # SQLite database will be created automatically
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open browser and go to: `http://127.0.0.1:8000/`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 🏗️ Project Structure

```
quote-management-system/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── quote_management/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── authentication/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── quotes/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── forms.py
│   ├── services/
│   └── dashboard/
├── templates/
│   ├── base.html
│   ├── quotes/
│   ├── auth/
│   └── dashboard/
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── bootstrap.min.css
│   ├── js/
│   │   ├── main.js
│   │   └── ajax.js
│   └── images/
└── media/
    └── exports/
```

## 📊 Database Models

### Core Models (SQLite)
```python
class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
class Quote(models.Model):
    client = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=20)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
class QuoteHistory(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    change_date = models.DateTimeField(auto_now_add=True)
    changes = models.TextField()
```

## 🔌 URL Patterns

```python
# Main URLs
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quotes.urls')),
    path('auth/', include('authentication.urls')),
    path('api/', include('api.urls')),
    path('dashboard/', include('dashboard.urls')),
]

# Quote URLs
urlpatterns = [
    path('', views.quote_list, name='quote_list'),
    path('create/', views.create_quote, name='create_quote'),
    path('<int:pk>/', views.quote_detail, name='quote_detail'),
    path('<int:pk>/edit/', views.edit_quote, name='edit_quote'),
    path('<int:pk>/delete/', views.delete_quote, name='delete_quote'),
    path('<int:pk>/export/', views.export_quote, name='export_quote'),
]
```

## 🎨 Frontend Structure

### HTML Templates
- **base.html**: Main layout template
- **quote_list.html**: Display all quotes
- **quote_detail.html**: Individual quote view
- **quote_form.html**: Create/edit quote form
- **login.html**: User authentication
- **dashboard.html**: Admin dashboard

### CSS Styling
```css
/* Main styles in static/css/style.css */
.quote-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.status-pending { color: #ffc107; }
.status-accepted { color: #28a745; }
.status-rejected { color: #dc3545; }
```

### JavaScript Functionality
```javascript
// AJAX for real-time updates
function updateQuoteStatus(quoteId, status) {
    fetch(`/api/quotes/${quoteId}/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getJWTToken()}`
        },
        body: JSON.stringify({status: status})
    });
}
```

## 🔒 JWT Authentication

### Implementation
```python
# views.py
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
```

### Frontend JWT Handling
```javascript
// Store JWT token
localStorage.setItem('access_token', response.access);

// Use JWT in requests
function getAuthHeaders() {
    return {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json'
    };
}
```

## 📱 Key Features Implementation

### Search and Filter
```html
<!-- Search form -->
<form method="GET" class="search-form">
    <input type="text" name="search" placeholder="Search quotes...">
    <select name="status">
        <option value="">All Status</option>
        <option value="pending">Pending</option>
        <option value="accepted">Accepted</option>
        <option value="rejected">Rejected</option>
    </select>
    <button type="submit">Search</button>
</form>
```

### Export Functionality
```python
def export_quote_pdf(request, pk):
    quote = get_object_or_404(Quote, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="quote_{pk}.pdf"'
    
    # Generate PDF using ReportLab
    p = canvas.Canvas(response)
    p.drawString(100, 750, f"Quote #{quote.id}")
    p.drawString(100, 730, f"Client: {quote.client}")
    p.save()
    return response
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test quotes

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report
```

### Sample Test
```python
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Quote, Service

class QuoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@test.com', 'pass')
        self.service = Service.objects.create(name='Web Dev', description='Web Development')
        
    def test_quote_creation(self):
        quote = Quote.objects.create(
            client='Test Client',
            amount=1000.00,
            service=self.service,
            created_by=self.user
        )
        self.assertEqual(quote.client, 'Test Client')
```

## 📦 Requirements.txt
```
Django==4.2.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.2.2
reportlab==4.0.4
openpyxl==3.1.2
Pillow==10.0.0
python-decouple==3.8
```

## ⚙️ Settings Configuration
```python
# settings.py key configurations
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# JWT Settings
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings.py
2. Configure allowed hosts
3. Use environment variables for secrets
4. Set up static file serving
5. Configure web server (Apache/Nginx)

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🔄 Future Enhancements
- Upgrade to PostgreSQL for production
- Add real-time WebSocket notifications
- Implement email notifications
- Mobile-responsive design improvements
- API rate limiting
- Advanced reporting and analytics

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -m 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Support

For support and questions:
- Create an issue on GitHub
- Email: [your-email@example.com]

---
*Professional Quote Management System - Built with Django, HTML, CSS, and SQLite*
