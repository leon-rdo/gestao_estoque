from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
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
    quantity.fget.short_description = "Quantidade"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categorias"
        verbose_name = "Categoria"

    def get_absolute_url(self):
        return reverse('inventory_management:category_items', kwargs={'slug': self.slug})

class Color(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Cor", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='color_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='color_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Color, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cores"
        verbose_name = "Cor"
        
class Pattern(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Estampa", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='pattern_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='pattern_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Pattern, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Estampas"
        verbose_name = "Estampa"
        
        
class Product(models.Model):
    MEASURE_CHOICES = (
        ('cm', 'Centímetros'),
        ('m', 'Metros'),
        ('g', 'Gramas'),
        ('kg', 'Quilogramas'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey('inventory_management.Category', on_delete=models.CASCADE, verbose_name="Categoria")
    name = models.CharField("Nome do Produto", max_length=100)
    description = models.TextField("Descrição")
    price = models.DecimalField("Preço", max_digits=10, decimal_places=2)
    measure = models.CharField("Medida", max_length=2, choices=MEASURE_CHOICES)
    width = models.DecimalField("Largura", max_digits=10, decimal_places=2, null=True, blank=True)
    composition = models.CharField("Composição", max_length=100, null=True, blank=True)
    image = models.ImageField("Imagem", upload_to='product_images', blank=True, null=True)
    code = models.CharField("Código", max_length=255, null=True, blank=True)
    ncm = models.CharField("NCM", max_length=8, null=True, blank=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    color = models.ForeignKey('inventory_management.Color', on_delete=models.CASCADE, verbose_name="Cor", blank=True, null=True, editable=False)
    pattern = models.ForeignKey('inventory_management.Pattern', on_delete=models.CASCADE, verbose_name="Estampa", blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='product_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='product_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)
        if "estampado" in self.name.lower():
            self.set_editable_fields(color=False, pattern=True)
        elif "liso" in self.name.lower():
            self.set_editable_fields(color=True, pattern=False)
        else:
            self.set_editable_fields(color=False, pattern=False)

    def set_editable_fields(self, color, pattern):
        self._meta.get_field('color').editable = color
        self._meta.get_field('pattern').editable = pattern

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    @property
    def quantity(self):
        return self.productunit_set.count()

    quantity.fget.short_description = "Quantidade"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Produtos"
        verbose_name = "Produto"
    
    def get_absolute_url(self):
        return reverse('inventory_management:product_detail', kwargs={'category_slug':self.category.slug, 'slug': self.slug})
    

def get_default_location():
    return Destinations.objects.get_or_create(name="Depósito")[0]

class ProductUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, verbose_name="Produto")
    location = models.ForeignKey('inventory_management.Destinations',default=get_default_location, on_delete=models.CASCADE, verbose_name="Localização")
    shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, verbose_name="Gaveta", blank=True, null=True)
    purchase_date = models.DateField("Data de Compra", null=True, blank=True)
    quantity = models.IntegerField("Quantidade", default=1)
    weight_length = models.DecimalField("Tamanho / Peso", max_digits=10, decimal_places=2, null=False, blank=False)
    imcoming = models.DecimalField("Rendimento", max_digits=10, decimal_places=2, null=True, blank=True)
    write_off = models.BooleanField("Baixado?", default=False)
    modified = models.DateTimeField("Modificado", auto_now=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='productunit_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='productunit_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)



    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(ProductUnit, self).save(*args, **kwargs)
        for i in range(1, self.quantity):
            ProductUnit.objects.create(product=self.product, location=self.location, purchase_date=self.purchase_date, weight_length=self.weight_length, imcoming=self.imcoming, write_off=self.write_off, created_by=self.created_by, updated_by=self.updated_by)

        self.__class__.objects.filter(id=self.id).update(quantity=1)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("A quantidade deve ser maior que 0.")
        
    def __str__(self):
        return f'{self.product.name} - {self.slug}'

    class Meta:
        verbose_name_plural = "Unidades de Produto"
        verbose_name = "Unidade de Produto"
        ordering = ['write_off', 'purchase_date', 'product']

    def get_absolute_url(self):
        return reverse('inventory_management:product_unit_detail', kwargs={'category_slug':self.product.category.slug, 'product_slug':self.product.slug, 'slug': self.slug})


class StockTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto")
    origin = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, related_name="origin", verbose_name="Origem")
    destination = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, related_name="destination", verbose_name="Destino")
    transfer_date = models.DateField("Data da Transferência")
    observations = models.TextField("Observações", blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='stock_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='stock_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        if self.origin == self.destination:
            raise ValidationError("Origem e destino não podem ser iguais.")
        if self.product_unit.write_off:
            raise ValidationError("A unidade de produto foi baixada.")
        if self.product_unit.location != self.origin:
            raise ValidationError("A unidade de produto não está na origem.")
        
        self.product_unit.location = self.destination
        self.product_unit.save()
        super(StockTransfer, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_unit.product.name} - {self.origin.hall.room.building} ( {self.origin}) -> {self.destination.hall.room.building} ({self.destination})"

    class Meta:
        verbose_name_plural = "Transferências de Estoque"
        verbose_name = "Transferência de Estoque"

    def get_absolute_url(self):
        return reverse('inventory_management:product_unit_detail', kwargs={'category_slug':self.product_unit.product.category.slug, 'product_slug':self.product_unit.product.slug, 'slug': self.product_unit.slug})

class Write_off(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto", related_name='write_offs')
    origin = models.CharField("Origem", blank=True, null=True, max_length=100)
    transfer_area = models.ForeignKey('inventory_management.Destinations',on_delete=models.CASCADE,verbose_name="Área de transferência", blank=True, null=True)
    destination = models.ForeignKey('inventory_management.Shelf',on_delete=models.CASCADE,verbose_name="Destino", blank=True, null=True)
    write_off_date = models.DateTimeField("Data de Baixa", auto_now_add=True)
    observations = models.TextField("Observações", blank=True, null=True)
    employee = models.ForeignKey('inventory_management.Employee', on_delete=models.CASCADE, verbose_name="Funcionário", blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='writeoff_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='writeoff_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)
    
    class Meta:
        verbose_name_plural = "Baixas"
        verbose_name = "Baixa"


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
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='building_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='building_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def address(self):
        return f"{self.street}, {self.number} - {self.neighborhood}, {self.city} - {self.state}, {self.cep}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Building, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Lojas"
        verbose_name = "Loja"


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Sala", max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="Prédio")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='room_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='room_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def address(self):
        return f"{self.building.street}, {self.building.number} - {self.building.neighborhood}, {self.building.city} - {self.building.state}, {self.building.cep} - Sala {self.name} "

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Room, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.building.name} - Sala {self.name}'

    class Meta:
        verbose_name_plural = "Salas"
        verbose_name = "Sala"
        ordering = ['building', 'name']

class Hall (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Corredor", max_length=100)
    room = models.ForeignKey('inventory_management.Room', on_delete=models.CASCADE, verbose_name="Sala")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='hall_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='hall_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Hall, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.room} - Corredor {self.name}'

    class Meta:
        verbose_name_plural = "Corredores"
        verbose_name = "Corredor"
        ordering = ['name']
        
class Shelf (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Prateleira", max_length=100)
    hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='shelf_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='shelf_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Shelf, self).save(*args, **kwargs)

    def full_adress(self):
        return f'{self.hall.room.building.address()} - Sala {self.hall.room.name} - Corredor {self.hall.name} - Prateleira {self.name}'
    
    def __str__(self):
        return f' {self.hall} - Prateleira {self.name}'

    class Meta:
        verbose_name_plural = "Prateleiras"
        verbose_name = "Prateleira"
        ordering = ['name']

class ClothConsumption(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto")
    weight_length_before = models.DecimalField("Tamanho / Peso Antes", max_digits=10, decimal_places=2, blank=True, null=True)
    remainder = models.DecimalField("Tamanho / Peso Atual", max_digits=10, decimal_places=2, blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='cloth_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='cloth_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        product_unit = self.product_unit
        self.weight_length_before = product_unit.weight_length

        product_unit.weight_length = self.remainder
        product_unit.save()

        self.remainder = product_unit.weight_length

        super().save(*args, **kwargs)

    def clean(self):
        product_unit = self.product_unit
        if self.remainder > product_unit.weight_length:
            raise ValidationError(_("O consumo não pode ser maior que o peso/tamanho antes da subtração."))
        if self.remainder is not None and self.remainder < 0:
            raise ValidationError(_("O peso/tamanho depois da subtração não pode ser negativo."))

        super().clean()

    def __str__(self):
        return f'{self.product_unit.product.name} - {self.pk}'

    class Meta:
        verbose_name_plural = "Consumos de Tecido"
        verbose_name = "Consumo de Tecido"

class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Funcionário", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='employee_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='employee_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Employee, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Funcionários"
        verbose_name = "Funcionário"

class Destinations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Local", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='destinations_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='destinations_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Destinations, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Destinos"
        verbose_name = "Destino"