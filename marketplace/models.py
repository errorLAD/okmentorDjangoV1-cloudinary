from django.db import models
from django.contrib.auth.models import User

class MentorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    expertise_tags = models.CharField(max_length=255, help_text="Comma-separated tags")
    domains = models.CharField(max_length=255, help_text="Comma-separated domains (tech, marketing, etc.)")
    is_mentor = models.BooleanField(default=False)
    calendar_link = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    # KYC fields
    kyc_status = models.CharField(max_length=20, choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')], default='pending')
    kyc_document = models.FileField(upload_to='kyc_docs/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class AvailabilitySlot(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='availability_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.mentor.user.username}: {self.start_time} - {self.end_time}"

class Service(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.mentor.user.username})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='bookings')
    scheduled_time = models.DateTimeField()
    payment_status = models.CharField(max_length=20, choices=[('pending','Pending'),('paid','Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.mentor.user.username} ({self.service.name})"

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.user.username} review by {self.user.username}"

class DigitalProduct(models.Model):
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='digital_products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    file = models.FileField(upload_to='digital_products/', blank=True, null=True, help_text="Optional: upload a digital file for download.")
    delivery_instructions = models.TextField(blank=True, help_text="Instructions for how the product will be delivered (e.g., email, link, etc.)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.mentor.user.username})"

class DigitalProductOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digital_product_orders')
    product = models.ForeignKey(DigitalProduct, on_delete=models.CASCADE, related_name='orders')
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_delivered = models.BooleanField(default=False)
    # Add payment fields as needed

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}"
