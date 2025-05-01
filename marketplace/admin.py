from django.contrib import admin
from django.contrib.auth.models import User
from .models import MentorProfile, Service, Booking, Review, Message, AvailabilitySlot

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_mentor', 'kyc_status')
    list_filter = ('is_mentor', 'kyc_status')
    search_fields = ('user__username', 'user__email', 'domains', 'expertise_tags')
    actions = ['approve_kyc', 'reject_kyc']

    def approve_kyc(self, request, queryset):
        queryset.update(kyc_status='approved')
    approve_kyc.short_description = "Approve selected KYC"

    def reject_kyc(self, request, queryset):
        queryset.update(kyc_status='rejected')
    reject_kyc.short_description = "Reject selected KYC"

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'mentor', 'price', 'description')
    search_fields = ('name', 'mentor__user__username')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'mentor', 'service', 'scheduled_time', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('user__username', 'mentor__user__username', 'service__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'user', 'rating', 'created_at')
    search_fields = ('mentor__user__username', 'user__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')
    search_fields = ('sender__username', 'receiver__username')

@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked',)
    search_fields = ('mentor__user__username',)

