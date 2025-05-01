from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import MentorProfile, Service, Booking, DigitalProduct, DigitalProductOrder
from .book_service_view import book_service
from .forms import MentorSignupForm, ServiceForm, AvailabilitySlotForm, MenteeSignupForm, DigitalProductForm, MentorProfileForm
from django.contrib.auth import login
from django.db.models import Q
import razorpay
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@login_required
def mentor_dashboard(request):
    """Mentor dashboard view showing mentor statistics and recent activities."""
    # Only allow users who are mentors
    if not hasattr(request.user, 'mentorprofile') or not request.user.mentorprofile.is_mentor:
        return redirect('home')
    
    # Get mentor profile
    mentor = request.user.mentorprofile
    
    # Calculate statistics
    total_sessions = Booking.objects.filter(mentor=mentor).count()
    return render(request, 'mentor/mentor_dashboard.html', {'total_sessions': total_sessions})

@login_required
def mentor_profile_update(request):
    """View for updating mentor's profile information."""
    if not hasattr(request.user, 'mentorprofile') or not request.user.mentorprofile.is_mentor:
        return redirect('home')
    
    mentor = request.user.mentorprofile
    if request.method == 'POST':
        form = MentorProfileForm(request.POST, request.FILES, instance=mentor)
        if form.is_valid():
            form.save()
            return redirect('mentor_dashboard')
    else:
        form = MentorProfileForm(instance=mentor)
    
    return render(request, 'mentor/profile_update.html', {'form': form})

@login_required
def mentor_settings(request):
    """View for mentor settings."""
    if not hasattr(request.user, 'mentorprofile') or not request.user.mentorprofile.is_mentor:
        return redirect('home')
    
    mentor = request.user.mentorprofile
    
    if request.method == 'POST':
        # Handle settings updates
        mentor.is_available = request.POST.get('is_available') == 'on'
        mentor.availability_hours = request.POST.get('availability_hours')
        mentor.save()
        return redirect('mentor_dashboard')
    
    return render(request, 'mentor/settings.html', {'mentor': mentor})

@login_required
def mentor_availability(request):
    """View for managing mentor availability slots."""
    if not hasattr(request.user, 'mentorprofile') or not request.user.mentorprofile.is_mentor:
        return redirect('home')
    
    mentor = request.user.mentorprofile
    slots = mentor.availabilityslot_set.all()
    
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.mentor = mentor
            slot.save()
            return redirect('mentor_availability')
    else:
        form = AvailabilitySlotForm()
    
    return render(request, 'mentor/availability.html', {
        'form': form,
        'slots': slots,
        'mentor': mentor
    })

def signup_options(request):
    return render(request, 'signup_options.html')

def mentee_signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = MenteeSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = MenteeSignupForm()
    return render(request, 'mentee_signup.html', {'form': form})

def home(request):
    slider_slides = [
        {
            'title': 'Personalized Guidance',
            'subtitle': 'Get 1:1 advice from industry leaders tailored to your career goals.',
            'image': 'https://randomuser.me/api/portraits/men/32.jpg',
        },
        {
            'title': 'Flexible Scheduling',
            'subtitle': 'Book sessions at times that work for you, anywhere in the world.',
            'image': 'https://randomuser.me/api/portraits/women/44.jpg',
        },
        {
            'title': 'Diverse Expertise',
            'subtitle': 'Find mentors in tech, business, design, and more.',
            'image': 'https://randomuser.me/api/portraits/men/85.jpg',
        },
        {
            'title': 'Real Success Stories',
            'subtitle': 'See how mentorship has transformed lives and careers.',
            'image': 'https://randomuser.me/api/portraits/women/65.jpg',
        },
    ]
    return render(request, 'home.html', {'slider_slides': slider_slides})

from django.db.models import Q

def mentor_list(request):
    q = request.GET.get('q', '').strip()
    selected_domain = request.GET.get('domain', '').strip()
    mentors = MentorProfile.objects.filter(is_mentor=True, kyc_status='approved')
    if q:
        mentors = mentors.filter(
            Q(user__first_name__icontains=q) |
            Q(user__username__icontains=q) |
            Q(bio__icontains=q) |
            Q(expertise_tags__icontains=q) |
            Q(domains__icontains=q)
        )
    # Gather all unique domains
    all_domains = set()
    for mentor in mentors:
        all_domains.update([d.strip() for d in mentor.domains.split(',') if d.strip()])
    domains = sorted(all_domains)
    # Filter by selected_domain
    if selected_domain:
        mentors = [m for m in mentors if selected_domain.lower() in [d.strip().lower() for d in m.domains.split(',')]]
    return render(request, 'mentor/mentor_list.html', {
        'mentors': mentors,
        'q': q,
        'domains': domains,
        'selected_domain': selected_domain,
    })

from django.shortcuts import redirect

def mentor_signup(request):
    if request.user.is_authenticated:
        return redirect('mentor_dashboard')
    if request.method == 'POST':
        form = MentorSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'mentor/dashboard.html')
    else:
        form = MentorSignupForm()
    return render(request, 'mentor/mentor_signup.html', {'form': form})

@login_required
def mentor_service_add(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.mentor = request.user.mentorprofile
            service.save()
            return render(request, 'mentor/service_form.html', {'form': form, 'success': True})
    else:
        form = ServiceForm()
    return render(request, 'mentor/service_form.html', {'form': form})

# Mentor dashboard
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def mentor_dashboard(request):
    # Only allow users who are mentors
    if not hasattr(request.user, 'mentorprofile') or not request.user.mentorprofile.is_mentor:
        return redirect('home')
    
    # Get mentor profile
    mentor = request.user.mentorprofile
    
    # Calculate statistics
    total_sessions = Booking.objects.filter(mentor=mentor).count()
    upcoming_sessions = Booking.objects.filter(mentor=mentor, scheduled_time__gt=timezone.now()).count()
    
    return render(request, 'mentor/mentor_dashboard.html', {
        'total_sessions': total_sessions,
        'upcoming_sessions': upcoming_sessions
    })

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'mentor/booking_detail.html', {'booking': booking})

@login_required
def digital_order_detail(request, order_id):
    order = get_object_or_404(DigitalProductOrder, id=order_id)
    return render(request, 'mentor/digital_order_detail.html', {'order': order})

@login_required
def mentor_digital_products(request):
    products = request.user.mentorprofile.digital_products.all()
    return render(request, 'mentor/digital_product_list.html', {'products': products, 'is_owner': True})

def digital_product_list(request):
    from .models import DigitalProduct
    products = DigitalProduct.objects.all()
    return render(request, 'mentor/digital_product_list.html', {'products': products, 'is_owner': False})

from .models import DigitalProduct, DigitalProductOrder
from django.contrib.auth.decorators import login_required

@login_required
def user_order_history(request):
    orders = DigitalProductOrder.objects.filter(user=request.user).select_related('product').order_by('-purchased_at')
    from .models import Booking
    service_bookings = Booking.objects.filter(user=request.user).select_related('service', 'mentor').order_by('-scheduled_time')
    return render(request, 'mentor/user_order_history.html', {
        'orders': orders,
        'service_bookings': service_bookings,
    })

import razorpay
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@login_required
def razorpay_payment(request, booking_id):
    from .models import Booking
    booking = Booking.objects.get(id=booking_id, user=request.user)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(booking.service.price * 100)  # paise
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })
    context = {
        "booking": booking,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "callback_url": reverse("razorpay_payment_callback", args=[booking.id]),
        "description": "Service Payment",
    }
    return render(request, "mentor/razorpay_payment.html", context)

@login_required
def razorpay_payment_digital(request, order_id):
    from .models import DigitalProductOrder
    order = DigitalProductOrder.objects.get(id=order_id, user=request.user)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(order.product.price * 100)
    razorpay_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })
    context = {
        "order": order,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "amount": amount,
        "callback_url": reverse("razorpay_payment_digital_callback", args=[order.id]),
        "description": "Digital Product Payment",
    }
    return render(request, "mentor/razorpay_payment_digital.html", context)

@csrf_exempt
@login_required
def razorpay_payment_callback(request, booking_id):
    if request.method == "POST":
        params = {
            "razorpay_order_id": request.POST.get("razorpay_order_id"),
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_signature": request.POST.get("razorpay_signature"),
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params)
            from .models import Booking
            booking = Booking.objects.get(id=booking_id, user=request.user)
            booking.payment_status = "paid"
            booking.save()
            return redirect("user_order_history")
        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("Payment verification failed", status=400)
    return HttpResponse(status=405)

@csrf_exempt
@login_required
def razorpay_payment_digital_callback(request, order_id):
    if request.method == "POST":
        params = {
            "razorpay_order_id": request.POST.get("razorpay_order_id"),
            "razorpay_payment_id": request.POST.get("razorpay_payment_id"),
            "razorpay_signature": request.POST.get("razorpay_signature"),
        }
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(params)
            from .models import DigitalProductOrder
            order = DigitalProductOrder.objects.get(id=order_id, user=request.user)
            order.is_delivered = True  # Use a real payment status in production
            order.save()
            return redirect("user_order_history")
        except razorpay.errors.SignatureVerificationError:
            return HttpResponse("Payment verification failed", status=400)
    return HttpResponse(status=405)

@login_required
def digital_product_buy(request, product_id):
    product = DigitalProduct.objects.get(id=product_id)
    order, created = DigitalProductOrder.objects.get_or_create(user=request.user, product=product)
    return render(request, 'mentor/digital_product_buy.html', {'product': product, 'order': order, 'created': created})

@login_required
def digital_product_add(request):
    if request.method == 'POST':
        form = DigitalProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.mentor = request.user.mentorprofile
            product.save()
            return redirect('mentor_digital_products')
    else:
        form = DigitalProductForm()
    return render(request, 'mentor/digital_product_form.html', {'form': form})

    
    # Get mentor profile
    mentor = request.user.mentorprofile
    
    # Calculate statistics
    total_sessions = Booking.objects.filter(mentor=mentor).count()
    total_earnings = Booking.objects.filter(mentor=mentor, status='completed').aggregate(
        total_earnings=models.Sum('service__price'))['total_earnings'] or 0
    active_students = Booking.objects.filter(mentor=mentor, status__in=['scheduled', 'in_progress']).distinct('mentee').count()
    pending_bookings = Booking.objects.filter(mentor=mentor, status='pending').count()
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(mentor=mentor).order_by('-created_at')[:5]
    
    # Get upcoming sessions
    upcoming_sessions = Booking.objects.filter(
        mentor=mentor,
        status='scheduled',
        scheduled_time__gte=timezone.now()
    ).order_by('scheduled_time')[:3]
    
    context = {
        'total_sessions': total_sessions,
        'total_earnings': total_earnings,
        'active_students': active_students,
        'pending_bookings': pending_bookings,
        'recent_bookings': recent_bookings,
        'upcoming_sessions': upcoming_sessions,
        'mentor': mentor
    }
    
    return render(request, 'mentor/dashboard.html', context)

@login_required
def service_list(request):
    services = request.user.mentorprofile.services.all()
    return render(request, 'mentor/service_list.html', {'services': services})

@login_required
def service_add(request):
    return render(request, 'mentor/service_form.html')

@login_required
def service_edit(request, pk):
    return render(request, 'mentor/service_form.html')

@login_required
def service_delete(request, pk):
    return render(request, 'mentor/service_confirm_delete.html')

@login_required
def availability_manage(request):
    mentor = request.user.mentorprofile
    if request.method == 'POST':
        form = AvailabilitySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.mentor = mentor
            slot.save()
            form = AvailabilitySlotForm()  # reset form after save
    else:
        form = AvailabilitySlotForm()
    slots = mentor.availability_slots.all().order_by('start_time')
    return render(request, 'mentor/availability.html', {'form': form, 'slots': slots})

@login_required
def mentor_bookings(request):
    mentor = request.user.mentorprofile
    bookings = mentor.bookings.select_related('user', 'service').order_by('-scheduled_time')
    from .models import DigitalProductOrder
    digital_orders = DigitalProductOrder.objects.filter(product__mentor=mentor).select_related('user', 'product').order_by('-purchased_at')
    return render(request, 'mentor/bookings.html', {'bookings': bookings, 'digital_orders': digital_orders})

from django.shortcuts import get_object_or_404

def mentor_profile(request, username):
    mentor = get_object_or_404(MentorProfile, user__username=username, is_mentor=True)
    services = Service.objects.filter(mentor=mentor).prefetch_related('mentor')
    digital_products = DigitalProduct.objects.filter(mentor=mentor).prefetch_related('mentor')
    
    # Convert querysets to lists to ensure we have actual objects
    services = list(services)
    digital_products = list(digital_products)
    
    # Filter out any services that don't have an ID
    services = [s for s in services if s.id and str(s.id).isdigit()]
    
    return render(request, 'mentor/mentor_profile.html', {
        'mentor': mentor,
        'services': services,
        'digital_products': digital_products,
    })

@login_required
def mentor_analytics(request):
    mentor = request.user.mentorprofile
    total_bookings = Booking.objects.filter(mentor=mentor).count()
    total_earnings = sum(booking.service.price for booking in Booking.objects.filter(mentor=mentor))
    
    return render(request, 'mentor/analytics.html', {
        'total_bookings': total_bookings,
        'total_earnings': total_earnings,
    })

def about(request):
    return render(request, 'about.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')
