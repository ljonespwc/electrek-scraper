# Electrek Monitor - Flask Web Application

**Project ID**: `icooetipqrnaxrazjrgk` (use this for all MCP database operations)

## Development Workflow Rules
When working on this project, always follow these 7 rules:
1. **Plan First**: Think through the problem, read the codebase for relevant files, and write a plan to `docs/todo.md`
2. **Create Todo List**: The plan should have a list of todo items that you can check off as you complete them
3. **Get Approval**: Before beginning work, check in with the user and get verification of the plan
4. **Execute Incrementally**: Work on todo items one by one, marking them as complete as you go
5. **Communicate Changes**: Give high-level explanations of what changes you made at each step
6. **Keep It Simple**: Make every task and code change as simple as possible. Avoid massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. **Document Results**: Add a review section to the `docs/todo.md` file with a summary of the changes made and any other relevant information

## Project Overview
Electrek Monitor is a comprehensive Flask web application designed to scrape, analyze, and visualize article data from Electrek.co (electric vehicle news website). The application provides sentiment analysis of headlines, engagement tracking through comment counts, and detailed analytics dashboards to understand reader engagement patterns.

## Technology Stack

### Backend
- **Framework**: Flask 3.1.0 (Python web framework)
- **Database**: Supabase (PostgreSQL-based cloud database)
- **Web Scraping**: BeautifulSoup4 for HTML parsing
- **Sentiment Analysis**: OpenAI GPT-4o API for advanced sentiment scoring
- **HTTP Requests**: requests library with proxy support
- **Data Processing**: NumPy for correlation calculations

### Frontend
- **UI Framework**: Bootstrap 5.3.0 for responsive design
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for data visualization
- **Styling**: Custom CSS with modern dashboard design
- **JavaScript**: Vanilla JS for dynamic filtering and interactions

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
├── __init__.py          # App factory and configuration
├── config.py            # Environment configuration
├── models.py            # Database models and queries
├── views.py             # Route handlers and business logic
├── utils/               # Utility modules
│   ├── scraper_service.py    # Web scraping functionality
│   ├── sentiment_service.py  # AI-powered sentiment analysis
│   ├── analyze_sentiments.py # Batch sentiment processing
│   └── proxy_manager.py      # HTTP proxy management
├── templates/           # Jinja2 HTML templates
│   ├── base.html            # Base template with navigation
│   ├── index.html           # Article listing page
│   └── reports.html         # Analytics dashboard
└── static/              # CSS, JS, and image assets
    ├── css/
    ├── js/
    └── img/
```

### Key Routes
- `/` - Homepage with article listing and scraping controls
- `/scrape` (POST) - Trigger web scraping operation
- `/reports` - Analytics dashboard with charts and statistics
- `/analyze_sentiments` (POST) - Batch sentiment analysis
- `/api/articles` - JSON API endpoint for article data
- `/health` - Application health check

## Core Functionality

### 1. Web Scraping (`scraper_service.py`)
- **Multi-page scraping**: Configurable to scrape 1-80 pages
- **Rate limiting**: Progressive delays and randomization to avoid detection
- **Proxy support**: Built-in proxy management for reliability
- **Duplicate detection**: Prevents re-scraping existing articles
- **Robust parsing**: Extracts title, author, publish date, and comment count
- **Error handling**: Graceful failure handling with detailed logging

**Scraping Process**:
1. Fetch article URLs from Electrek.co homepage and pagination
2. Parse individual article pages for metadata
3. Store unique articles in Supabase database
4. Provide real-time progress feedback

### 2. Sentiment Analysis (`sentiment_service.py`)
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

### Homepage (`index.html`)
- **Article Listing**: Sortable table with all scraped articles
- **Sorting Options**: Newest, oldest, most comments, most negative
- **Content Filtering**: Tesla/Elon, BYD, or non-Tesla article filters
- **Scraping Controls**: Configurable article limit (1-2000) and page count (1-80)
- **Real-time Feedback**: Progress indicators and status messages
- **Sentiment Display**: Color-coded sentiment badges with scores

### Analytics Dashboard (`reports.html`)
- **Title**: "The Business of Hate: By the Numbers" - reflects analysis focus
- **Interactive Charts**: 
  - Sentiment vs. Comment Count correlation scatter plot
  - Monthly trend analysis with engagement metrics
  - Sentiment distribution analysis
- **Statistical Summary**: Key metrics and insights
- **Global Filtering**: Apply Tesla/BYD filters across all visualizations
- **Responsive Design**: Mobile-friendly dashboard layout

### Key UI Features
- **Bootstrap Integration**: Modern, responsive design
- **Loading States**: Visual feedback during long operations
- **Flash Messages**: Color-coded success/error notifications
- **Mobile Responsive**: Optimized for all device sizes
- **Accessibility**: Semantic HTML and ARIA labels

## Configuration & Environment

### Required Environment Variables
```bash
FLASK_SECRET_KEY=your-secret-key
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
USE_PROXY=true/false (optional)
```

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

## Security Considerations

- **Environment Variables**: Secure credential management
- **Input Validation**: Parameterized queries and form validation
- **Rate Limiting**: Prevents abuse of scraping endpoints
- **Error Handling**: No sensitive information in error messages
- **HTTPS**: Secure API communications

## Deployment Notes

- **Flask Production**: Use WSGI server (Gunicorn, uWSGI) for production
- **Environment**: Supports various deployment platforms
- **Database**: Supabase provides managed PostgreSQL with global CDN
- **Monitoring**: Built-in health check endpoint (`/health`)

This application demonstrates modern web scraping, AI integration, and data visualization techniques in a production-ready Flask application focused on content analysis and engagement research.