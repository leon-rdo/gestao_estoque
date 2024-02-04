from django.db import models
from django.utils.text import slugify

import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Categoria", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    @property
    def quantity(self):
        return self.product_set.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey('inventory_management.Category', on_delete=models.CASCADE, verbose_name="Categoria")
    name = models.CharField("Nome do Produto", max_length=100)
    description = models.TextField("Descrição")
    price = models.DecimalField("Preço", max_digits=10, decimal_places=2)
    image = models.ImageField("Imagem", upload_to='product_images', blank=True, null=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    @property
    def quantity(self):
        return self.productunit_set.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Produtos"
        verbose_name = "Produto"


class ProductUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    location = models.ForeignKey('inventory_management.Room', on_delete=models.CASCADE, verbose_name="Localização")
    purchase_date = models.DateField("Data de Compra", null=True, blank=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(ProductUnit, self).save(*args, **kwargs)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = "Unidades de Produto"
        verbose_name = "Unidade de Produto"


class Building(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Prédio", max_length=100)
    cep = models.CharField("CEP", max_length=8)
    street = models.CharField("Rua", max_length=100)
    number = models.CharField("Número", max_length=10)
    complement = models.CharField("Complemento", max_length=100)
    neighborhood = models.CharField("Bairro", max_length=100)
    city = models.CharField("Cidade", max_length=100)
    state = models.CharField("Estado (UF)", max_length=2)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)

    def full_address(self):
        return f"{self.street}, {self.number} - {self.neighborhood}, {self.city} - {self.state}, {self.cep}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Building, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Prédios"
        verbose_name = "Prédio"


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Sala", max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="Prédio")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)

    def full_address(self):
        return f"{self.building.street}, {self.building.number} - {self.building.neighborhood}, {self.building.city} - {self.building.state}, {self.building.cep} - Sala {self.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Salas"
        verbose_name = "Sala"


# class StockTransfer(models.Model):