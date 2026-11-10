from django.db import models

class Category(models.Model):
    name = models.CharField('Назва категорії', max_length=100, unique=True)
    slug = models.SlugField('URL Slug', max_length=100, unique=True)
    description = models.TextField('Опис', blank=True, null=True)

    class Meta:
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField('Назва тегу', max_length=50, unique=True)
    code = models.CharField('Код тегу', max_length=30, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опубліковано'),
        ('archived', 'Архівовано'),
    ]

    name = models.CharField('Назва товару', max_length=200)
    price = models.DecimalField('Ціна (грн)', max_digits=10, decimal_places=2)
    in_stock = models.BooleanField('В наявності', default=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='published')
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2, default=5.0)
    created_at = models.DateTimeField('Дата створення', auto_now_add=True)
    
    # 1. Один-до-багатьох (ForeignKey)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='products',
        verbose_name='Категорія'
    )
    
    # 2. Багато-до-багатьох (ManyToManyField)
    tags = models.ManyToManyField(
        Tag, 
        blank=True, 
        related_name='products',
        verbose_name='Теги'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.price} грн)"


class ProductDetail(models.Model):
    # 3. Один-до-одного (OneToOneField)
    product = models.OneToOneField(
        Product, 
        on_delete=models.CASCADE, 
        primary_key=True,
        related_name='detail',
        verbose_name='Товар'
    )
    warranty_months = models.PositiveIntegerField('Гарантія (місяців)', default=12)
    manufacturer_country = models.CharField('Країна-виробник', max_length=100)
    specifications_json = models.JSONField('Специфікація (JSON)', default=dict, blank=True)

    class Meta:
        verbose_name = 'Деталі товару'
        verbose_name_plural = 'Деталі товарів'

    def __str__(self):
        return f"Деталі для {self.product.name}"