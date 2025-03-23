from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .models import Booking, Cart, Product, Profile, ReturnRequest
from .n_view import recommended_product
import logging

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def delete_user_booking(request, bid):
    """
    Handle user booking cancellation and restore product stock.
    Only restore the booking deduction since we no longer deduct from cart.
    """
    if not request.user.is_authenticated:
        logger.warning("Unauthenticated user tried to cancel booking")
        return redirect('login')
        
    booking = get_object_or_404(Booking, id=bid)
    logger.debug(f"Processing booking cancellation for booking ID: {bid}, booking_id: {booking.booking_id}, status: {booking.status.name}")
    
    # Verify the booking belongs to the current user
    if booking.profile.user != request.user:
        logger.warning(f"User {request.user.username} tried to cancel booking {bid} belonging to {booking.profile.user.username}")
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('view_booking')
    
    if booking.status.name != "Delivered":
        try:
            # Extract product ID from booking_id
            product_id = None
            try:
                parts = booking.booking_id.split('.')
                logger.debug(f"Booking ID parts: {parts}")
                if len(parts) >= 2:
                    product_id = int(parts[1])
                    logger.debug(f"Extracted product ID: {product_id}")
            except Exception as e:
                logger.error(f"Error extracting product ID: {e}")
                
            if not product_id and booking.product:
                product_id = booking.product.id
                logger.debug(f"Using direct product reference: {product_id}")
                
            logger.debug(f"Final product_id: {product_id}, booking quantity: {booking.quantity}")
                
            if product_id:
                # Use direct SQL to update stock
                from django.db import connection
                with connection.cursor() as cursor:
                    # Get current stock
                    cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
                    result = cursor.fetchone()
                    if result:
                        current_stock = result[0]
                        logger.debug(f"Current stock for product {product_id}: {current_stock}")
                        
                        # Update stock
                        cursor.execute(
                            "UPDATE grocery_product SET stock = stock + %s WHERE id = %s", 
                            [booking.quantity, product_id]
                        )
                        logger.debug(f"SQL executed: UPDATE grocery_product SET stock = stock + {booking.quantity} WHERE id = {product_id}")
                        
                        # Verify stock was updated
                        cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
                        new_stock = cursor.fetchone()[0]
                        logger.debug(f"Updated stock for product {product_id}: {current_stock} -> {new_stock}")
                        
                        # Get product name for message
                        cursor.execute("SELECT name FROM grocery_product WHERE id = %s", [product_id])
                        product_name = cursor.fetchone()[0]
                        
                        messages.success(request, f"Your booking has been canceled and {booking.quantity} units have been restored to {product_name}.")
                    else:
                        logger.error(f"Product {product_id} not found in database")
                        messages.error(request, f"Product {product_id} not found. Stock not restored.")
            else:
                logger.error("Could not determine product ID from booking")
                messages.warning(request, "Could not determine product from booking. Stock not restored.")
                
            # Delete the booking
            booking.delete()
            logger.info(f"Booking {bid} successfully canceled")
            
        except Exception as e:
            logger.error(f"Unexpected error in delete_user_booking: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        logger.warning(f"Cannot cancel delivered booking {bid}")
        messages.error(request, "You cannot cancel a delivered order.")
        
    return redirect('view_booking')

@login_required
def add_to_cart(request, pid):
    """Add a product to the user's cart without affecting stock."""
    if request.method != "POST":
        return redirect('cart')

    profile = get_object_or_404(Profile, user=request.user)
    product = get_object_or_404(Product, id=pid)

    with transaction.atomic():
        product.refresh_from_db()
        
        if product.stock > 0:
            cart_item, created = Cart.objects.get_or_create(profile=profile, product=product)

            if created:
                cart_item.quantity = 1
            else:
                if cart_item.quantity + 1 > product.stock:
                    messages.error(request, "Not enough stock available!")
                    return redirect('cart')
                cart_item.quantity += 1
            
            cart_item.save()
            messages.success(request, f"{product.name} added to cart!")
        else:
            messages.error(request, "This product is out of stock!")

    return redirect('cart')

@login_required
def increase_cart_quantity(request, cid):
    """Increase the quantity of a cart item without affecting stock."""
    cart_item = get_object_or_404(Cart, id=cid)
    
    # Verify cart item belongs to user
    if cart_item.profile.user != request.user:
        messages.error(request, "You are not authorized to modify this cart item.")
        return redirect('cart')

    product = cart_item.product

    with transaction.atomic():
        product.refresh_from_db()

        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Updated quantity for {product.name}.")
        else:
            messages.error(request, "Not enough stock available!")

    return redirect('cart')

@login_required
def decrease_cart_quantity(request, cid):
    """Decrease the quantity of a cart item without affecting stock."""
    cart_item = get_object_or_404(Cart, id=cid)
    
    # Verify cart item belongs to user
    if cart_item.profile.user != request.user:
        messages.error(request, "You are not authorized to modify this cart item.")
        return redirect('cart')

    with transaction.atomic():
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            messages.success(request, f"Reduced quantity for {cart_item.product.name}.")
        else:
            cart_item.delete()
            messages.success(request, f"Removed {cart_item.product.name} from cart.")

    return redirect('cart')

@login_required
def remove_from_cart(request, cid):
    """Remove an item from the cart without affecting stock."""
    cart_item = get_object_or_404(Cart, id=cid)
    
    # Verify cart item belongs to user
    if cart_item.profile.user != request.user:
        messages.error(request, "You are not authorized to modify this cart item.")
        return redirect('cart')

    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f"{product_name} removed from cart.")

    return redirect('cart')

@login_required
def view_cart(request):
    """View the user's shopping cart."""
    profile = get_object_or_404(Profile, user=request.user)
    cart = Cart.objects.filter(profile=profile)
    
    # Get recommended products
    recommended = recommended_product(request)
    
    # Calculate totals
    total = sum(item.product.price * item.quantity for item in cart)
    total_items = sum(item.quantity for item in cart)
    
    # Generate unique booking ID
    booking_id = request.user.username
    for item in cart:
        booking_id = f"{booking_id}.{item.product.id}"
    
    # Calculate individual item totals
    for item in cart:
        item.total_price = item.product.price * item.quantity

    context = {
        'profile': profile,
        'cart': cart,
        'total': total,
        'num1': total_items,
        'book': booking_id,
        'message': "Your cart is empty" if not cart else "",
        'pro': recommended
    }
    return render(request, 'cart.html', context)

def View_Booking(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = User.objects.get(id=request.user.id)
    profile = Profile.objects.get(user=user)
    cart = Cart.objects.filter(profile=profile)
    
    # Get bookings with latest status, ordered by date
    book = Booking.objects.filter(profile=profile).select_related('status', 'delivery_boy', 'product').order_by('-book_date')
    
    # Get return requests for these bookings
    from .models import ReturnRequest
    
    # Add return request info to each booking
    for booking in book:
        try:
            booking.return_request = ReturnRequest.objects.filter(
                user=user,
                product=booking.product,
                booking=booking
            ).order_by('-created_at').first()
        except:
            booking.return_request = None
    
    # Get recommended products
    pro = recommended_product(request)
    
    num1 = 0
    for i in cart:
        num1 += 1
        
    d = {'book': book, 'num1': num1, 'pro': pro}
    return render(request, 'view_booking.html', d)

@login_required
def delete_booking(request, bid):
    if not request.user.is_authenticated:
        return redirect('login')
    
    booking = get_object_or_404(Booking, id=bid)
    logger.debug(f"Processing booking cancellation for booking ID: {bid}, booking_id: {booking.booking_id}")
    
    # Verify the booking belongs to the user
    if booking.profile.user != request.user:
        messages.error(request, "You don't have permission to cancel this booking.")
        return redirect('view_booking')
    
    if booking.status.name != "Delivered":
        try:
            # Extract product ID from booking_id
            product_id = None
            try:
                parts = booking.booking_id.split('.')
                if len(parts) >= 2:
                    product_id = int(parts[1])
                    logger.debug(f"Extracted product ID: {product_id}")
            except Exception as e:
                logger.error(f"Error extracting product ID: {e}")
                
            if not product_id and booking.product:
                product_id = booking.product.id
                logger.debug(f"Using direct product reference: {product_id}")
                
            if product_id:
                # Use direct SQL to update stock
                from django.db import connection
                with connection.cursor() as cursor:
                    # Get current stock
                    cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
                    result = cursor.fetchone()
                    if result:
                        current_stock = result[0]
                        logger.debug(f"Current stock for product {product_id}: {current_stock}")
                        
                        # Update stock
                        cursor.execute(
                            "UPDATE grocery_product SET stock = stock + %s WHERE id = %s", 
                            [booking.quantity, product_id]
                        )
                        
                        # Verify stock was updated
                        cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
                        new_stock = cursor.fetchone()[0]
                        logger.debug(f"Updated stock for product {product_id}: {current_stock} -> {new_stock}")
                        
                        # Get product name for message
                        cursor.execute("SELECT name FROM grocery_product WHERE id = %s", [product_id])
                        product_name = cursor.fetchone()[0]
                        
                        messages.success(request, f"Your booking has been canceled and {booking.quantity} units have been restored to {product_name}.")
                    else:
                        logger.error(f"Product {product_id} not found in database")
                        messages.error(request, f"Product {product_id} not found. Stock not restored.")
            else:
                logger.error("Could not determine product ID from booking")
                messages.warning(request, "Could not determine product from booking. Stock not restored.")
                
            # Delete the booking
            booking.delete()
            logger.info(f"Booking {bid} successfully canceled")
            
        except Exception as e:
            logger.error(f"Unexpected error in delete_booking: {str(e)}")
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        logger.warning(f"Cannot cancel delivered booking {bid}")
        messages.error(request, "You cannot cancel a delivered order.")
    
    return redirect('view_booking')

@login_required
def test_stock_update(request, product_id=1, quantity=1):
    """Test function to update stock directly using SQL"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get current stock
            cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
            result = cursor.fetchone()
            if result:
                current_stock = result[0]
                
                # Update stock
                cursor.execute(
                    "UPDATE grocery_product SET stock = stock + %s WHERE id = %s", 
                    [quantity, product_id]
                )
                
                # Verify stock was updated
                cursor.execute("SELECT stock FROM grocery_product WHERE id = %s", [product_id])
                new_stock = cursor.fetchone()[0]
                
                # Get product name
                cursor.execute("SELECT name FROM grocery_product WHERE id = %s", [product_id])
                product_name = cursor.fetchone()[0]
                
                messages.success(request, f"Test successful! {product_name} stock updated: {current_stock} -> {new_stock}")
            else:
                messages.error(request, f"Product {product_id} not found")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    
    return redirect('view_booking')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Booking, Product, Profile

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
        'delivery_boy': delivery_boy  # Pass delivery boy to template
    }

    return render(request, 'booking_detail.html', context)


