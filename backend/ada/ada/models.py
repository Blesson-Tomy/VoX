from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


class Bill(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ada_bill'

    def __str__(self):
        return self.title


class Feedback(models.Model):
    SENTIMENT_CHOICES = [
        ("support", "Support"),
        ("oppose", "Oppose"),
        ("suggest", "Suggestion"),
        ("neutral", "Neutral"),  # <- useful when AI detects no strong opinion
    ]

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="feedbacks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # ✅ portable
    
    # User’s selected sentiment (optional, can be blank if AI decides)
    user_sentiment = models.CharField(
        max_length=10, choices=SENTIMENT_CHOICES, blank=True, #null=True
    )
    
    # AI-generated sentiment
    ai_sentiment = models.CharField(
        max_length=10, choices=SENTIMENT_CHOICES, blank=True, null=True
    )

    # Confidence score from AI model (0–1)
    ai_confidence = models.FloatField(blank=True, null=True)

    # Raw comment
    comment = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ada_feedback'

    def __str__(self):
        return f"{self.bill.title} - {self.user_sentiment or self.ai_sentiment}"
