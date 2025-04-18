from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Property
from .models import Booking
from .models import AppUser
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


def home(request):
  
    destinations = [
        {"name": "New Delhi", "img": static("images/humayuns-tomb.jpg")},
        {"name": "Bangalore", "img": static("images/Bengaluru.jpg")},
        {"name": "Pune", "img": static("images/pune.jpg")},
        {"name": "Chennai", "img": static("images/Shimla.jpg")},
        {"name": "Hyderabad", "img": static("images/hyderabad.jpg")},
        {"name": "Mumbai", "img": static("images/mumbai3.jpg")},
    ]


    rooms = [
        {"img": "IMG-20250213-WA0012.jpg", "name": "Treebo Corporate Park", "place": "New Delhi", "price": "₹ 8,594"},
        {"img": "IMG-20250213-WA0007.jpg", "name": "Quality Inn Elite, Amritsar", "place": "Amritsar", "price": "₹ 5,670"},
        {"img": "images.jpg", "name": "Aachman Valley Resort Shimla", "place": "Shimla", "price": "₹ 2,608"},
        {"img": "IMG-20250213-WA0009.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
        {"img": "IMG-20250213-WA0011.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
        {"img": "IMG-20250213-WA0008.jpg", "name": "Hotel Airport Residency", "place": "New Delhi", "price": "₹ 7,260"},
    ]

    return render(request, "index.html", {
        "destinations": destinations,
        "rooms": rooms
    })



@login_required
def list_property(request):
    if not request.user.is_staff:
        messages.error(request,"You're not authorized to access this page !")
        return render(request, 'index.html')
    
    if not request.user.is_authenticated:
        messages.error(request, "You must login as admin first !")
        return render(request, "index.html")

    if request.method == 'POST':
        hotel_name = request.POST.get('property_name')
        location = request.POST.get('property_location')
        image = request.FILES.get('property_image')
        license_number = request.POST.get('license_number')
        rooms = request.POST.get('rooms_available')
        price = request.POST.get('price')
        description = request.POST.get('property_description')

        Property.objects.create(
            hotel_name=hotel_name,
            location=location,
            image=image,
            license_number=license_number,
            rooms_available=rooms,
            price=price,
            description=description
        )
        messages.success(request, "Property listed successfully!")
    
    return render(request, 'listProperty.html')


def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        selected_role = request.POST.get('role') 
        
        user = authenticate(email=email, password=password)
        
        if user:
           
            if selected_role == "admin" and not user.is_staff:
                messages.error(request, "Invalid Admin Credentials.")
                return render(request, 'userlogin.html')
            
            if user.is_staff:
                auth_login(request, user)
                return redirect('owner_dashboard')
            else:
                auth_login(request, user)
                return redirect('home')
        
        else:
            messages.error(request, "Invalid credentials")
            return render(request, 'userlogin.html')
    
    return render(request, "userlogin.html")

@login_required
def owner_dashboard(request):
    if not request.user.is_staff:
        return redirect('home')

 
    properties = Property.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(property__in=properties).select_related('property')

    return render(request, 'owner_dashboard.html', {'bookings': bookings})



def signup(request):
    if request.method=="POST":
        name=request.POST.get('name')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm-password')


        if password!=confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        elif AppUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        elif AppUser.objects.filter(phone=phone).exists():
            messages.error(request,"Phone number already exists")
        else:
            AppUser.objects.create_user(name=name, phone=phone, email=email, password=password)
            messages.success(request, "Account created successfully!")
            return redirect('login')
        
    
    return render(request, "usersignup.html")


@login_required
def cancel_booking_owner(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    
    if booking.property.owner != request.user:
        return redirect('owner_dashboard')  

    booking.delete()
    return redirect('owner_dashboard')

def forgot(request):
    return render(request, "userforgot.html")

def user_logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

def privacy(request):
    return render(request, "privacy.html")

def contact(request):
    return render(request, "contact_us.html")



def about_us(request):
    return render(request, 'about_us.html')


def search_properties(request):
    location_to_search = request.GET.get("location_to_search")
    properties = []

    if location_to_search:
        properties = Property.objects.filter(location__icontains=location_to_search)

    return render(request, 'search_results.html', {'properties': properties})


def available_properties(request):
    properties = Property.objects.all()

    context = {
        'properties': properties
    }

    return render(request, 'hotels.html', context)


from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

@login_required
def book(request, id):
    property_obj = get_object_or_404(Property, id=id)

    if request.method == 'POST':
      
        user_name = request.POST.get('user-name')
        user_email = request.POST.get('user-email')
        user_phone = request.POST.get('user-phone')
        checkin_date = request.POST.get('checkin-date')
        checkout_date = request.POST.get('checkout-date')
        rooms = request.POST.get('rooms')

        if not all([user_name, user_email, user_phone, checkin_date, checkout_date, rooms]):
            messages.error(request, "Please fill all required fields.")
            return redirect('book', id=id)

        try:
        
            checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d')
            checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d')

    
            if checkin_date >= checkout_date:
                messages.error(request, "Check-out date must be after the check-in date.")
                return redirect('book', id=id)

        except ValueError:
            messages.error(request, "Invalid date format. Please use the correct format (YYYY-MM-DD).")
            return redirect('book', id=id)

   
        booking = Booking.objects.create(
            property=property_obj,
            user=request.user,
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            rooms_booked=int(rooms),
            booked_at=timezone.now()
        )

        messages.success(request, "Booking successful!")
        return redirect('booking_confirmation_hotelio', booking_id=booking.id)  


    rooms_range = range(1, min(property_obj.rooms_available, 6) + 1)

    return render(request, 'book_property.html', {
        'property': property_obj,
        'rooms_range': rooms_range
    })


@login_required
def user_bookings(request):

    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    
 
    return render(request, 'bookings.html', {'bookings': bookings})


def cancel_booking_hotel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        booking.delete()
        messages.success(request, "Your booking has been successfully cancelled.")
        return redirect('user_bookings')  

    messages.error(request, "Invalid request method.")
    return redirect('user_bookings')

from django.contrib.auth import logout


@login_required
def delete_profile(request):
    if request.method == 'POST':
        user = request.user
        logout(request)  
        user.delete()    
        messages.success(request, "Your profile has been deleted successfully.")
        return redirect('home')  

    return render(request, 'delete_profile.html')


@login_required
def dashboard(request):
    user = request.user
    context = {
        'user': user,
        'profile': getattr(user, 'profile', None)  
    }
    return render(request, 'dashboard.html', context) 


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.save()
        return redirect('dashboard') 

    return render(request, 'edit_profile.html', {'user': user})


from decimal import Decimal

def booking_confirmation_hotelio(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    total_price = booking.property.price * booking.rooms_booked

    # Get discount code from GET params
    discount_code = request.GET.get('discount_code', '').strip()
    discount = Decimal('0.00')

    if discount_code == 'HOTELIO10':
        discount = Decimal('10.00')  # 10%

    discount_amount = (discount / Decimal('100.00')) * total_price
    final_price = total_price - discount_amount

    context = {
        'booking': booking,
        'total_price': total_price,
        'discount': discount,
        'discount_amount': discount_amount,
        'final_price': final_price,
        'discount_code': discount_code
    }

    return render(request, 'booking_con_hotelio.html', context)