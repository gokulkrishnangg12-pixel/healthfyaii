from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    diabetes = models.BooleanField(default=False)
    hypertension = models.BooleanField(default=False)
    allergy = models.TextField(blank=True, help_text="Comma separated allergens")
    vegan = models.BooleanField(default=False)
    fitness_goal = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name

class ImageUpload(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='scans/', null=True, blank=True)
    expiry_image = models.ImageField(upload_to='scans/', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ScanResult(models.Model):
    image_upload = models.OneToOneField(ImageUpload, on_delete=models.CASCADE)
    health_score = models.IntegerField(null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    warnings = models.JSONField(default=list)
    nutrition_levels = models.JSONField(default=dict)
    expiry_date = models.CharField(max_length=50, null=True, blank=True)
    is_expired = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class IngredientLog(models.Model):
    RISK_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    scan_result = models.ForeignKey(ScanResult, on_delete=models.CASCADE, related_name='ingredients')
    ingredient_name = models.CharField(max_length=200)
    risk_level = models.CharField(max_length=50, choices=RISK_CHOICES)
    description = models.TextField()

class ProductAlternative(models.Model):
    scan_result = models.ForeignKey(ScanResult, on_delete=models.CASCADE, related_name='alternatives')
    suggestion_name = models.CharField(max_length=255)
    reason = models.TextField()
    image_url = models.URLField(blank=True)
