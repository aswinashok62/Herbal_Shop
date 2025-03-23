from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Booking, RefundRequest, ReturnRequest, Status
from .forms import RefundForm
import logging

# Configure logging
logger = logging.getLogger(__name__)

@login_required
def return_product(request, product_id):
    """
    Handle product return requests and create refund requests
    """
    product = get_object_or_404(Product, id=product_id)
    logger.debug(f"Processing return request for product ID: {product_id}, name: {product.name}")

    # Get booking_id from query parameters if available
    booking_id = request.GET.get("booking_id")
    booking = None
    
    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            logger.debug(f"Found booking with ID: {booking_id}")
        except Booking.DoesNotExist:
            logger.warning(f"Booking with ID {booking_id} not found")

    if request.method == "POST":
        # Get form data directly from POST
        reason = request.POST.get("reason")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        bank_name = request.POST.get("bank_name")
        ifsc_code = request.POST.get("ifsc_code")
        booking_id = request.POST.get("booking_id")
        
        logger.debug(f"POST data - reason: {reason}, booking_id: {booking_id}")
        
        # Try to get booking from POST if not already set
        if not booking and booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                logger.debug(f"Found booking with ID {booking_id} from POST data")
            except Booking.DoesNotExist:
                logger.warning(f"Booking with ID {booking_id} not found in POST")
        
        # Validate required fields
        if not all([reason, account_name, account_number, bank_name, ifsc_code]):
            messages.error(request, "All fields are required")
            return render(request, "refund_form.html", {
                "product": product, 
                "reason": reason,
                "booking_id": booking_id if booking_id else ""
            })
        
        # Create return request
        return_request = ReturnRequest.objects.create(
            user=request.user,
            product=product,
            booking=booking,  # Associate with booking
            reason=reason,
            account_name=account_name,
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code,
            status="Pending"
        )
        
        logger.info(f"Return request created for product {product_id} by user {request.user.username}")

        # Update booking status to "Refund Processing"
        try:
            # Find the booking for this product and user
            refund_processing_status, created = Status.objects.get_or_create(name="Refund Processing")
            
            # If we have a specific booking, update only that one
            if booking:
                booking.status = refund_processing_status
                booking.save()
                logger.debug(f"Updated booking {booking.id} status to Refund Processing")
            else:
                # Otherwise find all eligible bookings
                bookings = Booking.objects.filter(
                    profile__user=request.user, 
                    product=product,
                    status__name="Delivered"  # Only allow returns for delivered products
                )
                
                if bookings.exists():
                    for booking in bookings:
                        booking.status = refund_processing_status
                        booking.save()
                        logger.debug(f"Updated booking {booking.id} status to Refund Processing")
                else:
                    logger.warning(f"No delivered bookings found for user {request.user.username} and product {product_id}")
        except Exception as e:
            logger.error(f"Error updating booking status: {str(e)}")

        messages.success(request, "Your return request has been submitted successfully and is being processed.")
        return redirect("view_booking")
    else:
        # For GET requests, show the form with the reason from query params
        reason = request.GET.get("reason", "")
        return render(request, "refund_form.html", {"product": product, "reason": reason, "booking_id": booking_id if booking_id else ""})


@login_required
def admin_view_returns(request):
    """
    Admin view to manage return requests
    """
    if not request.user.is_staff:
        logger.warning(f"Non-staff user {request.user.username} attempted to access admin returns page")
        messages.error(request, "You don't have permission to access this page.")
        return redirect("home")

    if request.method == "POST":
        request_id = request.POST.get("request_id")
        new_status = request.POST.get("status")
        logger.debug(f"Processing status update for return request {request_id}: {new_status}")

        return_request = get_object_or_404(ReturnRequest, id=request_id)

        if new_status in ["Pending", "Approved", "Rejected"]:
            return_request.status = new_status
            return_request.save()
            
            # If approved, update product stock and change booking status to "Returned"
            if new_status == "Approved":
                try:
                    # Use the direct booking relationship if available
                    booking = return_request.booking
                    
                    # If no direct booking relationship, try to find it
                    if not booking:
                        booking = Booking.objects.filter(
                            profile__user=return_request.user,
                            product=return_request.product,
                            status__name="Refund Processing"
                        ).first()
                    
                    if booking:
                        # Update product stock
                        product = return_request.product
                        product.stock += booking.quantity
                        product.save()
                        logger.info(f"Restored {booking.quantity} units to product {product.id} stock")
                        
                        # Change status to "Returned"
                        returned_status, created = Status.objects.get_or_create(name="Returned")
                        booking.status = returned_status
                        booking.save()
                        logger.info(f"Updated booking {booking.id} status to Returned")
                except Exception as e:
                    logger.error(f"Error updating product stock: {str(e)}")
            
            messages.success(request, "Return request status updated successfully.")
        else:
            logger.warning(f"Invalid status selected: {new_status}")
            messages.error(request, "Invalid status selected.")

        return redirect("admin_view_returns")

    return_requests = ReturnRequest.objects.all().order_by("-created_at")
    return render(request, "admin_returns.html", {"return_requests": return_requests})


def refund_form(request):
    """
    Display refund form with pre-filled reason
    """
    product_id = request.GET.get("product_id")
    reason = request.GET.get("reason")
    booking_id = request.GET.get("booking_id")
    
    if not product_id:
        messages.error(request, "Product ID is required")
        return redirect("view_booking")
        
    product = get_object_or_404(Product, id=product_id)
    
    return render(request, 'refund_form.html', {
        "product": product,
        "reason": reason,
        "booking_id": booking_id
    })


@login_required
def submit_return_request(request):
    """
    Process return request submission
    """
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        reason = request.POST.get("reason")
        account_name = request.POST.get("account_name")
        account_number = request.POST.get("account_number")
        bank_name = request.POST.get("bank_name")
        ifsc_code = request.POST.get("ifsc_code")
        booking_id = request.POST.get("booking_id")
        
        if not product_id:
            messages.error(request, "Product ID is required")
            return redirect("view_booking")
            
        product = get_object_or_404(Product, id=product_id)
        
        # Get booking if booking_id is provided
        booking = None
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                logger.debug(f"Found booking with ID: {booking_id} for return request")
            except Booking.DoesNotExist:
                logger.warning(f"Booking with ID {booking_id} not found")
        
        # Create return request
        ReturnRequest.objects.create(
            user=request.user,
            product=product,
            booking=booking,  # Associate with booking
            reason=reason,
            account_name=account_name,
            account_number=account_number,
            bank_name=bank_name,
            ifsc_code=ifsc_code
        )
        
        messages.success(request, "Return request submitted successfully")
        return redirect("view_booking")
        
    # If GET request, show the form
    return redirect("refund_form")
