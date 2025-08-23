from django.shortcuts import render, get_object_or_404, redirect
from .models import Bill, Feedback


# Homepage → list bills
def home(request):
    bills = Bill.objects.all()
    return render(request, "home.html", {"bills": bills})

# Bill detail → show bill + feedback form
def bill_detail(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    message = ""

    if request.method == "POST":
        sentiment = request.POST.get("sentiment")
        comment = request.POST.get("comment", "")
        Feedback.objects.create(bill=bill, sentiment=sentiment, comment=comment)
        message = "Feedback submitted successfully!"

    feedbacks = bill.feedbacks.all()
    return render(request, "bill_detail.html", {
        "bill": bill,
        "feedbacks": feedbacks,
        "message": message
    })

# Dashboard → show charts
def dashboard(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    feedbacks = bill.feedbacks.all()

    support_count = feedbacks.filter(sentiment="support").count()
    oppose_count = feedbacks.filter(sentiment="oppose").count()
    suggest_count = feedbacks.filter(sentiment="suggest").count()

    return render(request, "dashboard.html", {
        "bill": bill,
        "support": support_count,
        "oppose": oppose_count,
        "suggest": suggest_count,
        "feedbacks": feedbacks
    })