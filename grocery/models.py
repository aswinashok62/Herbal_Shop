from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    image = models.FileField(null=True)
    name = models.CharField(max_length=30, null=True)
    price = models.IntegerField(null=True)
    desc = models.TextField(null=True)
    date = models.DateField(default=now, null=True, blank=True)    # Field for the product date
    expiry_date = models.DateField(null=True)  # Field for the expiry date
    stock = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.category.name + "--" + self.name
    
    
    

class Status(models.Model):
    name = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    dob = models.DateField(null=True)
    city = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=50, null=True)
    contact = models.CharField(max_length=10, null=True)
    image = models.FileField(null=True)

    def __str__(self):
        return self.user.username


class Cart(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.PositiveIntegerField(default=1)  # New field for quantity

    def __str__(self):
        return f"{self.profile.user.username} - {self.product.name} (x{self.quantity})"



from django.contrib.auth.hashers import check_password
from django.db import models

from django.contrib.auth.hashers import check_password

class DeliveryBoy(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, null=True, blank=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    image = models.ImageField(upload_to='delivery_boy_images/')
    idproof = models.FileField(upload_to='id_proofs/')
    password = models.CharField(max_length=128)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def check_password(self, raw_password):
        """Check if the given raw password matches the hashed password."""
        return check_password(raw_password, self.password)


class Booking(models.Model):
    status = models.ForeignKey('Status', on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True) 
    booking_id = models.CharField(max_length=200, null=True)
    quantity = models.IntegerField(null=True)
    book_date = models.DateField(null=True)
    total = models.IntegerField(null=True)
    cancel_reason = models.CharField(max_length=255, blank=True, null=True)
    delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.SET_NULL, null=True, blank=True)  # Now it is defined
    status_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.book_date} {self.profile.user.username}"
    
  


class RefundRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    bank_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Processed', 'Processed')], default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.status}"
    
from django.db import models
from django.contrib.auth.models import User

class ReturnRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True, related_name='return_requests')
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50, null=True)
    bank_name = models.CharField(max_length=255, default="Default Bank")
    ifsc_code = models.CharField(max_length=20, null=True)

    def __str__(self):
        return f"Return Request for {self.product.name} by {self.user.username}"
 


class Send_Feedback(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    message1 = models.TextField(null=True)
    date = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.profile.user.username


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100, default="General Practitioner")

    availability = models.CharField(max_length=100, blank=True, null=True)
    fee = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='doctor_images/', blank=True, null=True)  # Ensure this exists
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.specialization}"
    

from django.core.exceptions import ValidationError

class Appointment(models.Model):
    # Define your fields here
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        # Check for existing appointments
        if Appointment.objects.filter(doctor=self.doctor, date=self.date, time=self.time).exists():
            raise ValidationError("This time slot is already booked!")

        super(Appointment, self).save(*args, **kwargs)

    
class AvailableTimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    is_booked = models.BooleanField(default=False)  # Marks if slot is taken

    def __str__(self):
        status = "Booked" if self.is_booked else "Available"
        return f"{self.doctor.user.username} - {self.date} {self.time} ({status})"


class Chat(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files/", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"
    

from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # References the User model
    message = models.TextField()  # Stores the notification message
    created_at = models.DateTimeField(default=now)  # Automatically set the timestamp when created
    is_read = models.BooleanField(default=False)  # Indicates whether the notification has been read

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

    
class Message(models.Model):
    appointment = models.ForeignKey('Appointment', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text}"
from django.db import models
from django.contrib.auth.models import User

class SupplierProfile(models.Model):
    """Model representing a supplier."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.company_name
    


    #admin status
class ProductRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Not_Available', 'Not_Available'),
    ]

    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_product = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE)
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(null=True, blank=True)
    requested_at = models.DateTimeField(default=now, null=True, blank=True)

    def __str__(self):
        return f"{self.product_name} ({self.status}) - {self.supplier.company_name} - {self.requested_at.strftime('%Y-%m-%d')}"

class Supply(models.Model):
    product = models.ForeignKey('ProductRequest', on_delete=models.CASCADE)
    quantity_supplied = models.IntegerField()
    supplied_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity_supplied}"





from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Blog(models.Model):
    title = models.CharField(max_length=255)  # Blog title
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to user
    content = models.TextField()  # Blog content
    created_at = models.DateTimeField(default=now)  # Auto timestamp
    updated_at = models.DateTimeField(auto_now=True)  # Auto update timestamp
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)  # Optional image

    def __str__(self):
        return self.title  # Display title in admin panel
