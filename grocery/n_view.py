from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import DeliveryBoy, Booking

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from grocery.models import Booking, DeliveryBoy, Status  # Ensure Status is imported

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from grocery.models import Booking, DeliveryBoy, Status  

def assign_delivery_boy(request, booking_id, booking_obj_id):
    if request.method == "POST":
        delivery_boy_id = request.POST.get("delivery_boy_id")
        
        if delivery_boy_id:
            # Fetch the related objects
            delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)
            booking = get_object_or_404(Booking, booking_id=booking_id, id=booking_obj_id)

            # Get the Status instance
            assigned_status = get_object_or_404(Status, name="Assigned to Delivery Boy")

            # Assign the delivery boy and update status
            booking.delivery_boy = delivery_boy
            booking.status = assigned_status  # Assigning Status instance, not a string
            booking.save()

            messages.success(request, "Delivery boy assigned successfully!")
        else:
            messages.error(request, "Please select a delivery boy!")

    return redirect("admin_viewBooking")


    
    




def admin_cancel_booking(request, booking_id, id):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason")
        booking = get_object_or_404(Booking, booking_id=booking_id, id=id)
        
        booking.status.name = "Cancelled"  # Update status
        booking.cancel_reason = cancel_reason  # Save the cancellation reason
        booking.save()

        return redirect('admin_viewBooking')  # Correct
  # Redirect to the bookings page



def View_feedback(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    feed = Send_Feedback.objects.all()
    d = {'feed': feed}
    return render(request, 'view_feedback.html', d)


def View_prodcut(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    cat = ""
    cat1 = ""
    pro1 = ""
    num1 = 0
    user=""
    profile=""
    cart=""
    pro=""
    num=""
    if not request.user.is_staff:
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        cart = Cart.objects.filter(profile=profile)
        for i in cart:
            num1 += 1

    if pid == 0:
        cat = "All Product"
        pro1 = Product.objects.all()
    else:
        cat1 = Category.objects.get(id=pid)
        pro1 = Product.objects.filter(category=cat1).all()
    cat = Category.objects.all()
    pro = Product.objects.all()
    num = []
    b = 1
    for j in cat:
        a = 1
        for i in pro:
            if j.name == i.category.name:
                if a == 1:
                    num.append(i.id)
                    a = 2
    prod = recommended_product(request)
    d = {'pro': pro, 'cat': cat,'cat1': cat1,'num':num,'pro1':pro1,'num1':num1,'prod':prod}
    return render(request, 'view_product.html',d)

def View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    book = Booking.objects.filter(profile=profile)
    pro = recommended_product(request)
    num1 = 0
    for i in cart:
        num1 += 1
    d = {'book': book, 'num1': num1, 'pro': pro}
    return render(request, 'view_booking.html', d)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Booking, Product

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Booking, Product

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Booking, Product
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from .models import Booking, Product

from django.db import transaction

def delete_booking(request, bid):
    if not request.user.is_authenticated:
        return redirect('login')
    booking = get_object_or_404(Booking, id=bid)
    if booking.status.name != "Delivered":
        with transaction.atomic():
            if booking.product:
                booking.product.stock += booking.quantity
                booking.product.save()
            booking.delete()
        messages.success(request, "Your booking has been canceled, and stock has been restored.")
    else:
        messages.error(request, "You cannot cancel a delivered order.")
    return redirect('view_booking')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Booking, RefundRequest
from .forms import RefundForm

def return_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = RefundForm(request.POST)
        if form.is_valid():
            refund_request = form.save(commit=False)
            refund_request.user = request.user
            refund_request.product = product
            refund_request.status = "Pending"

            # Save refund details from form inputs
            refund_request.account_name = form.cleaned_data["account_name"]
            refund_request.account_number = form.cleaned_data["account_number"]
            refund_request.bank_name = form.cleaned_data["bank_name"]
            refund_request.ifsc_code = form.cleaned_data["ifsc_code"]

            refund_request.save()

            # Update booking status
            Booking.objects.filter(user=request.user, product=product).update(status="Returned")

            messages.success(request, "Your return request has been submitted successfully.")
            return redirect("view_booking")

    else:
        form = RefundForm()

    return render(request, "refund_form.html", {"form": form, "product": product})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ReturnRequest

@login_required
def admin_view_returns(request):
    if not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        new_status = request.POST.get("status")

        return_request = get_object_or_404(ReturnRequest, id=request_id)

        if new_status in ["Pending", "Approved", "Rejected"]:
            return_request.status = new_status
            return_request.save()
            messages.success(request, "Return request status updated successfully.")
        else:
            messages.error(request, "Invalid status selected.")

        return redirect("admin_view_returns")

    return_requests = ReturnRequest.objects.all().order_by("-created_at")
    return render(request, "admin_returns.html", {"return_requests": return_requests})



from django.shortcuts import render

def refund_form(request):
    product_id = request.GET.get("product_id")
    reason = request.GET.get("reason")
    return render(request, 'refund_form.html', {"product_id": product_id, "reason": reason})

from django.shortcuts import render, redirect
from .models import ReturnRequest
from django.contrib.auth.decorators import login_required

@login_required
def submit_return_request(request):
    if request.method == "GET":
        product_id = request.GET.get("product_id")
        reason = request.GET.get("reason")

        # Assume we fetch product details from database
        product_name = "Sample Product"  # Replace with actual lookup

        ReturnRequest.objects.create(
            user=request.user,
            product_name=product_name,
            reason=reason,
        )

        return redirect("view_booking")  # Redirect to booking page





def Add_Categary(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    error = False
    if request.method == "POST":
        n = request.POST['cat']
        Category.objects.create(name=n)
        error = True
    d = {'error': error}
    return render(request, 'add_category.html', d)


def View_Categary(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Category.objects.all()
    d = {'pro': pro}
    return render(request, 'view_category.html', d)












from .models import Send_Feedback


def Feedback(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')
    error = False
    user1 = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user1)
    cart = Cart.objects.filter(profile=profile)
    num1 = 0
    for i in cart:
        num1 += 1
    date1 = date.today()
    user = User.objects.get(id=pid)
    pro = Profile.objects.filter(user=user).first()
    if request.method == "POST":
        d = request.POST['date']
        u = request.POST['uname']
        e = request.POST['email']
        con = request.POST['contact']
        m = request.POST['desc']
        user = User.objects.filter(username=u, email=e).first()
        pro = Profile.objects.filter(user=user, contact=con).first()
        Send_Feedback.objects.create(profile=pro, date=d, message1=m)
        error = True
    d = {'pro': pro, 'date1': date1, 'num1': num1, 'error': error}
    return render(request, 'feedback.html', d)


def Change_Password(request):
    if not request.user.is_authenticated:
        return redirect('login')
    error = ""
    num1 = 0
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    for i in cart:
        num1 += 1
    if request.method == "POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            error = "yes"
        else:
            error = "not"
    d = {'error': error, 'num1': num1}
    return render(request, 'change_password.html', d)


def recommended_product(request):
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    book = Booking.objects.filter(profile=profile).order_by('-id')[:2]
    recommend = []
    for i in book:
        recommend += i.booking_id.split('.')[1:]
    pro1 = Product.objects.filter(id__in=recommend)
    cat = []
    for i in pro1:
        if not i.category.id in cat:
            cat.append(i.category.id)
    pro = Product.objects.filter(category__id__in=cat).order_by('?')
    return pro


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Cart

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Profile, Cart

from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Cart
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user = request.user

    # Ensure the user has a profile
    pro, created = Profile.objects.get_or_create(user=user)

    num1 = 0
    total = 0

    # Fetch all cart items (not linked to Profile)
    cart_items = Cart.objects.all()

    for item in cart_items:
        total += item.product.price
        num1 += 1

    context = {'pro': pro, 'user': user, 'num1': num1, 'total': total}
    return render(request, 'profile.html', context)




from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Cart

def Edit_profile(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')

    error = False
    user = User.objects.get(id=request.user.id)
    pro = Profile.objects.get(user=user)

    # Initialize cart total and item count
    total = 0
    num1 = 0

    # Get the cart items related to the profile
    cart_items = Cart.objects.filter(profile=pro)  # ✅ Fetch multiple cart items

    for item in cart_items:  # ✅ Iterate over multiple items
        total += item.product.price * item.quantity  # Multiply by quantity
        num1 += 1

    if request.method == 'POST':
        # Retrieve and validate form data
        f = request.POST.get('fname')
        l = request.POST.get('lname')
        u = request.POST.get('uname')
        c = request.POST.get('city')
        ad = request.POST.get('add')
        e = request.POST.get('email')
        con = request.POST.get('contact')
        d = request.POST.get('dob')  # Use 'dob' instead of 'date'

        # Handle image upload
        if 'img' in request.FILES:
            pro.image = request.FILES['img']
        
        # Update profile fields
        pro.user.username = u
        pro.user.first_name = f
        pro.user.last_name = l
        pro.user.email = e
        pro.contact = con
        pro.city = c
        pro.address = ad
        
        # Update date of birth if provided
        if d:
            pro.dob = d

        # Save the profile and user data
        pro.user.save()  # Save the user changes first
        pro.save()  # Then save the profile changes
        
        error = True  # Set error to True to indicate successful update

    # Prepare context for the template
    context = {
        'error': error,
        'pro': pro,
        'num1': num1,
        'total': total,
    }

    return render(request, 'edit_profile.html', context)



from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Booking, Profile, Product

from django.db.models import Count
from django.db.models.functions import TruncMonth, TruncDay

import json
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Count
from .models import Booking, Profile, Product

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import pandas as pd
import json
from .models import Booking, Profile, Product

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import pandas as pd
import json
from .models import Booking, Profile, Product
import json
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from grocery.models import Booking, Profile, Product

@login_required
def Admin_Home(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    # Fetch all data
    book = Booking.objects.all()
    customer = Profile.objects.all()
    pro = Product.objects.all()

    # Count totals
    total_book = book.count()
    total_customer = customer.count()
    total_pro = pro.count()

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(book.values('book_date', 'total')))  # 'total' instead of 'total_price'

    # Check if data exists
    if not df.empty:
        df['book_date'] = pd.to_datetime(df['book_date'])

        # Monthly Sales Data
        df['month'] = df['book_date'].dt.strftime('%Y-%m')
        monthly_sales = df.groupby('month').size().reset_index(name='total_sales')

        # Monthly Profit Data (Assuming profit is calculated from total sales)
        df['profit'] = df['total'] * 0.2  # Assuming 20% profit margin
        monthly_profits = df.groupby('month')['profit'].sum().reset_index(name='total_profit')

        # Daily Sales Data
        df['day'] = df['book_date'].dt.strftime('%Y-%m-%d')
        daily_sales = df.groupby('day').size().reset_index(name='total_sales')

        # **New Daily Profit Data**
        daily_profits = df.groupby('day')['profit'].sum().reset_index(name='total_profit')

        # Convert to dictionary format
        monthly_sales = monthly_sales.to_dict(orient='records')
        daily_sales = daily_sales.to_dict(orient='records')
        monthly_profits = monthly_profits.to_dict(orient='records')
        daily_profits = daily_profits.to_dict(orient='records')  # Added daily profits

    else:
        monthly_sales = []
        daily_sales = []
        monthly_profits = []
        daily_profits = []  # Added empty list for daily profits

    context = {
        'total_pro': total_pro,
        'total_customer': total_customer,
        'total_book': total_book,
        'monthly_sales': json.dumps(monthly_sales),
        'daily_sales': json.dumps(daily_sales),
        'monthly_profits': json.dumps(monthly_profits),
        'daily_profits': json.dumps(daily_profits),  # Sending daily profits to frontend
    }

    return render(request, 'admin_home.html', context)





def delete_category(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    cat = Category.objects.get(id=pid)
    cat.delete()
    return redirect('view_categary')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category

def edit_product(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    # Get all categories
    cat = Category.objects.all()

    # Retrieve the product or raise 404 if it doesn't exist
    product = get_object_or_404(Product, id=pid)

    error = ""
    if request.method == "POST":
        # Retrieve form data
        c = request.POST.get('cat')  # Get the selected category ID
        p = request.POST.get('pname')
        pr = request.POST.get('price')
        stock = request.POST.get('stock')  # Get stock quantity
        d = request.POST.get('desc')
        date_added = request.POST.get('date_added')  # Get the product date
        expiry_date = request.POST.get('expiry_date')  # Get the expiry date

        # Attempt to get the category by ID
        try:
            ct = Category.objects.get(id=c)
            product.category = ct
        except Category.DoesNotExist:
            error = "yes"  # If the category does not exist, set error
            return render(request, 'edit_product.html', {'cat': cat, 'error': error, 'product': product})

        # Update product details
        product.name = p
        product.price = pr
        product.stock = stock  # Update stock quantity
        product.desc = d
        product.date = date_added  # Update the product date
        product.expiry_date = expiry_date  # Update the expiry date

        # Handle image upload if present
        if 'img' in request.FILES and request.FILES['img']:
            product.image = request.FILES['img']

        # Try to save the product and handle potential errors
        try:
            product.save()
            error = "no"  # Successful update
        except Exception as e:
            error = "yes"  # If saving fails, set error
            print(f"Error saving product: {e}")  # Log the exception for debugging

    # Render the edit product template with the context
    context = {
        'cat': cat,
        'error': error,
        'product': product
    }
    return render(request, 'edit_product.html', context)



def edit_category(request,pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    category = Category.objects.get(id=pid)
    error=""
    if request.method=="POST":
        c = request.POST['cat']
        category.name = c
        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    d = {'error':error,'category':category}
    return render(request, 'edit_category.html', d)

def search_booking(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    terror = ""
    book=""
    sd=""
    if request.method == "POST":
        sd = request.POST['searchdata']
        try:
            book = Booking.objects.get(booking_id=sd)
            terror = "found"
        except:
            terror="notfound"
    d = {'book':book,'terror':terror,'sd':sd}
    return render(request,'search_booking.html',d)


def bookingbetweendate_reportdetails(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    return render(request, 'bookingbetweendate_reportdetails.html')



def bookingbetweendate_report(request):
    if not request.user.is_authenticated:
        return redirect('loginadmin')
    if request.method == "POST":
        fd = request.POST['fromdate']
        td = request.POST['todate']
        booking = Booking.objects.filter(book_date__range=[fd,td])
        d = {'booking':booking,'fd':fd,'td':td}
        return render(request, 'bookingbetweendate_reportdetails.html', d)
    return render(request, 'bookingbetweendate_report.html')

from django.shortcuts import render, get_object_or_404
from .models import Product  # Assuming your product model is named `Product`

def product_details(request, product_id):
    # Fetch the product details using the product ID
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {'product': product})



# from django.shortcuts import render
# from .models import Product, Category

# def search_product(request):
#     query = request.GET.get('q', '')
#     products = Product.objects.all()

#     if query:
#         products = products.filter(
#             models.Q(name__icontains=query) |
#             models.Q(price__icontains=query) |
#             models.Q(category__name__icontains=query)
#         )

#     return render(request, 'view_product.html', {'products': products, 'query': query})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Appointment, Chat
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    return render(request, 'appointments.html', {'doctor': doctor})

# @login_required
# def doctor_appointments(request):
#     doctor = get_object_or_404(Doctor, user=request.user)
#     appointments = Appointment.objects.filter(doctor=doctor)
#     return render(request, 'appointments.html', {'appointments': appointments})


@login_required
def user_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)
    return render(request, 'appointments.html', {'appointments': appointments})

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
# from datetime import datetime
from .models import Doctor, Appointment, Notification

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Doctor, Appointment, Notification

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Doctor, Appointment, Notification

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Doctor, Appointment, Notification

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Doctor, Appointment, Notification
from datetime import datetime

@login_required
def book_appointment(request):
    error_message = None  # Initialize an error message variable
    booked_slots = []  # List to hold booked time slots
    appointments = Appointment.objects.filter(user=request.user)  # Get user's appointments

    if request.method == "POST":
        doctor_id = request.POST.get('doctor')
        date = request.POST.get('date')
        time = request.POST.get('time')  # This is coming in "10:00 AM" format
        reason = request.POST.get('reason')

        # Convert time from 12-hour format to 24-hour format
        try:
            time_24 = datetime.strptime(time, '%I:%M %p').strftime('%H:%M')
        except ValueError:
            error_message = 'Invalid time format. Please use HH:MM AM/PM format.'
            return render(request, 'book_appointment.html', {
                'doctors': Doctor.objects.all(),
                'error_message': error_message,
                'appointments': appointments
            })

        # Check if the appointment already exists
        if Appointment.objects.filter(doctor_id=doctor_id, date=date, time=time_24).exists():
            error_message = 'This time slot is already booked!'
            return render(request, 'book_appointment.html', {
                'doctors': Doctor.objects.all(),
                'error_message': error_message,
                'appointments': appointments
            })

        # Create the appointment with the converted time
        appointment = Appointment.objects.create(
            doctor_id=doctor_id,
            user=request.user,
            date=date,
            time=time_24,  # Use the 24-hour format
            reason=reason,
            status='Pending'
        )

        # Create a notification with the user assigned
        Notification.objects.create(
            user=request.user,  # Assign the user to the notification
            message=f"New appointment booked with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} on {date} at {time}."
        )

        return redirect('doctor_notifications')  # Redirect to notifications or another page

    doctors = Doctor.objects.all()
    # Get all booked appointments for the selected date and doctor
    if request.GET.get('doctor') and request.GET.get('date'):
        doctor_id = request.GET.get('doctor')
        date = request.GET.get('date')
        booked_appointments = Appointment.objects.filter(doctor_id=doctor_id, date=date)
        booked_slots = [appointment.time.strftime('%I:%M %p') for appointment in booked_appointments]

    return render(request, 'book_appointment.html', {
        'doctors': doctors,
        'error_message': error_message,
        'booked_slots': booked_slots,
        'appointments': appointments  # Pass user's appointments to the template
    })

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Appointment, Doctor

@login_required
def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date = request.GET.get('date')

    # Fetch booked time slots
    doctor = get_object_or_404(Doctor, id=doctor_id)
    booked_slots = Appointment.objects.filter(doctor=doctor, date=date).values_list('time', flat=True)

    # Define available slots
    available_slots = ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]
    
    # Remove booked slots
    free_slots = [slot for slot in available_slots if slot not in booked_slots]

    return JsonResponse({"available_slots": free_slots})





# views.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Appointment  # Adjust the import based on your models

@login_required
def your_appointments(request):
    appointments = Appointment.objects.filter(user=request.user)  # Adjust based on your model
    appointment_list = []

    for appointment in appointments:
        appointment_list.append({
            'doctor': f"Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name}",
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M'),  # Adjust based on your time format
            'reason': appointment.reason
        })

    return JsonResponse({'appointments': appointment_list})


@login_required
def doctor_appointments(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor)
    
    pending_appointments = appointments.filter(status="Pending").count()
    total_appointments = appointments.count()

    return render(
        request,
        'appointments.html',
        {
            'appointments': appointments,
            'pending_appointments': pending_appointments,
            'total_appointments': total_appointments,
            'doctor': doctor,
        },
    )


@login_required
def get_available_slots(request):
    doctor_id = request.GET.get('doctor_id')
    date = request.GET.get('date')
    
    doctor = get_object_or_404(Doctor, id=doctor_id)
    booked_slots = Appointment.objects.filter(doctor=doctor, date=date).values_list('time', flat=True)

    available_slots = ["10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"]
    free_slots = [slot for slot in available_slots if slot not in booked_slots]

    return JsonResponse({"available_slots": free_slots})






from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template.loader import get_template
from xhtml2pdf import pisa
import traceback
from datetime import datetime
from .models import ProductRequest, SupplierProfile


from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import ProductRequest, SupplierProfile
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import ProductRequest, Category, SupplierProfile, Status

from django.http import HttpResponse
from django.utils.timezone import now
from .models import ProductRequest, Category, SupplierProfile, Status
from django.contrib.auth.models import User
def send_product_request(request):
    if request.method == "POST":
        product_name = request.POST.get('product_name', '').strip()
        category_id = request.POST.get('category', '').strip()
        quantity = request.POST.get('quantity', '').strip()
        supplier_id = request.POST.get('supplier', '').strip()

        # Debug: Print received values
        print(f"Product Name: {product_name}, Category: {category_id}, Quantity: {quantity}, Supplier: {supplier_id}")

        if not (product_name and category_id and quantity and supplier_id):
            return HttpResponse("All fields are required.", status=400)

        category_instance = get_object_or_404(Category, id=category_id)
        supplier = get_object_or_404(SupplierProfile, id=supplier_id)
        admin_user = request.user

        ProductRequest.objects.create(
            product_name=product_name,
            category=category_instance,
            quantity=int(quantity),
            supplier=supplier,
            admin_user=admin_user,
            status='Pending',
            requested_at=now()
        )

        return redirect('send_product_request')

    suppliers = SupplierProfile.objects.all()
    categories = Category.objects.all()
    requests = ProductRequest.objects.filter(admin_user=request.user).order_by('-requested_at')

    return render(
        request, 
        'admin_product_request.html', 
        {'suppliers': suppliers, 'categories': categories, 'requests': requests}
    )


from django.http import JsonResponse
from .models import ProductRequest

def delete_product_request(request, request_id):
    if request.method == "POST":
        try:
            product_request = ProductRequest.objects.get(id=request_id)
            product_request.delete()
            return JsonResponse({"success": True})
        except ProductRequest.DoesNotExist:
            return JsonResponse({"success": False, "error": "Product request not found."})
    return JsonResponse({"success": False, "error": "Invalid request."})



@login_required
def supplier_product_requests(request):
    if hasattr(request.user, 'supplierprofile'):
        product_requests = ProductRequest.objects.filter(supplier=request.user.supplierprofile)
        return render(request, 'supplier_product_requests.html', {'product_requests': product_requests})
    return redirect('home')


def download_requests_pdf(request, date):
    try:
        # Ensure the user is authenticated and has a SupplierProfile
        if not hasattr(request.user, 'supplierprofile'):
            return HttpResponse("Unauthorized", status=401)

        # Get the supplier profile
        supplier = request.user.supplierprofile

        # Parse the date and filter product requests for the specific supplier
        date_object = datetime.strptime(date, '%Y-%m-%d').date()
        product_requests = ProductRequest.objects.filter(
            requested_at__date=date_object,
            supplier=supplier
        )

        # Check if there are no requests for the supplier on that date
        if not product_requests.exists():
            return HttpResponse("No product requests found for this supplier on the specified date.", status=404)

        # Render the PDF template
        template = get_template("supplier_requests_pdf.html")
        html = template.render({"product_requests": product_requests})

        # Create the PDF response
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="product_requests_{date}.pdf"'

        # Generate the PDF
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse("Error generating PDF", content_type="text/plain")

        return response

    except Exception as e:
        return HttpResponse(f"An error occurred:\n{traceback.format_exc()}", content_type="text/plain")


from collections import defaultdict
from datetime import datetime
from django.shortcuts import render
from .models import ProductRequest

def all_requests_view(request):
    if hasattr(request.user, 'supplierprofile'):
        # Filter requests by the logged-in supplier
        product_requests = ProductRequest.objects.filter(supplier=request.user.supplierprofile).order_by('-requested_at')

        # Group requests by date
        grouped_requests = defaultdict(list)
        for req in product_requests:
            grouped_requests[req.requested_at.date()].append(req)

        return render(request, 'all_requests.html', {'grouped_requests': dict(grouped_requests)})
    
    return redirect('home')  # Redirect if the user is not a supplier


def update_request_status(request, request_id):
    if request.method == "POST":
        product_request = get_object_or_404(ProductRequest, id=request_id)
        new_status = request.POST.get("status")

        if new_status:
            product_request.status = new_status
            product_request.save()

        return redirect('all_requests')

    return HttpResponse("Invalid Request", status=400)


from django.shortcuts import get_object_or_404
from .models import ProductRequest, Category

from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
from .models import ProductRequest, Category

from django.shortcuts import get_object_or_404, redirect
from django.db import IntegrityError
from grocery.models import ProductRequest, Category

from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from .models import ProductRequest, Category, SupplierProfile

from django.shortcuts import render, redirect
from django.db.utils import IntegrityError
from .models import ProductRequest, Category, SupplierProfile
from django.contrib.auth.models import User

from django.shortcuts import redirect
from django.db.utils import IntegrityError
from .models import ProductRequest, Category, SupplierProfile
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.db import IntegrityError

def submit_all_requests(request):
    if request.method == "POST":
        product_names = request.POST.getlist("product_name[]")
        categories = request.POST.getlist("category[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price_per_product[]")
        statuses = request.POST.getlist("status[]")
        suppliers = request.POST.getlist("supplier[]")
        admin_user = request.user  

        added_requests = set()  # Set to track unique records for insertion
        updated_requests = set()  # Track requests that should be retained

        for i in range(len(product_names)):
            product_name = product_names[i].strip()
            category_name = categories[i].strip()
            quantity = quantities[i]
            price = prices[i]
            status = statuses[i]
            supplier_name = suppliers[i].strip()

            if not product_name or not supplier_name:
                continue  

            category_instance, _ = Category.objects.get_or_create(name=category_name)
            supplier_instance, _ = SupplierProfile.objects.get_or_create(company_name=supplier_name)

            try:
                quantity = int(quantity)
                price = float(price)
            except ValueError:
                continue  

            unique_key = (supplier_instance.id, product_name, category_instance.id, quantity, price, status)

            if unique_key in added_requests:
                continue  

            existing_request = ProductRequest.objects.filter(
                supplier=supplier_instance,
                product_name=product_name,
                category=category_instance
            ).first()

            if existing_request:
                # Update existing request instead of inserting duplicate
                existing_request.quantity = quantity
                existing_request.price_per_product = price
                existing_request.status = status
                existing_request.save()
                updated_requests.add(existing_request.id)
            else:
                # Insert only if the record is not already present
                try:
                    new_request = ProductRequest.objects.create(
                        supplier=supplier_instance,
                        product_name=product_name,
                        category=category_instance,
                        quantity=quantity,
                        price_per_product=price,
                        status=status,
                        admin_user=admin_user
                    )
                    updated_requests.add(new_request.id)
                except IntegrityError:
                    continue  

            added_requests.add(unique_key)  

        # Remove old requests that were not updated
        ProductRequest.objects.exclude(id__in=updated_requests).delete()

    return redirect("all_requests")






from django.shortcuts import render, get_object_or_404, redirect
from .models import ProductRequest

from django.shortcuts import render, get_object_or_404, redirect
from .models import ProductRequest

from django.shortcuts import render, get_object_or_404, redirect
from .models import ProductRequest

from django.shortcuts import render, get_object_or_404, redirect
from .models import ProductRequest

from django.db.models import F, ExpressionWrapper, FloatField

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, ExpressionWrapper, FloatField
from .models import ProductRequest, Product

def supply_details(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("product_name_"):
                request_id = key.split("_")[-1]
                
                if request_id.isdigit():
                    product_request = get_object_or_404(ProductRequest, id=request_id)

                    # Update fields
                    product_request.product_name = request.POST.get(f"product_name_{request_id}", product_request.product_name)
                    product_request.category = request.POST.get(f"category_{request_id}", product_request.category)
                    product_request.quantity = request.POST.get(f"quantity_{request_id}", product_request.quantity)
                    product_request.status = request.POST.get(f"status_{request_id}", product_request.status)
                    product_request.remarks = request.POST.get(f"remarks_{request_id}", product_request.remarks)

                    product_request.save()

        return redirect('supply_details')

    # Retrieve and calculate total price
    supplies = ProductRequest.objects.annotate(
        total_price=ExpressionWrapper(F('quantity') * F('price_per_product'), output_field=FloatField())
    ).order_by('-requested_at')

    # Filter completed products to send to the Add Product page
    completed_products = ProductRequest.objects.filter(status="Completed")

    return render(request, 'supply_details.html', {
        "supplies": supplies,
        "completed_products": completed_products
    })




from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import ProductRequest, SupplierProfile
from django.template.loader import get_template
# import datetime

# import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa
from grocery.models import ProductRequest, SupplierProfile

import os
# import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from django.conf import settings
from .models import SupplierProfile, ProductRequest  # Import your models

import os
import datetime as dt
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import SupplierProfile, ProductRequest

def download_invoice(request, supplier_id):
    supplier = get_object_or_404(SupplierProfile, id=supplier_id)
    supplies = ProductRequest.objects.filter(supplier=supplier, status="Completed")

    # Calculate total amount
    total_amount = sum(supply.quantity * supply.price_per_product for supply in supplies)

    # Get the absolute file path of the QR code
    qr_code_relative_path = "static/images/dummy_qr.png"
    qr_code_absolute_path = os.path.join(settings.BASE_DIR, qr_code_relative_path)

    # Debugging: Ensure the file path is correct
    if not os.path.exists(qr_code_absolute_path):
        print("QR Code image not found at:", qr_code_absolute_path)

    # Use STATIC_URL instead of absolute path in the template
    qr_code_url = f"{request.build_absolute_uri(settings.STATIC_URL)}images/dummy_qr.png"

    # Define context for template
    context = {
        "supplier": supplier,
        "supplies": supplies,
        "total_amount": total_amount,  
        "date": dt.date.today(),
        "qr_code_url": qr_code_url,  # Pass URL instead of file path
    }

    # Load template
    template = get_template("supplier_invoice.html")
    html = template.render(context)

    # Create a response object for PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{supplier.company_name}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=400)
    
    return response



from django.shortcuts import render
from .models import Blog  # Import Blog model

def blog(request):
    # Fetch all blogs (Admin + Doctor)
    blogs = Blog.objects.all().order_by('-created_at')  # Latest first
    return render(request, 'blog.html', {'blogs': blogs})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Blog

@login_required
def add_blog(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    error = False
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')  # Optional image
        blog = Blog(title=title, content=content, author=request.user, image=image)
        blog.save()
        error = True

    blogs = Blog.objects.all().order_by('-created_at')  # Fetch all blogs

    context = {'error': error, 'blogs': blogs}
    return render(request, 'add_blog.html', context)

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        blog.title = request.POST['title']
        blog.content = request.POST['content']
        if 'image' in request.FILES:
            blog.image = request.FILES['image']
        blog.save()
        return redirect('add_blog')

    return render(request, 'edit_blog.html', {'blog': blog})

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)
    blog.delete()
    return redirect('add_blog')
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Doctor, Appointment, AvailableTimeSlot

@login_required
def add_available_time_slot(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        doctor = get_object_or_404(Doctor, user=request.user)

        # Create a new AvailableTimeSlot
        AvailableTimeSlot.objects.create(doctor=doctor, date=date, time=time)

        return redirect('doctor_appointments')  # Redirect back to the appointments page

    return render(request, 'appointments.html', {
        'doctor': get_object_or_404(Doctor, user=request.user),
        'pending_appointments': Appointment.objects.filter(doctor=request.user.doctor, status='Pending').count(),
        'total_appointments': Appointment.objects.filter(doctor=request.user.doctor).count(),
    })


@login_required
def update_appointment_status(request, appointment_id):
    if request.method == 'POST':
        new_status = request.POST['status']
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Update the appointment status
        appointment.status = new_status
        appointment.save()

        # Optionally create a notification for the user about the status update
        notification_message = f"Your appointment with Dr. {appointment.doctor.user.first_name} {appointment.doctor.user.last_name} has been updated to {new_status}."
        Notification.objects.create(user=appointment.user, message=notification_message)

        messages.success(request, 'Appointment status updated successfully!')
        return redirect('your_appointments')  # Redirect to the appointment history page

@login_required
def your_appointments(request):
    # Fetch user appointments
    appointments = Appointment.objects.filter(user=request.user)
    context = {
        'appointments': appointments,
    }
    return render(request, 'your_appointments.html', context)
















from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def appointment_history(request):
    # Fetch the appointment history for the logged-in user
    if request.user.is_staff:  # For doctors
        appointments = Appointment.objects.filter(doctor=request.user.doctor)
    else:  # For regular users
        appointments = Appointment.objects.filter(user=request.user)

    context = {
        'appointments': appointments,
    }
    return render(request, 'appointment_history.html', context)




@login_required
def appointment_chat(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    chats = Chat.objects.filter(appointment=appointment)

    if request.method == 'POST':
        message = request.POST['message']
        Chat.objects.create(appointment=appointment, sender=request.user, message=message)
        return redirect('appointment_chat', appointment_id=appointment_id)

    return render(request, 'chat.html', {'appointment': appointment, 'chats': chats})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def doctor_profile(request):
    # Add logic for the profile page
    return render(request, 'doctor_profile.html')




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Appointment

@login_required
def all_appointments(request):
    if request.user.is_staff:  # For doctors
        appointments = Appointment.objects.filter(doctor=request.user.doctor)
    else:  # For regular users
        appointments = Appointment.objects.filter(user=request.user)

    return render(request, 'all_appointments.html', {'appointments': appointments})




from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Doctor

# Doctor Registration
def doctor_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Doctor.objects.create(user=user)
            return redirect('doctor_login')
    else:
        form = UserCreationForm()
    return render(request, 'doctor_register.html', {'form': form})

# Doctor Login
def doctor_login(request):
    # Use Django's built-in login view for simplicity.
    return render(request, 'doctor_login.html')





@login_required
def doctor_profile(request):
    doctor = request.user.doctor
    if request.method == 'POST':
        doctor.specialization = request.POST.get('specialization')
        doctor.availability = request.POST.get('availability')
        doctor.fee = request.POST.get('fee')
        doctor.save()
        return redirect('doctor_dashboard')
    return render(request, 'doctor_profile.html', {'doctor': doctor})



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Appointment

def doctor_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        specialization = request.POST['specialization']
        image = request.FILES.get('image')  # Handle the uploaded file

        if password != confirm_password:
            return render(request, 'doctor_register.html', {'error': 'Passwords do not match.'})

        try:
            # Create a new user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True  # Mark as staff to access doctor features
            )
            # Create a doctor profile
            Doctor.objects.create(user=user, specialization=specialization, image=image)
            return redirect('doctor_login')
        except Exception as e:
            return render(request, 'doctor_register.html', {'error': str(e)})

    return render(request, 'doctor_register.html')

# Doctor Login View
def doctor_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and hasattr(user, 'doctor'):  # Ensure user is associated with a Doctor profile
            login(request, user)
            return redirect('doctor_dashboard')  # Redirect to the dashboard
        else:
            return render(request, 'doctor_login.html', {'error': 'Invalid credentials or access restricted.'})

    return render(request, 'doctor_login.html')


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def doctor_dashboard(request):
    doctor = request.user.doctor  # Access the related Doctor model

    # Mock or real data for appointments
    appointments = [
        {'status': 'pending'},  # Example appointment status
        {'status': 'completed'},
        {'status': 'pending'},
    ]
    pending_appointments = sum(1 for appt in appointments if appt['status'] == 'pending')
    total_appointments = len(appointments)

    context = {
        'doctor': doctor,
        'pending_appointments': pending_appointments,
        'total_appointments': total_appointments,
    }
    return render(request, 'doctor_dashboard.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification, Appointment

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Appointment, Notification

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import Appointment, Notification, Doctor
from django.core.exceptions import ValidationError

@login_required
def doctor_notifications(request):
    try:
        doctor = request.user.doctor  # Get the logged-in doctor
    except Doctor.DoesNotExist:
        messages.error(request, "No Doctor profile found for your account.")
        return redirect('book_appointment')  # Redirect to a suitable page

    # Fetch notifications for the logged-in doctor
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Fetch appointments assigned to the doctor
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-date', '-time')

    if request.method == "POST":
        appointment_id = request.POST.get('appointment_id')
        status = request.POST.get('status')

        try:
            appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

            # Only update the status without triggering the full save() validation
            Appointment.objects.filter(id=appointment.id).update(status=status)

            # Create a notification for the patient
            Notification.objects.create(
                user=appointment.patient.user,
                message=f"Your appointment status with Dr. {doctor.user.first_name} {doctor.user.last_name} has been updated to {status} on {appointment.date} at {appointment.time}."
            )

            messages.success(request, 'Appointment status updated successfully!')
            return redirect('doctor_notifications')

        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, "An error occurred while updating the appointment.")

    return render(request, 'doctor_notifications.html', {'doctor': doctor, 'notifications': notifications, 'appointments': appointments})



from datetime import date






from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def doctor_profile(request):
    doctor = getattr(request.user, 'doctor', None)  # Avoids error if doctor doesn't exist
    return render(request, 'doctor_profile.html', {'doctor': doctor})

import logging
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Appointment, Chat

logger = logging.getLogger(__name__)

@login_required
def chat_view(request, appointment_id):
    logger.info(f"Fetching chat for appointment ID: {appointment_id}")

    appointment = get_object_or_404(Appointment, id=appointment_id)
    messages = Chat.objects.filter(appointment=appointment).order_by('timestamp')

    template = 'user_chat.html' if request.user == appointment.user else 'doctor_chat.html'
    
    return render(request, template, {
        'appointment': appointment,
        'messages': messages,
        'user': request.user,
    })

@login_required
def send_message(request, appointment_id):
    if request.method == "POST":
        message_text = request.POST.get("message", "")
        reply_to_id = request.POST.get("reply_to", None)
        file = request.FILES.get("file", None)
        appointment = get_object_or_404(Appointment, id=appointment_id)

        logger.info(f"Reply to ID: {reply_to_id}")  # Debugging

        reply_to = None
        if reply_to_id:
            try:
                reply_to = Chat.objects.get(id=reply_to_id)
            except Chat.DoesNotExist:
                logger.error(f"Message with ID {reply_to_id} not found.")
                return redirect("chat", appointment_id=appointment.id)

        Chat.objects.create(
            sender=request.user,
            appointment=appointment,
            message=message_text,
            file=file,
            reply_to=reply_to
        )
        return redirect("chat", appointment_id=appointment.id)

    return redirect("chat", appointment_id=appointment_id)

@login_required
def fetch_messages(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    messages = Chat.objects.filter(appointment=appointment).order_by("timestamp")
    message_list = [
        {"sender": msg.sender.username, "message": msg.message, "file": msg.file.url if msg.file else None} 
        for msg in messages
    ]
    return JsonResponse({"messages": message_list})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def supplier_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('supplier_dashboard')  # Redirect to supplier dashboard
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'supplier_login.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import SupplierProfile

def supplier_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        company_name = request.POST['company_name']

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, 'supplier_register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, 'supplier_register.html')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        
        # Create Supplier Profile
        SupplierProfile.objects.create(user=user, company_name=company_name)

        messages.success(request, "Registration successful! You can now log in.")
        return redirect('supplier_login')

    return render(request, 'supplier_register.html')


def supplier_dashboard(request):
    return render(request, 'supplier_dashboard.html')


def supplier_logout(request):
    logout(request)
    return redirect('home') 


from django.shortcuts import render, redirect
from .models import Blog  # Import Blog model
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Blog

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog

@login_required
def doctor_add_blog(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')

        # Create a new blog post by the logged-in doctor
        Blog.objects.create(title=title, content=content, image=image, author=request.user)

        return redirect('doctor_add_blog')

    # Fetch all blogs (Admin + Doctor)
    blogs = Blog.objects.all().order_by('-created_at')  # Latest first
    return render(request, 'doctor_add_blog.html', {'blogs': blogs})

@login_required
def doctor_edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    # Ensure that only the author can edit
    if blog.author != request.user:
        return redirect('doctor_add_blog')

    if request.method == "POST":
        blog.title = request.POST['title']
        blog.content = request.POST['content']
        if 'image' in request.FILES:
            blog.image = request.FILES['image']
        blog.save()
        return redirect('doctor_add_blog')

    return render(request, 'edit_blog.html', {'blog': blog})


@login_required
def doctor_delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)  # Ensure only the owner can delete
    blog.delete()
    return redirect('doctor_add_blog')



from django.shortcuts import render, get_object_or_404
from .models import Blog

def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    return render(request, 'blog_detail.html', {'blog': blog})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DeliveryBoy, Booking, Notification

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DeliveryBoy, Booking, Notification

from django.shortcuts import render, redirect
from .models import Booking, DeliveryBoy

def delivery_boy_dashboard(request):
    # Check if the delivery boy is logged in
    delivery_boy_id = request.session.get('delivery_boy_id')
    if not delivery_boy_id:
        return redirect('delivery_boy_login')

    # Get the logged-in delivery boy
    delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)

    # Retrieve bookings assigned to this delivery boy
    bookings = Booking.objects.filter(delivery_boy=delivery_boy).select_related('status')

    context = {
        'delivery_boy': delivery_boy,
        'bookings': bookings
    }
    return render(request, 'delivery_boy_dashboard.html', context)



from django.shortcuts import render, redirect
from .models import DeliveryBoy, Booking

from django.shortcuts import render, redirect
from .models import DeliveryBoy, Booking

def delivery_boy_pending(request):
    # Check if the delivery boy is logged in
    delivery_boy_id = request.session.get('delivery_boy_id')
    if not delivery_boy_id:
        return redirect('delivery_boy_login')

    # Get the logged-in delivery boy
    try:
        delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)
    except DeliveryBoy.DoesNotExist:
        return redirect('delivery_boy_login')

    # Retrieve bookings assigned to this delivery boy that are still pending or "Out for Delivery"
    pending_bookings = Booking.objects.filter(delivery_boy=delivery_boy).exclude(status__name="Delivered")

    context = {
        'delivery_boy': delivery_boy,
        'bookings': pending_bookings
    }
    return render(request, 'delivery_boy_pending.html', context)



from django.shortcuts import render, redirect
from .models import DeliveryBoy, Booking

def delivery_history(request):
    # Check if the delivery boy is logged in
    delivery_boy_id = request.session.get('delivery_boy_id')
    if not delivery_boy_id:
        return redirect('delivery_boy_login')

    # Get the logged-in delivery boy
    delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)

    # Retrieve all successfully delivered bookings assigned to this delivery boy
    delivered_bookings = Booking.objects.filter(delivery_boy=delivery_boy, status__name="Delivered")

    context = {
        'delivery_boy': delivery_boy,
        'bookings': delivered_bookings
    }
    return render(request, 'delivery_history.html', context)


from django.shortcuts import render, redirect
from .models import DeliveryBoy

def delivery_boy_profile(request):
    # Check if the delivery boy is logged in
    delivery_boy_id = request.session.get('delivery_boy_id')
    if not delivery_boy_id:
        return redirect('delivery_boy_login')

    # Get the logged-in delivery boy
    delivery_boy = DeliveryBoy.objects.get(id=delivery_boy_id)

    context = {
        'delivery_boy': delivery_boy
    }
    return render(request, 'delivery_boy_profile.html', context)




def delivery_boy_logout(request):
    logout(request)
    request.session.flush()  # Clear session
    return redirect('delivery_boy_login')




# def deliveryboy_profile(request):
#     return render(request, 'deliveryboy_profile.html')

from django.contrib.auth.decorators import login_required

@login_required
def deliveryboy_orders(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Assuming the DeliveryBoy model is linked to the User model
    delivery_boy = request.user.deliveryboy  # Fetch the logged-in delivery boy

    # Fetch bookings assigned to the current delivery boy
    bookings = Booking.objects.filter(delivery_boy=delivery_boy)

    return render(request, 'deliveryboy_orders.html', {'bookings': bookings})


def deliveryboy_feedback(request):
    return render(request, 'deliveryboy_feedback.html')

def deliveryboy_logout(request):
    logout(request)
    return redirect('home')




from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import DeliveryBoy
from django.core.files.storage import FileSystemStorage

def delivery_boy_registration(request):
    if request.method == 'POST':
        # Extracting data from the request
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        district = request.POST['district']
        place = request.POST['place']
        location = request.POST['location']
        pincode = request.POST['pincode']
        password = request.POST['password']  # Get the password from the form
        
        # Hash the password
        hashed_password = make_password(password)

        # Handling file uploads
        image = request.FILES['image']
        idproof = request.FILES['idproof']

        # Save the files to the media directory
        fs = FileSystemStorage()
        image_filename = fs.save(image.name, image)
        idproof_filename = fs.save(idproof.name, idproof)

        # Create and save a new DeliveryBoy instance
        delivery_boy = DeliveryBoy(
            firstname=firstname,
            lastname=lastname,
            email=email,
            phone=phone,
            state=state,
            district=district,
            place=place,
            location=location,
            pincode=pincode,
            image=image_filename,
            idproof=idproof_filename,
            password=hashed_password,  # Save the hashed password
        )
        delivery_boy.save()

        return redirect('success_page')  # Redirect to a success page after registration

    return render(request, 'delivery_boy_registration.html')  # Render the registration form
  # Render the registration form

def success_page(request):
    return render(request, 'success.html')













#here to
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .models import DeliveryBoy, Booking
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DeliveryBoy

def delivery_boy_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            delivery_boy = DeliveryBoy.objects.get(email=email)
            
            if not delivery_boy.is_approved:  
                messages.error(request, 'Your account is not approved yet. Please wait for admin approval.')
                return redirect('delivery_boy_login')

            if delivery_boy.check_password(password):  
                request.session['delivery_boy_id'] = delivery_boy.id  # Save session
                return redirect('delivery_boy_dashboard')  # Redirect to dashboard
            else:
                messages.error(request, 'Invalid email or password.')

        except DeliveryBoy.DoesNotExist:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'delivery_boy_login.html')


from django.shortcuts import render
from .models import DeliveryBoy

def verify_delivery_boys(request):
    delivery_boys = DeliveryBoy.objects.all()  # Fetch all registered delivery boys
    return render(request, 'verify_delivery_boys.html', {'title': 'Delivery Boys', 'delivery_boys': delivery_boys})

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import DeliveryBoy

def approve_delivery_boy(request, delivery_boy_id):
    delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)
    delivery_boy.is_approved = True  # Approve the delivery boy
    delivery_boy.save()
    messages.success(request, f"{delivery_boy.firstname} {delivery_boy.lastname} has been approved!")
    return redirect('verify_delivery_boys')  # Redirect back to the verification page

from django.shortcuts import render, get_object_or_404
from .models import DeliveryBoy

def delivery_boy_details(request, delivery_boy_id):
    delivery_boy = get_object_or_404(DeliveryBoy, id=delivery_boy_id)
    return render(request, 'delivery_boy_details.html', {'delivery_boy': delivery_boy})



#here









def confirm_delivery_boy(request, id):
    delivery_boy = DeliveryBoy.objects.get(id=id)
    delivery_boy.is_verified = True  # Set the delivery boy as verified
    delivery_boy.save()
    return redirect('verify_delivery_boys')  # Redirect back to the verification page


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Status  # Ensure correct imports

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Status
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Status

def update_delivery_status(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.POST.get("status")

        if new_status in ["Out for Delivery", "Delivered"]:
            status_obj, created = Status.objects.get_or_create(name=new_status)
            booking.status = status_obj
            booking.save()
            messages.success(request, f"Status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status update attempt.")

    return redirect('delivery_boy_dashboard')  # Redirect back to dashboard



import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import re  # Import regex module for text processing

# Ensure your API key is set in your Django settings
API_KEY = settings.GEMINI_API_KEY  # Store your API key securely in settings
API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'

def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        response = get_gemini_response(user_message)
        return JsonResponse({'response': response})
    return render(request, 'chatbot.html')

def get_gemini_response(user_message):
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'contents': [{
            'parts': [{
                'text': user_message
            }]
        }]
    }

    # Sending the request to the API
    response = requests.post(API_URL, headers=headers, json=data)

    # Debugging information
    print("Response Status Code:", response.status_code)  # Log status code
    try:
        response_data = response.json()  # Attempt to parse response as JSON
        print("Response Body:", response_data)  # Log response body
    except ValueError:
        print("Response could not be parsed as JSON:", response.text)
        return 'Error: Unable to parse response from the API.'

    if response.status_code == 200:
        # Check for expected keys in the response
        if 'candidates' in response_data and len(response_data['candidates']) > 0:
            raw_text = response_data['candidates'][0]['content']['parts'][0]['text']
            return preprocess_output(raw_text)
        else:
            return 'No candidates found in response.'
    else:
        # Return detailed error information
        return f'Error: {response.status_code} - {response_data.get("error", "Unknown error occurred.")}'

def preprocess_output(text):
    # Remove unwanted characters like asterisks and markdown syntax
    text = re.sub(r'\*+', '', text)  # Remove asterisks
    text = re.sub(r'\_+', '', text)  # Remove underscores
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    
    # Split into paragraphs based on double line breaks (assuming text uses "\n\n" for paragraphs)
    paragraphs = text.strip().split('\n\n')
    
    # Format the output into HTML paragraphs
    formatted_output = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
    
    return formatted_output


# import os
# import requests
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.conf import settings
# import re  # Import regex module for text processing

# # Ensure your API key is set in your Django settings
# API_KEY = settings.GEMINI_API_KEY  # Store your API key securely in settings
# API_URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}'

# def chatbot(request):
#     if request.method == 'POST':
#         user_message = request.POST.get('message')
#         response = get_gemini_response(user_message)
#         return JsonResponse({'response': response})
#     return render(request, 'chatbot.html')

# def get_gemini_response(user_message):
#     # Check if the message is related to herbal shop topics
#     if not is_herbal_shop_related(user_message):
#         return 'Sorry, I can only assist with herbal shop-related questions.'

#     headers = {
#         'Content-Type': 'application/json',
#     }
#     data = {
#         'contents': [{
#             'parts': [{
#                 'text': user_message
#             }]
#         }]
#     }

#     # Sending the request to the API
#     response = requests.post(API_URL, headers=headers, json=data)

#     # Debugging information
#     print("Response Status Code:", response.status_code)  # Log status code
#     try:
#         response_data = response.json()  # Attempt to parse response as JSON
#         print("Response Body:", response_data)  # Log response body
#     except ValueError:
#         print("Response could not be parsed as JSON:", response.text)
#         return 'Error: Unable to parse response from the API.'

#     if response.status_code == 200:
#         # Check for expected keys in the response
#         if 'candidates' in response_data and len(response_data['candidates']) > 0:
#             raw_text = response_data['candidates'][0]['content']['parts'][0]['text']
#             return preprocess_output(raw_text)
#         else:
#             return 'No candidates found in response.'
#     else:
#         # Return detailed error information
#         return f'Error: {response.status_code} - {response_data.get("error", "Unknown error occurred.")}'

# def is_herbal_shop_related(message):
#     # Define a list of keywords related to herbal shop inquiries
#     herbal_keywords = [
#         'herb', 'herbal', 'tea', 'plant', 'supplement', 'natural', 
#         'remedy', 'medicinal', 'wellness', 'essential oil', 'tincture', 
#         'herb garden', 'health', 'herbalist', 'herbs', 'nutrition',
#         'aloevera', 'anise', 'arnica', 'astragalus', 'basil', 'bitter melon', 
#         'black cohosh', 'black seed', 'burdock', 'cayenne', 'chamomile', 
#         'chickweed', 'chinese medicine', 'cinnamon', 'clove', 'comfrey', 
#         'coriander', 'dandelion', 'echinacea', 'elderberry', 'fennel', 
#         'fenugreek', 'flaxseed', 'garlic', 'ginger', 'ginseng', 'goldenseal', 
#         'hawthorn', 'hibiscus', 'hops', 'horsetail', 'lavender', 'lemon balm', 
#         'licorice', 'marshmallow', 'milk thistle', 'moringa', 'myrrh', 
#         'nettle', 'oregano', 'passionflower', 'peppermint', 'red clover', 
#         'rosemary', 'sage', 'saw palmetto', 'st john\'s wort', 'thyme', 
#         'turmeric', 'valerian', 'willow bark', 'yarrow', 'zinc', 'zucchini', 
#         'allergies', 'anxiety', 'arthritis', 'asthma', 'blood pressure', 
#         'cough', 'cold', 'digestive issues', 'diabetes', 'eczema', 
#         'fatigue', 'headache', 'heart health', 'inflammation', 'insomnia', 
#         'joint pain', 'menopause', 'migraines', 'nausea', 'pms', 
#         'respiratory health', 'skin care', 'stress', 'weight loss', 
#         'wound healing',
#         "Herbal Shampoo: Shampoo infused with herbal extracts for hair health.",
#     "Herbal Conditioner: Conditioner that nourishes hair using plant-based ingredients.",
#     "Herbal Soap: Natural soap made with herbal oils and extracts.",
#     "Herbal Body Lotion: Moisturizing lotion with herbal ingredients for skin hydration.",
#     "Herbal Face Wash: Gentle cleanser made with herbs for facial cleansing.",
#     "Herbal Face Mask: Masks formulated with herbal extracts for skin rejuvenation.",
#     "Herbal Exfoliating Scrub: Scrubs that use herbal ingredients to remove dead skin cells.",
#     "Herbal Deodorant: Natural deodorant made with herbal ingredients to combat odor.",
#     "Herbal Toothpaste: Toothpaste made with herbal extracts for oral health.",
#     "Herbal Mouthwash: Alcohol-free mouthwash infused with herbs for fresh breath.",
#     "Herbal Cream: Skin cream enriched with herbal extracts for various skin issues.",
#     "Herbal Balm: Ointment made from herbs for soothing skin or muscle aches.",
#     "Herbal Lip Balm: Moisturizing lip product made with herbal ingredients.",
#     "Herbal Perfume: Fragrance made from essential oils and herbal extracts.",
#     "Herbal Hair Oil: Oil for hair nourishment and scalp health.",
#     "Herbal Bath Salts: Soaking salts infused with herbs for relaxation.",
#     "Herbal Body Wash: Liquid cleanser for the body made from herbal ingredients.",
#     "Herbal Anti-Aging Cream: Cream formulated with herbs for reducing signs of aging.",
#     "Herbal Sunblock: Natural sunscreen with herbal ingredients for sun protection.",
#     "Herbal Aftershave: Soothing aftershave balm made with herbs for skin comfort.",
#     "Herbal Foot Cream: Cream designed to nourish and refresh tired feet.",
#     "Herbal Nail Oil: Oil for strengthening and conditioning nails.",
#     "Herbal Hair Serum: Serum that promotes shine and health in hair.",
#     "Herbal Stretch Mark Cream: Cream designed to reduce the appearance of stretch marks.",
#     "Herbal Acne Treatment: Formulations targeting acne using herbal ingredients.",
#     "Herbal Skin Brightening Serum: Serum to enhance skin radiance and tone.",
#     "Herbal Eye Cream: Cream formulated to reduce puffiness and dark circles under the eyes.",
#     "Herbal Scar Cream: Cream that helps in reducing the appearance of scars.",
#     "Herbal Cold Cream: Thick cream for moisturizing and protecting the skin in cold weather.",
#     "Herbal Hair Mask: Deep conditioning treatment made with herbs for hair restoration.",
#     "Herbal Anti-Dandruff Shampoo: Shampoo formulated to reduce dandruff using herbal ingredients.",
#     "Herbal Hand Sanitizer: Alcohol-free sanitizer infused with herbal extracts for cleanliness.",
#     "Herbal Shaving Cream: Cream for smooth shaving made with soothing herbal ingredients.",
#     "Herbal Makeup Remover: Gentle remover made from herbal ingredients.",
#     "Herbal Antiseptic Spray: Herbal spray for minor cuts and abrasions.",
#     "Herbal Skin Toner: Toner made from herbs to balance and refresh the skin.",
#     "Herbal Baby Lotion: Gentle lotion for baby skin care with herbal ingredients.",
#     "Herbal Hair Coloring: Natural hair dyes derived from herbs for coloring hair.",
#     "Herbal Ear Drops: Herbal formulations for soothing ear discomfort.",
#     "Herbal Cough Syrup: Syrup made with herbs to relieve cough symptoms.",
#     "Herbal Sleep Spray: Pillow spray infused with calming herbal scents for better sleep.",
#     "Herbal Energy Drink: Beverage made with herbs for boosting energy.",
#     "Herbal Protein Powder: Plant-based protein powder with herbal extracts.",
#     "Herbal Weight Loss Tea: Tea designed to support weight loss using herbal ingredients.",
#     "Herbal Immune Booster: Supplement made from herbs to enhance immune function.",
#     "Herbal Digestive Aid: Products made with herbs to support digestive health.",
#     "Herbal Fertility Blend: Formulations made from herbs to support reproductive health.",
#     "Herbal Detox Tea: Tea that aids detoxification processes in the body.",
#     "Herbal Hormonal Balance Supplement: Products formulated with herbs for hormonal health.",
#     "Herbal Joint Support Formula: Supplements that use herbs to support joint health.",
#     "Acne",
#     "Anxiety",
#     "Arthritis",
#     "Asthma",
#     "Back Pain",
#     "Bloating",
#     "Cold and Flu",
#     "Constipation",
#     "Cough",
#     "Depression",
#     "Diabetes",
#     "Digestive Disorders",
#     "Eczema",
#     "Fatigue",
#     "Fever",
#     "Headaches",
#     "High Blood Pressure",
#     "High Cholesterol",
#     "Hormonal Imbalance",
#     "Indigestion",
#     "Inflammation",
#     "Insomnia",
#     "Menstrual Cramps",
#     "Migraine",
#     "Nausea",
#     "PMS (Premenstrual Syndrome)",
#     "Respiratory Issues",
#     "Skin Irritations",
#     "Sleep Disorders",
#     "Stress",
#     "Thyroid Disorders",
#     "Ulcers",
#     "Varicose Veins",
#     "Weight Management",
#     "Wound Healing",
#     "Digestive Enzyme Deficiency",
#     "Immune System Support",
#     "Liver Health",
#     "Kidney Stones",
#     "Memory and Cognitive Function",
#     "Menopausal Symptoms",
#     "Nutritional Deficiencies",
#     "Oral Health Issues",
#     "Panic Attacks",
#     "Poor Circulation",
#     "Rheumatism",
#     "Scarring",
#     "Seasonal Allergies",
#     "Skin Aging",
#     "Stress-Related Disorders",


#     ]

#     # Check if any of the keywords are present in the user message (case insensitive)
#     return any(keyword in message.lower() for keyword in herbal_keywords)


# def preprocess_output(text):
#     # Remove unwanted characters like asterisks and markdown syntax
#     text = re.sub(r'\*+', '', text)  # Remove asterisks
#     text = re.sub(r'\_+', '', text)  # Remove underscores
#     text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    
#     # Split into paragraphs based on double line breaks (assuming text uses "\n\n" for paragraphs)
#     paragraphs = text.strip().split('\n\n')
    
#     # Format the output into HTML paragraphs
#     formatted_output = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
    
#     return formatted_output
