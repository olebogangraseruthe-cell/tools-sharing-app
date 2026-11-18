from django.conf import settings
from django.db import models


class Tool(models.Model):
    CATEGORY_CHOICES = [
        ('power', 'Power tools'),
        ('hand', 'Hand tools'),
        ('garden', 'Garden & lawn'),
        ('ladders', 'Ladders'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tools'
    )
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='tools/', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='requests')
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrow_requests'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.borrower} -> {self.tool} ({self.status})'