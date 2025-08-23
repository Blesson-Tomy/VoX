from django.db import models

class Bill(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'ada_bill'


class Feedback(models.Model):
    SENTIMENT_CHOICES = [
        ("support", "Support"),
        ("oppose", "Oppose"),
        ("suggest", "Suggestion"),
    ]

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="feedbacks")
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill.title} - {self.sentiment}"
