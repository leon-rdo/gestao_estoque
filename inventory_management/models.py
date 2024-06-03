from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum, F, FloatField
from decimal import Decimal, ROUND_HALF_UP

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
        
@receiver(post_save, sender=Color)
def create_or_update_products_with_color(sender, instance, created, **kwargs):
    if created:
        for product in Product.objects.filter(name__contains="liso", color__isnull=True):
            Product.objects.create(name=f"{product.name.capitalize()} {instance.name}", description=product.description, price=product.price, measure=product.measure, width=product.width, composition=product.composition, image=product.image, code=product.code, ncm=product.ncm, color=instance, pattern=product.pattern, created_by=product.created_by, updated_by=product.updated_by)
    else:
        Product.objects.filter(color=instance).delete()

        
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

@receiver(post_save, sender=Pattern)
def create_or_update_products_with_pattern(sender, instance, created, **kwargs):
    if created:
        for product in Product.objects.filter(name__contains="estampado", pattern__isnull=True):
            Product.objects.create(name=f"{product.name.capitalize()} {instance.name}", description=product.description, price=product.price, measure=product.measure, width=product.width, composition=product.composition, image=product.image, code=product.code, ncm=product.ncm, color=product.color, pattern=instance, created_by=product.created_by, updated_by=product.updated_by)
    else:
        Product.objects.filter(pattern=instance).delete()
        
        
class Product(models.Model):
    MEASURE_CHOICES = (
        ('cm', 'Centímetros'),
        ('m', 'Metros'),
        ('g', 'Gramas'),
        ('kg', 'Quilogramas'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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


    def save(self, *args, **kwargs):
        if "liso" in self.name.lower() and self.color is None:
            for color in Color.objects.all():
                Product.objects.create(name=f"{self.name.capitalize()} {color.name}", description=self.description, price=self.price, measure=self.measure, width=self.width, composition=self.composition, image=self.image, code=self.code, ncm=self.ncm, color=color, pattern=self.pattern, created_by=self.created_by, updated_by=self.updated_by, slug=slugify(f"{self.name} {color.name}"))
        if "estampado" in self.name.lower() and self.pattern is None:
            for pattern in Pattern.objects.all():
                Product.objects.create(name=f"{self.name.capitalize()} {pattern.name}", description=self.description, price=self.price, measure=self.measure, width=self.width, composition=self.composition, image=self.image, code=self.code, ncm=self.ncm, color=self.color, pattern=pattern, created_by=self.created_by, updated_by=self.updated_by, slug=slugify(f"{self.name} {pattern.name}"))
        self.slug = slugify(f"{self.name}")
        self.name = self.name.capitalize()
        super(Product, self).save(*args, **kwargs)


    def clean(self):
        if Product.objects.filter(name__startswith=self.name).exists():
            raise ValidationError("Esse nome já está em uso.")
        
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
        return reverse('inventory_management:product_detail', kwargs={'slug': self.slug})
    

def get_default_location():
    return TransferAreas.objects.get_or_create(name="Depósito")[0]

class ProductUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, verbose_name="Produto")
    location = models.ForeignKey('inventory_management.TransferAreas',default=get_default_location, on_delete=models.CASCADE, verbose_name="Localização")
    building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Loja", blank=True, null=True)
    room = models.ForeignKey('inventory_management.Room', on_delete=models.CASCADE, verbose_name="Sala", blank=True, null=True)
    hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor", blank=True, null=True)
    shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, verbose_name="Prateleira", blank=True, null=True)
    purchase_date = models.DateField("Data de Compra", null=True, blank=True)
    quantity = models.IntegerField("Quantidade", default=1)
    weight_length = models.DecimalField("Tamanho / Peso", max_digits=10, decimal_places=2, null=False, blank=False)
    incoming = models.DecimalField("Rendimento", max_digits=10, decimal_places=2, null=True, blank=True)
    write_off = models.BooleanField("Baixado?", default=False)
    qr_code_generated = models.BooleanField("QR Code Gerado?", default=False) 
    modified = models.DateTimeField("Modificado", auto_now=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='productunit_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='productunit_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)


    def mark_qr_code_generated(self):
        self.qr_code_generated = True
        self.save(update_fields=['qr_code_generated'])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(ProductUnit, self).save(*args, **kwargs)
        for i in range(1, self.quantity):
            ProductUnit.objects.create(product=self.product, location=self.location, purchase_date=self.purchase_date, weight_length=self.weight_length, incoming=self.incoming, write_off=self.write_off, created_by=self.created_by, updated_by=self.updated_by, shelf=self.shelf)

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
        return reverse('inventory_management:product_unit_detail', kwargs={'product_slug':self.product.slug, 'slug': self.slug})
    
    @classmethod
    def get_total_quantity(cls):
        meters = cls.objects.filter(product__measure='m').aggregate(total_meters=Sum('weight_length'))['total_meters'] or Decimal('0')
        centimeters_to_meters = cls.objects.filter(product__measure='cm').aggregate(
            total_cm_to_m=Sum(F('weight_length') / 100.0, output_field=FloatField())
        )['total_cm_to_m'] or 0.0
        total_meters = meters + Decimal(centimeters_to_meters)

        kilograms = cls.objects.filter(product__measure='kg').aggregate(total_kilograms=Sum('weight_length'))['total_kilograms'] or Decimal('0')
        grams_to_kilograms = cls.objects.filter(product__measure='g').aggregate(
            total_g_to_kg=Sum(F('weight_length') / 1000.0, output_field=FloatField())
        )['total_g_to_kg'] or 0.0
        total_kilograms = kilograms + Decimal(grams_to_kilograms)


        total_meters = total_meters.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_kilograms = total_kilograms.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'total_meters': total_meters,
            'total_kilograms': total_kilograms
        }


class StockTransfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto")
    origin_transfer_area = models.ForeignKey('inventory_management.TransferAreas', on_delete=models.CASCADE, related_name='stocktransfer_origin', verbose_name="Origem")
    origin_shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, related_name="stocktransfer_origin_shelf", verbose_name="Prateleira de origem", blank=True, null=True)
    destination_transfer_area = models.ForeignKey('inventory_management.TransferAreas', on_delete=models.CASCADE, verbose_name="Destino de Transferência")
    destination_building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Loja de Destino", blank=True, null=True)
    destination_room = models.ForeignKey('inventory_management.Room', on_delete=models.CASCADE, verbose_name="Sala de Destino", blank=True, null=True)
    destination_hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor de Destino", blank=True, null=True)
    destination_shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, verbose_name="Prateleira de Destino", blank=True, null=True)
    transfer_date = models.DateField("Data da Transferência")
    observations = models.TextField("Observações", blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='stock_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='stock_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)
    
    def clean(self):
        if self.product_unit.write_off:
            raise ValidationError("A unidade de produto foi baixada.")
        if self.product_unit.shelf != self.origin_shelf or self.product_unit.location != self.origin_transfer_area:
            raise ValidationError("A unidade de produto não está na origem.")
        if self.origin_transfer_area == self.destination_transfer_area and self.origin_shelf == self.destination_shelf:
            raise ValidationError("A unidade de produto não pode ser transferida para o mesmo local.")
            

    def save(self, *args, **kwargs):
        self.clean()
        self.product_unit.location = self.destination_transfer_area
        self.product_unit.building = self.destination_building
        self.product_unit.room = self.destination_room
        self.product_unit.hall = self.destination_hall
        self.product_unit.shelf = self.destination_shelf
        self.product_unit.save()
        super(StockTransfer, self).save(*args, **kwargs)

    def __str__(self):
        if self.origin_shelf and self.destination_shelf:
            return f'{self.product_unit.product.name} - {self.origin_transfer_area} - {self.origin_shelf}  -->  {self.destination_transfer_area.name} - {self.destination_shelf}'
        
        if self.origin_shelf:
            return f'{self.product_unit.product.name} - {self.origin_transfer_area} - {self.origin_shelf}  -->  {self.destination_transfer_area.name}'
        
        if self.destination_shelf:
            return f'{self.product_unit.product.name} - {self.origin_transfer_area}  -->  {self.destination_transfer_area.name} - {self.destination_shelf}'
        
        return f'{self.product_unit.product.name} - {self.origin_transfer_area}  -->  {self.destination_transfer_area.name}'

    class Meta:
        verbose_name_plural = "Transferências de Estoque"
        verbose_name = "Transferência de Estoque"

    def get_absolute_url(self):
        return reverse('inventory_management:product_unit_detail', kwargs={'product_slug':self.product_unit.product.slug, 'slug': self.product_unit.slug})

class Write_off(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto", related_name='write_offs')
    origin = models.CharField("Origem", max_length=100, blank=True, null=True)
    transfer_area = models.ForeignKey('inventory_management.TransferAreas',on_delete=models.CASCADE,verbose_name="Área de transferência",related_name='writeoff_origin', blank=True, null=True)
    recomission_transfer_area = models.ForeignKey('inventory_management.TransferAreas',on_delete=models.CASCADE,verbose_name="Área de Recomissão", blank=True, null=True)
    recomission_building = models.ForeignKey('inventory_management.Building',on_delete=models.CASCADE,verbose_name="Loja de Recomissão", blank=True, null=True)
    recomission_room = models.ForeignKey('inventory_management.Room',on_delete=models.CASCADE,verbose_name="Sala de Recomissão", blank=True, null=True)
    recomission_hall = models.ForeignKey('inventory_management.Hall',on_delete=models.CASCADE,verbose_name="Corredor de Recomissão", blank=True, null=True)
    recomission_shelf = models.ForeignKey('inventory_management.Shelf',on_delete=models.CASCADE,verbose_name="Prateleira da Recomissão", blank=True, null=True)
    write_off_date = models.DateTimeField("Data de Baixa", auto_now_add=True)
    observations = models.TextField("Observações", blank=True, null=True)
    write_off_destination = models.ForeignKey('inventory_management.WriteOffDestinations', on_delete=models.CASCADE, verbose_name="Destinatário da Baixa", blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='writeoff_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='writeoff_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)
    
    def save(self, *args, **kwargs):
        if self.write_off_destination:
            self.product_unit.write_off = True
        else:
            self.product_unit.write_off = False
            
        self.product_unit.save()
        super(Write_off, self).save(*args, **kwargs)
    
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

class WriteOffDestinations(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Destinatário", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='writeoffdestinations_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='writeoffdestinations_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(WriteOffDestinations, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Destinos de Baixa"
        verbose_name = "Destino de Baixa"

class TransferAreas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Local", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='destinations_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='destinations_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(TransferAreas, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Áreas de Transferência"	
        verbose_name = "Área de Transferência"
        

class WorkSpace(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Usuário")
    product = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto")
    
    def __str__(self):
        return f'{self.user} - {self.product}'
    
    class Meta:
        verbose_name_plural = "Áreas de Trabalho"
        verbose_name = "Área de Trabalho"
    
