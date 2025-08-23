from django.shortcuts import render, get_object_or_404, redirect
from .models import Bill, Feedback
from django.utils import timezone
from django.contrib import messages
from .scraper import BillScraper
from datetime import datetime
from django.contrib.auth.decorators import login_required
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

sia = SentimentIntensityAnalyzer()


# Homepage → list bills 
@login_required
def home(request):
    scraper = BillScraper()
    articles_data = scraper.scrape_bills()
    
    print(f"Found {len(articles_data)} articles")  
    
    # Update or create articles as bills
    for article in articles_data:
        print(f"Processing article: {article['title']}")  
        Bill.objects.update_or_create(
            title=article['title'],
            defaults={
                'summary': article['summary'],
                'created_at': datetime.now()
            }
        )
    
    bills = Bill.objects.all().order_by('-created_at')
    print(f"Total bills in database: {bills.count()}")  
    return render(request, 'ada/home.html', {'bills': bills, 'scraped_count': len(articles_data)})

def dashboard(request, bill_id):
     bill = get_object_or_404(Bill, id=bill_id)
     feedbacks = bill.feedbacks.all()
     support_count = feedbacks.filter(user_sentiment="support").count()
     oppose_count = feedbacks.filter(user_sentiment="oppose").count()
     suggest_count = feedbacks.filter(user_sentiment="suggest").count()
     return render(request, "ada/dashboard.html", { "bill": bill, "support": support_count, "oppose": oppose_count, "suggest": suggest_count, "feedbacks": feedbacks })



from django.shortcuts import render, get_object_or_404, redirect
from .models import Bill, Feedback
from nltk.sentiment import SentimentIntensityAnalyzer

# ✅ Initialize once
analyzer = SentimentIntensityAnalyzer()


def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    feedbacks = bill.feedbacks.all().order_by("-submitted_at")

    if request.method == "POST":
        comment = request.POST.get("comment")
        user_sentiment = request.POST.get("user_sentiment")

        if comment:
            sentiment_score = analyzer.polarity_scores(comment)["compound"]
            if sentiment_score >= 0.05:
                ai_sentiment = "support"
            elif sentiment_score <= -0.05:
                ai_sentiment = "oppose"
            else:
                ai_sentiment = "neutral"

            feedback = Feedback(
                bill=bill,
                user=request.user,  # links feedback to logged-in user
                comment=comment,
                user_sentiment=user_sentiment,
                ai_sentiment=ai_sentiment,
                ai_confidence=abs(sentiment_score)
            )
            feedback.save()
            return redirect("bill_detail", bill_id=bill.pk)

    return render(request, "ada/bill_detail.html", {
        "bill": bill,
        "feedbacks": feedbacks
    })

