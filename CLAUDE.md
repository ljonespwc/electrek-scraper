# Electrek Monitor - Flask Web Application

**Project ID**: `icooetipqrnaxrazjrgk` (use this for all MCP database operations)

## Development Workflow Rules
When working on this project, always follow these 7 rules:
1. **Plan First**: Think through the problem, read the codebase for relevant files, and create a plan
2. **Create Todo List**: Use the TodoWrite tool to track progress on multi-step tasks
3. **Get Approval**: Before beginning work, check in with the user and get verification of the plan
4. **Execute Incrementally**: Work on todo items one by one, marking them as complete as you go
5. **Communicate Changes**: Give high-level explanations of what changes you made at each step
6. **Keep It Simple**: Make every task and code change as simple as possible. Avoid massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. **Document Results**: Update this CLAUDE.md file when significant architectural changes are made

## Project Overview
Electrek Monitor is a Flask web application with public articles and private admin functionality. The application features:
- **Public Site**: Clean, Medium-style articles accessible to all visitors
- **Admin Dashboard**: Google OAuth-protected scraping and analytics tools
- **Data Analysis**: Advanced sentiment analysis and engagement metrics for Tesla/EV coverage

## Technology Stack

### Backend
- **Framework**: Flask 3.1.0 (Python web framework)
- **Database**: Supabase (PostgreSQL-based cloud database)
- **Authentication**: Supabase Google OAuth with JWT tokens
- **Web Scraping**: BeautifulSoup4 for HTML parsing
- **Sentiment Analysis**: OpenAI GPT-4o API for advanced sentiment scoring
- **HTTP Requests**: requests library with proxy support
- **Data Processing**: NumPy for correlation calculations
- **Performance**: File-based caching + Vercel CDN caching (30-day TTL)
- **Reading Time**: BeautifulSoup-based word counting (250 WPM)

### Frontend
- **Public Design**: Medium-style clean typography with SF Pro Display
- **Admin UI**: Bootstrap 5.3.0 for dashboard functionality
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for data visualization
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Vanilla JS for dynamic interactions

### Key Dependencies
- `supabase==2.15.0` - Database client
- `beautifulsoup4==4.13.3` - HTML parsing
- `requests==2.32.3` - HTTP requests
- `numpy==2.2.5` - Mathematical operations
- `python-dotenv==1.1.0` - Environment variable management

## Database Schema

### Articles Table (`articles`)
```sql
- id (bigint, primary key, auto-increment)
- created_at (timestamptz, default: now())
- updated_at (timestamptz, default: now())
- title (text, not null)
- url (text, unique)
- author (text)
- published_at (timestamptz)
- comment_count (integer, default: 0)
- sentiment_score (double precision, -1.0 to 1.0)
```

Current database contains 2,962 articles with 1552 kB storage.

## Application Architecture

### Flask Application Structure
```
electrek_scraper/
├── __init__.py              # App factory with blueprint registration
├── config.py                # Environment configuration
├── models.py                # Database models and queries
├── public_views.py          # Public routes (articles, auth)
├── admin_views.py           # Protected admin routes (scraping, analytics)
├── auth.py                  # Authentication decorators and helpers
├── utils/                   # Utility modules
│   ├── scraper_service.py   # Web scraping functionality
│   ├── sentiment_service.py # AI-powered sentiment analysis
│   ├── cache_service.py     # File-based caching system
│   ├── reading_time.py      # Reading time estimation
│   └── proxy_manager.py     # HTTP proxy management
├── templates/               # Jinja2 HTML templates
│   ├── public_base.html     # Clean public template
│   ├── admin/base.html      # Admin dashboard template
│   ├── articles/            # Public article templates
│   ├── auth/                # Authentication templates
│   └── admin/               # Protected admin templates
└── static/                  # CSS, JS, and image assets
    ├── css/medium-style.css # Medium-style public design
    ├── css/style.css        # Admin dashboard styles
    ├── cache/               # File cache storage
    └── favicon/
```

### Key Routes

**Public Routes (no authentication required):**
- `/` - Clean article overview page with reading times
- `/articles/tesla-hate-machine` - Tesla analysis article (cached 30 days)
- `/login` - Google OAuth login page
- `/auth/google` - Initiate OAuth flow
- `/auth/callback` - OAuth callback handler
- `/logout` - Clear session and redirect

**Admin Routes (Google OAuth required - lancecj@gmail.com only):**
- `/admin/` - Admin dashboard with article listing and controls
- `/admin/scrape` (POST) - Trigger web scraping operation
- `/admin/reports` - Analytics dashboard with charts and statistics
- `/admin/business_of_hate_blog` - Admin view of Tesla analysis
- `/admin/analyze_sentiments` (POST) - Batch sentiment analysis

## Core Functionality

### 1. Authentication System (`auth.py`)
- **Google OAuth Integration**: Uses Supabase's built-in Google OAuth
- **Access Control**: Restricts admin access to single email (lancecj@gmail.com)
- **JWT Token Management**: Secure session handling with refresh tokens
- **Route Protection**: Decorators for admin-only and user-required routes
- **Session Management**: Proper login/logout flow with error handling

**Authentication Flow**:
1. User clicks "Sign in with Google" on `/login`
2. Redirected to Google OAuth via Supabase
3. OAuth callback validates and creates session
4. JWT tokens stored in Flask session
5. Admin routes check email authorization

### 2. Performance & Caching (`cache_service.py`)
- **File-based Cache**: Stores chart data locally for 30 days
- **Vercel CDN Integration**: 30-day CDN caching for Tesla article
- **Reading Time Cache**: Pre-calculated reading estimates
- **Chart Data Bundling**: All database queries cached as single object
- **Instant Load Times**: 80-90% faster after first visit

**Performance Strategy**:
1. First visitor: Generate data + cache locally + serve to CDN
2. Subsequent visitors: Instant CDN delivery
3. Cache expires automatically after 30 days
4. Local fallback for development

### 3. Web Scraping (`scraper_service.py`)
- **Multi-page scraping**: Configurable to scrape 1-80 pages
- **Rate limiting**: Progressive delays and randomization to avoid detection
- **Proxy support**: Built-in proxy management for reliability
- **Duplicate detection**: Prevents re-scraping existing articles
- **Robust parsing**: Extracts title, author, publish date, and comment count
- **Error handling**: Graceful failure handling with detailed logging

### 4. Reading Time Estimation (`reading_time.py`)
- **Word Count Analysis**: Strips HTML and counts readable words
- **Reading Speed**: 250 words per minute average
- **Visual Element Bonus**: +30 seconds per chart/image
- **Clean Display**: "X min read" badges in Medium style
- **Template Integration**: Works with both overview cards and article headers

### 5. Sentiment Analysis (`sentiment_service.py`)
- **AI-Powered**: Uses OpenAI GPT-4o for sophisticated sentiment analysis
- **Contextual Understanding**: Includes few-shot learning examples
- **Score Range**: -1.0 (very negative) to 1.0 (very positive)
- **Categories**: Very negative, negative, slightly negative, neutral, slightly positive, positive, very positive
- **Color Coding**: Visual sentiment representation with color gradients
- **Batch Processing**: Handles large datasets with rate limiting

**Sentiment Categories**:
- Very Positive (≥0.7): Strong green (#28a745)
- Positive (≥0.3): Medium green (#5cb85c)
- Slightly Positive (≥0.1): Light green (#8bc34a)
- Neutral (-0.1 to 0.1): Gray (#6c757d)
- Slightly Negative (≤-0.1): Light red (#f08080)
- Negative (≤-0.3): Medium red (#e74c3c)
- Very Negative (≤-0.7): Strong red (#dc3545)

### 3. Data Analytics (`models.py`)
- **Comprehensive Statistics**: Total articles, comments, averages, maximums
- **Time-based Filtering**: Monthly, quarterly, yearly analysis
- **Correlation Analysis**: Sentiment vs. engagement correlation
- **Pagination Support**: Handles large datasets efficiently
- **Data Validation**: Type checking and error handling

## User Experience

### Public Site Experience
**Landing Page (`/`)**:
- **Clean Design**: Medium-style typography with SF Pro Display
- **Article Cards**: Horizontal layout with reading times and categories
- **Responsive**: Mobile-optimized with elegant hover effects
- **Performance**: Cached for 6 hours, instant loading

**Tesla Article (`/articles/tesla-hate-machine`)**:
- **Professional Layout**: Clean article header with reading time badge
- **Interactive Charts**: Four Chart.js visualizations with hover tooltips
- **Data Analysis**: 2,962 articles analyzed with statistical insights
- **Performance**: 30-day CDN caching for instant loading
- **Mobile Friendly**: Responsive design for all screen sizes

### Admin Dashboard Experience
**Admin Homepage (`/admin/`)**:
- **Article Management**: Sortable table with all scraped articles
- **Sorting Options**: Newest, oldest, most comments, most negative
- **Content Filtering**: Tesla/Elon, BYD, or non-Tesla article filters
- **Scraping Controls**: Configurable article limit (1-2000) and page count (1-80)
- **Real-time Feedback**: Progress indicators and status messages
- **Sentiment Display**: Color-coded sentiment badges with scores

**Analytics Dashboard (`/admin/reports`)**:
- **Interactive Charts**: Correlation analysis, engagement metrics, sentiment trends
- **Statistical Summary**: Key metrics and business insights
- **Global Filtering**: Apply Tesla/BYD filters across all visualizations
- **Responsive Design**: Mobile-friendly dashboard layout

### Authentication Experience
- **Google OAuth**: Single-click "Sign in with Google" button
- **Clean Design**: Standalone login page with glassmorphism effects
- **Access Control**: Automatic redirect based on authentication status
- **Error Handling**: Graceful failure messages and retry options

## Configuration & Environment

### Required Environment Variables
```bash
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key

# Supabase Database & Authentication
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key

# AI Services
OPENAI_API_KEY=your-openai-api-key

# Optional Features
USE_PROXY=true/false (optional)
```

### Authentication Setup
1. **Google Cloud Console**: Create OAuth 2.0 credentials
2. **Supabase Auth**: Configure Google provider with client credentials
3. **Redirect URLs**: Set callback URLs for production/development
4. **Test Users**: Add allowed email addresses in Google Cloud Console
5. **RLS Policies**: Database-level access control automatically configured

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run development server
python app.py
```

## API Capabilities

### Web Scraping API
- **Configurable Limits**: Up to 2000 articles, 80 pages
- **Duplicate Prevention**: Automatic URL existence checking
- **Progress Tracking**: Detailed logging and statistics
- **Error Recovery**: Continues processing despite individual failures

### Sentiment Analysis API
- **Batch Processing**: Analyzes 25 articles per batch
- **Rate Limiting**: Built-in delays to respect API limits
- **Cost Management**: Configurable batch sizes to control API costs
- **Progress Tracking**: Real-time analysis feedback

### Data Export
- **JSON API**: Programmatic access to article data
- **Flexible Queries**: Filtering, sorting, and pagination support
- **Statistical Endpoints**: Pre-calculated analytics data

## Performance & Scalability

### Database Optimization
- **Pagination**: Handles large datasets with efficient queries
- **Indexing**: Optimized for common query patterns
- **Connection Pooling**: Supabase managed connections

### Scraping Performance
- **Rate Limiting**: Prevents target site overload
- **Proxy Rotation**: Improves reliability and speed
- **Error Handling**: Robust failure recovery

### Frontend Performance
- **Lazy Loading**: Efficient data loading strategies
- **Client-side Filtering**: Fast interactive filtering
- **Optimized Assets**: Minified CSS/JS from CDNs

## Use Cases

1. **Content Analysis**: Understanding sentiment patterns in EV journalism
2. **Engagement Research**: Correlation between headline sentiment and reader comments
3. **Competitive Intelligence**: Tracking coverage of specific companies (Tesla, BYD, etc.)
4. **Market Research**: Identifying trending topics and sentiment shifts
5. **Editorial Insights**: Understanding what content drives engagement

## Security & Access Control

- **Google OAuth**: Industry-standard authentication with Supabase integration
- **Email-based Authorization**: Single admin user (lancecj@gmail.com) with JWT validation
- **Route Protection**: Decorator-based access control for admin functionality
- **Session Security**: Secure JWT token handling with refresh capability
- **Environment Variables**: All credentials stored securely in environment
- **Input Validation**: Parameterized queries and form validation
- **Rate Limiting**: Prevents abuse of scraping endpoints
- **HTTPS**: Secure API communications throughout

## Performance Optimization

- **30-Day CDN Caching**: Tesla article cached on Vercel's global CDN
- **File-based Caching**: Local chart data caching for development
- **Reading Time Pre-calculation**: Cached with article metadata
- **Optimized Database Queries**: Efficient pagination and filtering
- **Bundle Chart Data**: Single cache object reduces query overhead
- **Instant Load Times**: 80-90% performance improvement after first visit

## Deployment Architecture

### Production Environment (Vercel)
- **Serverless Functions**: Flask routes deployed as serverless functions
- **Global CDN**: 30-day caching for public articles
- **Environment Variables**: Secure credential management
- **Database**: Supabase managed PostgreSQL with global access
- **Authentication**: Supabase handles OAuth flow and session management

### Development Environment
- **Local File Cache**: Fallback caching for development
- **Hot Reload**: Flask development server with auto-reload
- **Environment Sync**: `.env` file for local credential management

This application demonstrates modern Flask architecture with public/private separation, advanced caching strategies, and production-ready authentication for content analysis and engagement research.