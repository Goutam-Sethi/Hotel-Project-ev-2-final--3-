
from .models import CarBooking, TaxiCar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect



def ride_book(request):
    return render(request, "taxi_index.html")

@login_required
def confirm_book(request):
    return render(request, "taxi_booking.html")



from django.views.decorators.csrf import csrf_protect
@login_required
@csrf_protect
def book_car_view(request):
    from django.contrib import messages
    from datetime import datetime

    if request.method == "POST":
        pickup_location = request.POST.get("location")
        pickup_date = request.POST.get("pickup_date")
        pickup_time = request.POST.get("pickup_time")
        dropoff_date = request.POST.get("dropoff_date")
        dropoff_time = request.POST.get("dropoff_time")

        if not all([pickup_location, pickup_date, pickup_time, dropoff_date, dropoff_time]):
            messages.error(request, "Please fill all required fields.")
            return render(request, 'taxi_index.html')

        # Here you can add filtering logic based on availability, location, etc.
        # For now, just fetch all cars
        cars = TaxiCar.objects.all()

        return render(request, 'taxi_detail.html', {'cars': cars, 'pickup_location': pickup_location,
                                                    'pickup_date': pickup_date, 'pickup_time': pickup_time,
                                                    'dropoff_date': dropoff_date, 'dropoff_time': dropoff_time})
    else:
        cars = TaxiCar.objects.all()
        return render(request, 'taxi_detail.html', {'cars': cars})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def confirm_booking(request, car_id):
    from datetime import datetime
    from django.contrib import messages

    # Get the Car by ID
    car = get_object_or_404(TaxiCar, id=car_id)

    if request.method == "POST":
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        pickup_location = request.POST.get("pickup_location")
        dropoff_location = request.POST.get("dropoff_location")
        pickup_datetime_str = request.POST.get("pickup_datetime")
        dropoff_datetime_str = request.POST.get("dropoff_datetime")

        # Basic validation
        if not all([username, phone, pickup_location, dropoff_location, pickup_datetime_str, dropoff_datetime_str]):
            messages.error(request, "Please fill all required fields.")
            return redirect('cab_booking')

        # Parse datetime strings into date and time objects
        try:
            pickup_datetime = datetime.strptime(pickup_datetime_str, "%Y-%m-%dT%H:%M")
            dropoff_datetime = datetime.strptime(dropoff_datetime_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            messages.error(request, "Invalid date/time format.")
            return redirect('cab_booking')

        # Create a CarBooking object
        booking = CarBooking.objects.create(
            car_name=car.name,
            car_price=car.rate_per_hour,
            username=username,
            phone=phone,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            pickup_date=pickup_datetime.date(),
            pickup_time=pickup_datetime.time(),
            dropoff_date=dropoff_datetime.date(),
            dropoff_time=dropoff_datetime.time()
        )

        return redirect('manage_bookings')  # Redirect to manage bookings page after success

    # For GET request, render the booking form with the car data
    return render(request, 'taxi_booking.html', {'car': car})

@login_required
def manage_bookings(request):
    # For now, show all bookings; ideally filter by user if linked
    bookings = CarBooking.objects.all().order_by('-booked_at')
    return render(request, 'taxi_manage_booking.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    booking = get_object_or_404(CarBooking, id=booking_id)
    if request.method == "POST":
        booking.delete()
        messages.success(request, "Your booking has been successfully cancelled.")
        return redirect('manage_bookings')
    messages.error(request, "Invalid request method.")
    return redirect('manage_bookings')
