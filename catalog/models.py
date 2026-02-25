# catalog/models.py

from django.db import models

class Animal(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Иконка")
    
    class Meta:
        verbose_name = "Животное"
        verbose_name_plural = "Животные"
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.IntegerField(verbose_name="Цена")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Животное")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    image = models.ImageField(upload_to='products/', verbose_name="Изображение", blank=True, null=True)
    badge = models.CharField(max_length=50, blank=True, verbose_name="Бейдж")
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
    
    def __str__(self):
        return self.name