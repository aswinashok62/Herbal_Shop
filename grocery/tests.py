from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Product, Booking, Status, Category
from decimal import Decimal

class BookingCancellationTests(TestCase):
    def setUp(self):
        # Create test user and profile
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.profile = Profile.objects.create(user=self.user)
        
        # Create another user for unauthorized tests
        self.other_user = User.objects.create_user(username='otheruser', password='testpass123')
        self.other_profile = Profile.objects.create(user=self.other_user)
        
        # Create test category
        self.category = Category.objects.create(name='Test Category')
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            price=10,
            desc='Test Description',
            stock=100,
            category=self.category
        )
        
        # Create status options
        self.pending_status = Status.objects.create(name='Pending')
        self.delivered_status = Status.objects.create(name='Delivered')
        
        # Create test booking
        self.booking = Booking.objects.create(
            profile=self.profile,
            product=self.product,
            quantity=5,
            status=self.pending_status,
            booking_id=f'testuser.{self.product.id}'
        )
        
        # Update product stock to simulate booking deductions
        self.product.stock -= 5
        self.product.save()
        
    def test_successful_booking_cancellation(self):
        """Test successful booking cancellation with proper stock restoration"""
        self.client.login(username='testuser', password='testpass123')
        initial_stock = self.product.stock
        
        response = self.client.get(reverse('delete_booking', args=[self.booking.id]))
        
        # Check redirect
        self.assertRedirects(response, reverse('view_booking'))
        
        # Verify booking is deleted
        self.assertFalse(Booking.objects.filter(id=self.booking.id).exists())
        
        # Verify stock is restored
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock + 5)
        
    def test_unauthorized_booking_cancellation(self):
        """Test that users cannot cancel other users' bookings"""
        self.client.login(username='otheruser', password='testpass123')
        
        response = self.client.get(reverse('delete_booking', args=[self.booking.id]))
        
        # Check booking still exists
        self.assertTrue(Booking.objects.filter(id=self.booking.id).exists())
        
        # Check error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("permission" in str(m) for m in messages))
        
    def test_delivered_booking_cancellation(self):
        """Test that delivered bookings cannot be cancelled"""
        self.client.login(username='testuser', password='testpass123')
        
        # Change booking status to delivered
        self.booking.status = self.delivered_status
        self.booking.save()
        
        response = self.client.get(reverse('delete_booking', args=[self.booking.id]))
        
        # Check booking still exists
        self.assertTrue(Booking.objects.filter(id=self.booking.id).exists())
        
        # Check error message
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("cannot cancel a delivered order" in str(m) for m in messages))
        
    def test_nonexistent_booking_cancellation(self):
        """Test handling of non-existent booking cancellation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Use a non-existent booking ID
        nonexistent_id = self.booking.id + 1000
        
        response = self.client.get(reverse('delete_booking', args=[nonexistent_id]))
        
        # Should return a 404 response
        self.assertEqual(response.status_code, 404)
        
    def test_unauthenticated_booking_cancellation(self):
        """Test that unauthenticated users are redirected to login"""
        # No login
        
        response = self.client.get(reverse('delete_booking', args=[self.booking.id]))
        
        # Check redirect to login page
        self.assertEqual(response.status_code, 302)  # 302 is redirect
        self.assertTrue('/login/' in response.url)  # Check if redirected to login
