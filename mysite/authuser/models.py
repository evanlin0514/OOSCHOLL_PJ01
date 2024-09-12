from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.utils import timezone

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
        

    def create_user(self, email = None, password = None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(blank = True, default= '', unique=True)
    name = models.CharField(max_length=255, blank=True, default='')

    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'tb_user'

    def get_user_id(self):
        return self.id

class StockManager(models.Manager):
    def update_stock(self, ticker, date, open, high, low, close, volume):
        stock, created = self.update_or_create(
            ticker=ticker,
            date=date,
            defaults={
                'open': open,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            }
        )
        return stock

class Stock(models.Model):
    ticker = models.CharField(max_length=10)
    date = models.DateField()
    open = models.DecimalField(max_digits=10, decimal_places=2)
    high = models.DecimalField(max_digits=10, decimal_places=2)
    low = models.DecimalField(max_digits=10, decimal_places=2)
    close = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Add default value
    volume = models.BigIntegerField()
    d5 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    d10 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    d15 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = StockManager()

    class Meta:
        unique_together = ('ticker', 'date')
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        db_table = 'tb_stock'

    def __str__(self):
        return f"{self.ticker} - {self.date}"

class ListManager(models.Manager):
    def _create_list(self, list_name, user_id):
        user = User.objects.get(id=user_id)
        list = self.model(name=list_name, user = user)
        list.save(using=self._db)
        return list
    

class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    stocks = models.ManyToManyField(
        'Stock',
        through='DataManager',
        through_fields=('list', 'stock'),
        related_name='watchlists'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'name']
        db_table = 'tb_list'

    def __str__(self):
        return f"{self.user.name}'s {self.name} Watchlist"

class DataManager(models.Model):
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='data_managers')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='data_managers')

    def __str__(self):
        return f"{self.list} - {self.stock}"

    class Meta:
        db_table = 'tb_manager'
        unique_together = ('list', 'stock')
