from django.db import models

class CaseIntake(models.Model):
    CASE_TYPES = [
        ('TRAFFIC', 'Traffic Fine'),
        ('LOAN', 'Small Loan Dispute'),
        ('FAMILY', 'Family Dispute'),
    ]

    case_type = models.CharField(max_length=20, choices=CASE_TYPES)
    complainant_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField()
    supporting_documents = models.FileField(upload_to='case_documents/', blank=True)
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='PENDING')

    def __str__(self):
        return f"{self.case_type} - {self.complainant_name}"