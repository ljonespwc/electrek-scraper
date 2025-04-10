# electrek_scraper/views.py
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from datetime import datetime, timedelta
from .models import Article
from .utils.scraper_service import ElectrekScraper

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Homepage showing recent articles and scraper controls"""
    # Get the sort order
    sort = request.args.get('sort', 'newest')
    ascending = sort == 'oldest'
    
    # Get the last time we scraped
    last_scraped = request.args.get('last_scraped', None)
    
    # Get recent articles
    articles = Article.get_all(limit=50, order_by="published_at", ascending=ascending)
    
    return render_template('index.html', 
                          articles=articles,
                          last_scraped=last_scraped,
                          sort=sort)

@bp.route('/scrape', methods=['POST'])
def scrape():
    """Trigger a scraping job with better error handling"""
    print("=" * 50)
    print("STARTING SCRAPE OPERATION")
    print("=" * 50)
    
    try:
        # Get the number of articles and pages to scrape
        article_limit = int(request.form.get('article_limit', 25))
        article_limit = min(max(1, article_limit), 1000)  # Increased max to 1000

        page_count = int(request.form.get('page_count', 1))
        page_count = min(max(1, page_count), 40)  # Increased max to 40 pages
        
        print(f"Article limit set to: {article_limit}, Pages: {page_count}")
        
        # Add the warning message right here
        if page_count > 10 or article_limit > 250:
            print("⚠️ WARNING: Large scraping job requested. This may take a while and put significant load on the target site.")
            flash('Large scraping job started. This may take a while to complete.', 'warning')
        
        scraper = ElectrekScraper()
        
        # Get recent article URLs from multiple pages
        print(f"Fetching up to {article_limit} articles across {page_count} pages...")
        article_urls = scraper.get_article_urls(limit=article_limit, pages=page_count)
        
        if not article_urls:
            print("No articles found on the homepage.")
            flash('No articles found on the homepage.', 'warning')
            return redirect(url_for('main.index'))
        
        print(f"Found {len(article_urls)} article URLs")
        
        # Track results
        results = {
            "total": len(article_urls),
            "success": [],
            "skipped": [],
            "failed": []
        }
        
        # Process each URL
        for i, url in enumerate(article_urls):
            print(f"\nProcessing article {i+1}/{len(article_urls)}: {url}")
            
            # Skip if article already exists
            try:
                if Article.url_exists(url):
                    print(f"  - Skipping (already exists in database)")
                    results["skipped"].append(url)
                    continue
            except Exception as e:
                print(f"  - Warning: Error checking if article exists: {str(e)}")
            
            try:
                # Parse the article
                print(f"  - Parsing article metadata...")
                article_data = scraper.parse_article(url)
                
                # Store in database
                print(f"  - Storing article in database...")
                creation_result = Article.create(article_data)
                print(f"  - Database insert result: {creation_result}")
                
                results["success"].append(url)
                print(f"  - SUCCESS: Article stored")
            except Exception as e:
                print(f"  - FAILED: Error processing article: {str(e)}")
                import traceback
                print(traceback.format_exc())
                results["failed"].append({"url": url, "error": str(e)})
                
                # If this was a duplicate URL error, categorize it as skipped instead of failed
                error_str = str(e).lower()
                if "duplicate" in error_str or "unique constraint" in error_str or "already exists" in error_str:
                    print(f"  - Reclassifying as skipped (duplicate URL)")
                    # Move from failed to skipped
                    results["failed"].pop()
                    results["skipped"].append(url)
        
        # Create success message with stats
        success_count = len(results["success"])
        skipped_count = len(results["skipped"])
        failed_count = len(results["failed"])
        
        print("\n" + "=" * 50)
        print(f"SCRAPE SUMMARY: {success_count} added, {skipped_count} skipped, {failed_count} failed")
        print("=" * 50)
        
        if success_count > 0:
            flash(f'Successfully scraped {success_count} articles. Skipped {skipped_count}. Failed {failed_count}.', 'success')
        elif skipped_count > 0 and failed_count == 0:
            flash(f'All {skipped_count} articles already existed in the database.', 'info')
        elif failed_count > 0 and success_count == 0:
            flash(f'Failed to scrape any articles. {failed_count} errors occurred.', 'danger')
        else:
            flash('No new articles were processed.', 'info')
            
        # Pass the current time for display
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return redirect(url_for('main.index', last_scraped=current_time))
        
    except Exception as e:
        print(f"CRITICAL ERROR IN SCRAPE OPERATION: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash(f'An error occurred: {str(e)}', 'danger')
        # Ensure we redirect back to the index even on critical errors
        return redirect(url_for('main.index'))
        
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        flash(f'An error occurred: {str(e)}', 'danger')
        return redirect(url_for('main.index'))

@bp.route('/api/articles')
def api_articles():
    """API endpoint to get articles as JSON"""
    limit = request.args.get('limit', 20, type=int)
    articles = Article.get_all(limit=limit)
    return jsonify(articles)

@bp.route('/test')
def test_route():
    print("Test route accessed!")
    return "Test route works! Check your console for the print statement."