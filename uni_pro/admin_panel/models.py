from django.db import models

def food_image_upload_to(instance, filename):
    return f'foods/{instance.category}/{filename}'

class Course(models.Model):
    name = models.CharField(max_length=200)
    professor = models.CharField(max_length=200)
    grade = models.CharField(max_length=50)
    credits = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Food(models.Model):
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    imgoffood = models.ImageField(upload_to=food_image_upload_to, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.category})"
