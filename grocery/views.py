from random import shuffle, random

from dateutil import parser
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login

from grocery.n_view import recommended_product
from .models import *
from datetime import date
from django.db import transaction

# Create your views here.

def Home(request):
    search = request.GET.get('search', 0)
    print(search,1112332)
    search_pro = None

    if search == "":
        pass
    elif search==0:
        pass
    else:
        search_pro = Product.objects.filter(Q(name__icontains=search) | Q(category__name__icontains=search))
    cat = ""
    pro = ""
    cat = ""
    num = 0
    num1 = 0
    cat = Category.objects.all()
    pro = Product.objects.all()
    num = []
    num1 = 0
    product = None
    try:
        user = User.objects.get(id=request.user.id)
        profile = Profile.objects.get(user=user)
        cart = Cart.objects.filter(profile=profile)
        product = recommended_product(request)
        for i in cart:
            num1 += 1

    except:
        pass
    a = 1
    li = []

    for j in pro:
        b = 1
        for i in cat:
            if i.name == j.category.name:
                if not j.category.name in li:
                    li.append(j.category.name)
                    if b == 1:
                        num.append(a)
                        b = 2
        a += 1

    d = {'pro': pro, 'cat': cat, 'num': num, 'num1': num1, 'product': product, 'search_pro': search_pro}
    return render(request, 'all_product.html', d)


def About(request):
    return render(request, 'about.html')


def Contact(request):
    return render(request, 'contact.html')


def Signup(request):
    error = False
    if request.method == 'POST':
        f = request.POST['fname']
        l = request.POST['lname']
        u = request.POST['uname']
        p = request.POST['pwd']
        d = request.POST['date']
        c = request.POST['city']
        ad = request.POST['add']
        e = request.POST['email']
        con = request.POST['contact']

        user = User.objects.create_user(username=u, email=e, password=p, first_name=f, last_name=l)
        Profile.objects.create(user=user, dob=d, city=c, address=ad, contact=con)

        error = True

    d = {'error': error}
    return render(request, 'signup.html', d)


def Login(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user:
                login(request, user)
                error = "yes"
            else:
                error = "not"
        except:
            error = "not"
    d = {'error': error}
    return render(request, 'login.html', d)


def Admin_Login(request):
    error = ""
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        try:
            if user.is_staff:
                login(request, user)
                error = "yes"
            else:
                error = "not"
        except:
            error = "not"
    d = {'error': error}
    return render(request, 'loginadmin.html', d)


def Logout(request):
    logout(request)
    return redirect('home')


def View_user(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Profile.objects.all()
    d = {'user': pro}
    return render(request, 'view_user.html', d)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Category, Product, Supply  # Ensure Supply model is imported
from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Supply  # Ensure these models exist

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProductRequest, Product, Category

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, ProductRequest

def Add_Product(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    categories = Category.objects.all()
    completed_supplies = ProductRequest.objects.filter(status="Completed")  # Fetch completed supplies

    if request.method == "POST":
        try:
            category_name = request.POST.get('cat')
            product_name = request.POST.get('pname')
            price = float(request.POST.get('price', 0))
            image = request.FILES.get('img')
            description = request.POST.get('desc')
            date = request.POST.get('date')
            expiry_date = request.POST.get('expiry_date')
            stock = int(request.POST.get('stock', 0))
            selected_supply_id = request.POST.get("selected_supply")

            if not all([category_name, product_name, price, image, description, date, expiry_date, stock]):
                messages.error(request, "All fields are required.")
                return redirect('add_product')

            category = get_object_or_404(Category, name=category_name)

            # Fetch the selected supply for validation
            if selected_supply_id:
                selected_supply = get_object_or_404(ProductRequest, id=selected_supply_id)

                # Ensure the new price is not greater than the supplied price
                if price > selected_supply.price_per_product:
                    messages.error(request, f"Product price cannot exceed the supplied price of ₹{selected_supply.price_per_product}.")
                    return redirect('add_product')

                # Ensure the new price is not less than the stock price
                if price < selected_supply.price_per_product * 0.9:  # Assuming 10% threshold
                    messages.warning(request, f"Warning: The price you entered (₹{price}) is significantly lower than the stock price (₹{selected_supply.price_per_product}).")

            # Create the product if validation passes
            Product.objects.create(
                category=category,
                name=product_name,
                price=price,
                image=image,
                desc=description,
                date=date,
                expiry_date=expiry_date,
                stock=stock
            )

            messages.success(request, "Product added successfully!")
            return redirect('view_product')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    context = {
        'categories': categories,
        'completed_supplies': completed_supplies
    }
    return render(request, 'add_product.html', context)




def All_product(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    num1 = 0
    for i in cart:
        num1 += 1
    cat = Category.objects.all()
    pro = Product.objects.all()
    d = {'pro': pro, 'cat': cat, 'num1': num1}
    return render(request, 'all_product.html', d)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking

from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking

from django.shortcuts import render, redirect, get_object_or_404
from .models import Booking, DeliveryBoy
from django.contrib.auth.decorators import login_required

@login_required
def Admin_View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    book = Booking.objects.all()
    delivery_boys = DeliveryBoy.objects.all()  # Fetch all available delivery boys

    return render(request, 'admin_viewBokking.html', {'book': book, 'delivery_boys': delivery_boys})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Product, Cart

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, Product, Cart

def Add_Cart(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == "POST":
        user = request.user
        profile = get_object_or_404(Profile, user=user)
        product = get_object_or_404(Product, id=pid)

        with transaction.atomic():  # Ensure atomicity
            product.refresh_from_db()  # Refresh stock data before modifying
            
            if product.stock > 0:
                cart_item, created = Cart.objects.get_or_create(profile=profile, product=product)

                if created:
                    cart_item.quantity = 1  # Set to 1 if newly created
                else:
                    if cart_item.quantity + 1 > product.stock:
                        messages.error(request, "Not enough stock available!")
                        return redirect('cart')

                    cart_item.quantity += 1  # Only increase if within stock limits
                
                cart_item.save()
                product.stock -= 1  # Reduce stock correctly
                product.save()

                messages.success(request, f"{product.name} added to cart!")

            else:
                messages.error(request, "This product is out of stock!")

        return redirect('cart')

def increase_quantity(request, cid):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = get_object_or_404(Cart, id=cid)
    product = cart_item.product

    with transaction.atomic():
        product.refresh_from_db()

        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            product.stock -= 1  # Deduct stock correctly
            product.save()
            messages.success(request, f"Updated quantity for {product.name}.")
        else:
            messages.error(request, "Not enough stock available!")

    return redirect('cart')
from django.db import transaction

def decrease_quantity(request, cid):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = get_object_or_404(Cart, id=cid)
    product = cart_item.product

    with transaction.atomic():  # Ensure atomicity
        if cart_item.quantity > 1:  # Ensure quantity doesn't go below 1
            cart_item.quantity -= 1
            cart_item.save()
            product.stock += 1  # Restore stock correctly
            product.save()
            messages.success(request, f"Reduced quantity for {product.name}.")
        else:
            product.stock += 1  # Restore stock when removing completely
            product.save()
            cart_item.delete()  # Remove item if quantity reaches 0
            messages.success(request, f"Removed {product.name} from cart.")

    return redirect('cart')

def remove_cart(request, cid):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = get_object_or_404(Cart, id=cid)
    product = cart_item.product

    with transaction.atomic():
        product.stock += cart_item.quantity  # Restore stock before deleting
        product.save()
        cart_item.delete()

    messages.success(request, f"{product.name} removed from cart.")
    return redirect('cart')


def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)

    pro = recommended_product(request)
    total = sum(item.product.price * item.quantity for item in cart)
    num1 = sum(item.quantity for item in cart)

    book_id = request.user.username
    message1 = "Here ! No Any Product"
    
    for item in cart:
        book_id = f"{book_id}.{item.product.id}"
    
    # Calculate item total price in view
    for item in cart:
        item.total_price = item.product.price * item.quantity  

    d = {
        'profile': profile,
        'cart': cart,
        'total': total,
        'num1': num1,
        'book': book_id,
        'message': message1,
        'pro': pro
    }
    return render(request, 'cart.html', d)





def remove_cart(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    cart_item = Cart.objects.get(id=pid)
    product = cart_item.product

    product.stock += cart_item.quantity  # Return the full quantity back to stock
    product.save()

    cart_item.delete()

    return redirect('cart')


from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Cart, Booking, Status

def Booking_order(request, pid):
    if not request.user.is_authenticated:
        return redirect('login')

    data1 = User.objects.get(id=request.user.id)
    data = Profile.objects.filter(user=data1).first()
    cart = Cart.objects.filter(profile=data).all()

    total = 0
    num1 = 0
    for i in cart:
        total += i.product.price * i.quantity  # Update total price based on quantity
        num1 += i.quantity  # Count total number of items

    user1 = data1.username
    li = pid.split('.')
    li2 = []
    for j in li:
        if user1 != j:
            li2.append(int(j))

    date1 = date.today()

    if request.method == "POST":
        d = request.POST['date1']
        c = request.POST['name']
        c1 = request.POST['city']
        ad = request.POST['add']
        e = request.POST['email']
        con = request.POST['contact']
        b = request.POST['book_id']
        t = request.POST['total']

        user = User.objects.get(username=c)
        profile = Profile.objects.get(user=user)
        status = Status.objects.get(name="pending")

        cart2 = Cart.objects.filter(profile=profile).all()
        
        # Deduct stock for each product in the cart
        with transaction.atomic():
            for cart_item in cart2:
                product = cart_item.product
                if product.stock >= cart_item.quantity:
                    product.stock -= cart_item.quantity
                    product.save()
                else:
                    messages.error(request, f"Not enough stock for {product.name}")
                    return redirect('view_cart')
                    
            # Create the booking after stock deduction is successful    
            book1 = Booking.objects.create(
                profile=profile, 
                book_date=date1, 
                booking_id=b, 
                total=t, 
                quantity=num1, 
                status=status
            )
            
            # Clear the cart after successful booking
            cart2.delete()

        return redirect('payment', book1.total)  # Redirect to payment page

    context = {'data': data, 'data1': data1, 'book_id': pid, 'date1': date1, 'total': total, 'num1': num1}
    return render(request, 'booking.html', context)



from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile, Cart, Product  # Import necessary models
from django.db import transaction

def payment(request, total):
    if not request.user.is_authenticated:
        return redirect('login')
    
    error = False
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile).all()  # Get all items in the cart
    
    if request.method == "POST":
        # Handle payment processing here
        payment_successful = True  # Replace with actual payment processing logic
        
        if payment_successful:
            try:
                # Use a transaction to ensure atomic operations
                with transaction.atomic():
                    for item in cart:
                        product = item.product  # Assuming Cart has a foreign key to Product
                        if product.stock > 0:
                            product.stock -= item.quantity  # Decrease stock by quantity in the cart
                            product.save()
                        else:
                            # Handle out of stock scenario
                            error = True
                            break

                if error:
                    # If any product was out of stock, show an error message
                    return render(request, 'payment2.html', {'total': total, 'error': 'Some items are out of stock.'})
                else:
                    # Clear the cart after successful payment
                    cart.delete()  # Clear cart items after purchase
                    return redirect('view_booking')  # Redirect to booking view or success page
            except Exception as e:
                # Log the exception and show a generic error message
                error = True
                return render(request, 'payment2.html', {'total': total, 'error': 'Payment processing failed.'})
    
    d = {'total': total, 'error': error}
    return render(request, 'payment2.html', d)



def delete_admin_booking(request, pid, bid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    book = Booking.objects.get(booking_id=pid, id=bid)
    book.delete()
    return redirect('admin_viewBooking')





def delete_user(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=pid)
    user.delete()
    return redirect('view_user')


def delete_feedback(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    feed = Send_Feedback.objects.get(id=pid)
    feed.delete()
    return redirect('view_feedback')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Product, Profile, ReturnRequest

@login_required
def booking_detail(request, pid, bid):
    if not request.user.is_authenticated:
        return redirect('login')

    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile).all()
    product = Product.objects.all()

    # Fetch the booking object
    book = Booking.objects.get(booking_id=pid, id=bid)
    
    # Fetch delivery boy details
    delivery_boy = book.delivery_boy if book.delivery_boy else None
    status = book.status.name if book.status else "Pending"

    # Get the product ID from the booking
    product_id = None
    try:
        parts = book.booking_id.split('.')
        if len(parts) >= 2:
            product_id = int(parts[1])
    except Exception as e:
        logger.error(f"Error extracting product ID: {e}")
        
    if not product_id and book.product:
        product_id = book.product.id

    # Fetch return request if exists
    return_request = None
    if product_id:
        try:
            return_request = ReturnRequest.objects.filter(
                user=user,
                product_id=product_id,
                booking=book
            ).order_by('-created_at').first()
        except ReturnRequest.DoesNotExist:
            pass

    total = sum(item.product.price for item in cart)
    num1 = len(cart)

    # Extracting booking details
    user1 = user.username
    li = book.booking_id.split('.')
    li2 = [int(j) for j in li if user1 != j]

    context = {
        'profile': profile,
        'cart': cart,
        'total': total,
        'num1': num1,
        'book': li2,
        'product': product,
        'total': book,
        'status': status,
        'delivery_boy': delivery_boy,
        'return_request': return_request,
        'booking': book  # Pass the full booking object
    }

    return render(request, 'booking_detail.html', context)



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Booking, Profile, Product

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Booking, Product

def generate_invoice(request, bid):
    # Fetch the booking and related details
    booking = Booking.objects.get(id=bid)
    profile = booking.profile
    products = Product.objects.filter(id__in=[int(i) for i in booking.booking_id.split('.') if i.isdigit()])

    # Calculate tax and subtotal
    subtotal = sum([product.price for product in products])
    tax = round(subtotal * 0.10, 2)  # 10% tax
    total = subtotal + tax

    # Prepare context for template
    context = {
        'booking': booking,
        'profile': profile,
        'products': products,
        'booking.subtotal': subtotal,
        'booking.tax': tax,
        'booking.total': total,
    }

    # Load template
    template_path = 'invoice_template.html'
    template = get_template(template_path)
    html = template.render(context)

    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.booking_id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF invoice.')

    return response



def admin_booking_detail(request, pid, bid, uid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    user = User.objects.get(id=uid)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile).all()
    product = Product.objects.all()
    book = Booking.objects.get(booking_id=pid, id=bid)
    total = 0
    num1 = 0
    user1 = user.username
    li = book.booking_id.split('.')
    li2 = []
    for j in li:
        if user1 != j:
            li2.append(int(j))
    for i in cart:
        total += i.product.price
        num1 += 1
    d = {'profile': profile, 'cart': cart, 'total': total, 'num1': num1, 'book': li2, 'product': product, 'total': book}
    return render(request, 'admin_view_booking_detail.html', d)


def Edit_status(request, pid, bid):
    if not request.user.is_authenticated:
        return redirect('login_admin')

    book = Booking.objects.get(booking_id=pid, id=bid)
    stat = Status.objects.all()  # Fetch all status options from the database

    if request.method == "POST":
        n = request.POST['book']
        s = request.POST['status']  # Get selected status from form
        book.booking_id = n
        
        sta = Status.objects.filter(name=s).first()  # Fetch corresponding Status instance
        if sta:  # Ensure status exists
            book.status = sta
            book.save()
        
        return redirect('admin_viewBooking')

    d = {'book': book, 'stat': stat}
    return render(request, 'status.html', d)




def Admin_View_product(request):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Product.objects.all()
    d = {'pro': pro}
    return render(request, 'admin_view_product.html', d)


def delete_product(request, pid):
    if not request.user.is_authenticated:
        return redirect('login_admin')
    pro = Product.objects.get(id=pid)
    pro.delete()
    return redirect('admin_view_product')

from django.shortcuts import render, redirect, get_object_or_404