from django.shortcuts import render, get_object_or_404, redirect
from .models import Bill, Feedback
from django.utils import timezone

# Import VADER
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()


# Homepage → list bills 
def home(request): 
    bills = Bill.objects.all() 
    return render(request, "home.html", {"bills": bills})

def dashboard(request, bill_id):
     bill = get_object_or_404(Bill, id=bill_id)
     feedbacks = bill.feedbacks.all()
     support_count = feedbacks.filter(sentiment="support").count()
     oppose_count = feedbacks.filter(sentiment="oppose").count()
     suggest_count = feedbacks.filter(sentiment="suggest").count()
     return render(request, "dashboard.html", { "bill": bill, "support": support_count, "oppose": oppose_count, "suggest": suggest_count, "feedbacks": feedbacks })

def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)

    if request.method == "POST":
        sentiment_choice = request.POST.get("sentiment")
        comment_text = request.POST.get("comment")

        # Run AI Sentiment Analysis
        ai_result = sia.polarity_scores(comment_text)
        compound = ai_result["compound"]

        # Decide AI sentiment label
        if compound >= 0.05:
            ai_sentiment = "positive"
        elif compound <= -0.05:
            ai_sentiment = "negative"
        else:
            ai_sentiment = "neutral"

        ai_confidence = abs(compound)  # confidence = intensity of sentiment

        # Save Feedback with AI fields
        Feedback.objects.create(
            bill=bill,
            sentiment=sentiment_choice,
            comment=comment_text,
            ai_sentiment=ai_sentiment,
            ai_confidence=ai_confidence,
            submitted_at=timezone.now()
        )

        return redirect("bill_detail", pk=bill.pk)

    feedbacks = bill.feedbacks.all()
    return render(request, "bill_detail.html", {"bill": bill, "feedbacks": feedbacks})
