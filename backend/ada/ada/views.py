
from datetime import datetime
import re


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from .models import Bill, Feedback
from .scraper import BillScraper


analyzer = SentimentIntensityAnalyzer()


#@login_required
def home(request):
    """
    Scrapes for new bills, updates the database, and displays a list of all bills.
    """
    scraper = BillScraper()
    articles_data = scraper.scrape_bills()
    
    print(f"Found {len(articles_data)} articles")  
    
    for article in articles_data:
        
        year = None
        title = article['title']
        match = re.search(r'\b\d{4}\b', title)
        if match:
            year = int(match.group(0))

        print(f"Processing article: {title} | Year: {year}")
        
        Bill.objects.update_or_create(
            title=title,
            defaults={
                'summary': article['summary'],
                'url': article['url'],
                'created_at': year, 
            }
        )
    

    bills = Bill.objects.all().order_by('created_at', 'title')
    
    print(f"Total bills in database: {bills.count()}")  
    return render(request, 'ada/home.html', {'bills': bills, 'scraped_count': len(articles_data)})


def dashboard(request, bill_id):
    """
    Displays a dashboard with sentiment analysis for a specific bill.
    """
    bill = get_object_or_404(Bill, id=bill_id)
    feedbacks = bill.feedbacks.all()
    

    support_count = feedbacks.filter(user_sentiment="support").count()
    oppose_count = feedbacks.filter(user_sentiment="oppose").count()
    suggest_count = feedbacks.filter(user_sentiment="suggest").count()
    
    return render(request, "ada/dashboard.html", {
        "bill": bill,
        "support": support_count,
        "oppose": oppose_count,
        "suggest": suggest_count,
        "feedbacks": feedbacks
    })


def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    feedbacks = bill.feedbacks.all().order_by("-submitted_at")

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to submit feedback.")
            return redirect('login')

        if Feedback.objects.filter(bill=bill, user=request.user).exists():
            messages.warning(request, "You have already submitted feedback for this bill.")
            return redirect("bill_detail", bill_id=bill.id)

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

            Feedback.objects.create(
                bill=bill,
                user=request.user,
                comment=comment,
                user_sentiment=user_sentiment if user_sentiment else None,
                ai_sentiment=ai_sentiment,
                ai_confidence=abs(sentiment_score)
            )

            messages.success(request, "Your feedback has been submitted successfully!")
            return redirect("bill_detail", bill_id=bill.id)


    support_count = feedbacks.filter(user_sentiment="support").count()
    oppose_count = feedbacks.filter(user_sentiment="oppose").count()
    neutral_count = feedbacks.filter(user_sentiment="neutral").count()


    support_comments = feedbacks.filter(user_sentiment="support").values_list("comment", flat=True)[:5]
    oppose_comments = feedbacks.filter(user_sentiment="oppose").values_list("comment", flat=True)[:5]
    neutral_comments = feedbacks.filter(user_sentiment="neutral").values_list("comment", flat=True)[:5]


    has_voted = False
    if request.user.is_authenticated:
        has_voted = Feedback.objects.filter(bill=bill, user=request.user).exists()

    return render(request, "ada/bill_detail.html", {
        "bill": bill,
        "feedbacks": feedbacks,
        "has_voted": has_voted,
        "support_count": support_count,
        "oppose_count": oppose_count,
        "neutral_count": neutral_count,
        "support_comments": support_comments,
        "oppose_comments": oppose_comments,
        "neutral_comments": neutral_comments,
    })



def login_view(request):
    """
    Handles user login.
    """
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
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def register(request):
    """
    Handles user registration.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
