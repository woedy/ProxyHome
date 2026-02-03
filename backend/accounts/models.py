from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model with additional fields"""
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_premium = models.BooleanField(default=False)
    proxy_access_limit = models.IntegerField(default=1000)  # Daily limit
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class UserProxyAccess(models.Model):
    """Track user proxy access and usage"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proxy_access')
    date = models.DateField(auto_now_add=True)
    proxies_accessed = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'date']
        
    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.proxies_accessed}"