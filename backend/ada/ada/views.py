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
     support_count = feedbacks.filter(sentiment="support").count()
     oppose_count = feedbacks.filter(sentiment="oppose").count()
     suggest_count = feedbacks.filter(sentiment="suggest").count()
     return render(request, "dashboard.html", { "bill": bill, "support": support_count, "oppose": oppose_count, "suggest": suggest_count, "feedbacks": feedbacks })


from django.shortcuts import render, get_object_or_404, redirect
from .models import Bill, Feedback
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    feedbacks = bill.feedbacks.all().order_by("-submitted_at")  # newest first
    feedbacks = bill.feedbacks.all().order_by("-submitted_at")  # newest first

    if request.method == "POST":
        comment = request.POST.get("comment")
        user_sentiment = request.POST.get("user_sentiment")  # <- get from form

        if comment:
            feedback = Feedback(
                bill=bill,
                comment=comment,
                user_sentiment=user_sentiment if user_sentiment else None
            )

            # Run sentiment analysis
            sentiment_score = analyzer.polarity_scores(comment)["compound"]

            if sentiment_score >= 0.05:
                feedback.ai_sentiment = "support"
            elif sentiment_score <= -0.05:
                feedback.ai_sentiment = "oppose"
            else:
                feedback.ai_sentiment = "neutral"

            # Save AI confidence score
            feedback.ai_confidence = abs(sentiment_score)

            feedback.save()
            return redirect("ada/bill_detail", pk=bill.pk)
        comment = request.POST.get("comment")
        user_sentiment = request.POST.get("user_sentiment")  # <- get from form

        if comment:
            feedback = Feedback(
                bill=bill,
                comment=comment,
                user_sentiment=user_sentiment if user_sentiment else None
            )

            # Run sentiment analysis
            sentiment_score = analyzer.polarity_scores(comment)["compound"]

            if sentiment_score >= 0.05:
                feedback.ai_sentiment = "support"
            elif sentiment_score <= -0.05:
                feedback.ai_sentiment = "oppose"
            else:
                feedback.ai_sentiment = "neutral"

            # Save AI confidence score
            feedback.ai_confidence = abs(sentiment_score)

            feedback.save()
            return redirect("ada/bill_detail", pk=bill.pk)

    return render(request, "ada/bill_detail.html", {
        "bill": bill,
        "feedbacks": feedbacks,
    })

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
