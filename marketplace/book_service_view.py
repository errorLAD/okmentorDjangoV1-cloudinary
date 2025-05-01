from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Service, Booking

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    mentor = service.mentor
    if request.method == 'POST':
        scheduled_time = request.POST.get('scheduled_time')
        # Create the booking
        Booking.objects.create(
            user=request.user,
            service=service,
            mentor=mentor,
            scheduled_time=scheduled_time,
            payment_status='pending'
        )
        return render(request, 'mentor/book_service.html', {'service': service, 'success': True})
    return render(request, 'mentor/book_service.html', {'service': service})
