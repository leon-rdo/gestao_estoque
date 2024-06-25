from django.db import models, transaction
from django.forms import ValidationError
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
import uuid
from django.db.models import Sum, F, FloatField, Max
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
        ('u', 'Unidade'),
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


    def get_measure(self):
        return self.get_measure_display()

    def clean(self):
        if Product.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError("Esse nome já está em uso.")

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.name}")
        self.name = self.name.capitalize()
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
        ordering = ['name']
    
    def get_absolute_url(self):
        return reverse('inventory_management:product_detail', kwargs={'slug': self.slug})

def get_default_location():
    return StorageType.objects.get_or_create(name="Hub")[0]
        
class ProductUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField("Código", max_length=10, unique=True, editable=False)
    product = models.ForeignKey("Product", on_delete=models.CASCADE, verbose_name="Produto")
    location = models.ForeignKey('inventory_management.StorageType',default=get_default_location, on_delete=models.CASCADE, verbose_name="Localização")
    building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Depósito", blank=True, null=True)
    room = models.ForeignKey('inventory_management.Rooms', on_delete=models.CASCADE, verbose_name="Sala", blank=True, null=True)
    hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor", blank=True, null=True)
    shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, verbose_name="Prateleira", blank=True, null=True)
    purchase_date = models.DateField("Data de Entrada", auto_now_add=True)
    quantity = models.IntegerField("Quantidade", default=1)
    weight_length = models.DecimalField("Metro/Kg", max_digits=10, decimal_places=2, null=False, blank=False)
    incoming = models.DecimalField("Rendimento", max_digits=10, decimal_places=2, null=True, blank=True)
    write_off = models.BooleanField("Está Baixado?", default=False)
    was_written_off = models.BooleanField("Foi baixado?", default=False)
    qr_code_generated = models.BooleanField("QR Code Gerado?", default=False) 
    modified = models.DateTimeField("Modificado", auto_now=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='productunit_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='productunit_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def get_measure(self):
        return self.product.get_measure_display()

    def mark_qr_code_generated(self):
        self.qr_code_generated = True
        self.save(update_fields=['qr_code_generated'])

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.code:
                self.generate_code()

            super(ProductUnit, self).save(*args, **kwargs)

            if not self.slug:
                self.slug = slugify(f"{self.product.name}-{self.code}")
                self.save(update_fields=['slug'])

            if self.quantity > 1:
                for i in range(1, self.quantity):
                    new_unit = ProductUnit.objects.create(
                        product=self.product,
                        location=self.location,
                        purchase_date=self.purchase_date,
                        weight_length=self.weight_length,
                        incoming=self.incoming,
                        write_off=self.write_off,
                        created_by=self.created_by,
                        updated_by=self.updated_by,
                        shelf=self.shelf
                    )
                    new_unit.generate_code()
                    new_unit.slug = slugify(f"{self.product.name}-{new_unit.code}")
                    new_unit.save()
            
            self.__class__.objects.filter(id=self.id).update(quantity=1)

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("A quantidade deve ser maior que 0.")
    
    def generate_code(self):
        last_unit = ProductUnit.objects.aggregate(Max('code'))
        last_code = last_unit['code__max']

        if last_code:
            last_number = int(last_code.split('-')[1]) 
        else:
            last_number = 0

        new_number = last_number + 1
        self.code = f"PRD-{new_number}"

        while ProductUnit.objects.filter(code=self.code).exists():
            new_number += 1
            self.code = f"PRD-{new_number}"
        
    def __str__(self):
        return self.product.name

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
    origin_storage_type = models.ForeignKey('inventory_management.StorageType', on_delete=models.CASCADE, related_name='stocktransfer_origin', verbose_name="Origem")
    origin_building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, related_name="stocktransfer_origin_building", verbose_name="Depósito de Origem", blank=True, null=True)
    origin_hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, related_name="stocktransfer_origin_hall", verbose_name="Corredor de Origem", blank=True, null=True)
    origin_room = models.ForeignKey('inventory_management.Rooms', on_delete=models.CASCADE, related_name="stocktransfer_origin_room", verbose_name="Sala de Origem", blank=True, null=True)
    origin_shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, related_name="stocktransfer_origin_shelf", verbose_name="Prateleira de origem", blank=True, null=True)
    destination_storage_type = models.ForeignKey('inventory_management.StorageType', on_delete=models.CASCADE, verbose_name="Tipo do Depósito de Destino")
    destination_building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Depósito de Destino", blank=True, null=True)
    destination_room = models.ForeignKey('inventory_management.Rooms', on_delete=models.CASCADE, verbose_name="Sala de Destino", blank=True, null=True)
    destination_hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor de Destino", blank=True, null=True)
    destination_shelf = models.ForeignKey('inventory_management.Shelf', on_delete=models.CASCADE, verbose_name="Prateleira de Destino", blank=True, null=True)
    transfer_date = models.DateTimeField("Data da Transferência", auto_now_add= True)
    observations = models.TextField("Observações", blank=True, null=True)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='stock_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='stock_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)
    
    def clean(self):
        if self.product_unit.write_off:
            raise ValidationError("A unidade de produto foi baixada.")
        if self.product_unit.location != self.origin_storage_type:
            raise ValidationError("A unidade de produto não está na origem.")
        
            

    def save(self, *args, **kwargs):
        self.clean()
        self.product_unit.location = self.destination_storage_type
        self.product_unit.building = self.destination_building
        self.product_unit.hall = self.destination_hall
        self.product_unit.room = self.destination_room
        self.product_unit.shelf = self.destination_shelf
        if not self.destination_building:
            self.product_unit.building = None
        if not self.destination_hall:
            self.product_unit.hall = None
        if not self.destination_room:
            self.product_unit.room = None
        if not self.destination_shelf:
            self.product_unit.shelf = None
        self.product_unit.save()
        super(StockTransfer, self).save(*args, **kwargs)

    def __str__(self):
        if self.origin_shelf and self.destination_shelf:
            return f'{self.product_unit.product.name} - {self.origin_storage_type} - {self.origin_shelf}  -->  {self.destination_storage_type.name} - {self.destination_shelf}'
        
        if self.origin_shelf:
            return f'{self.product_unit.product.name} - {self.origin_storage_type} - {self.origin_shelf}  -->  {self.destination_storage_type.name}'
        
        if self.destination_shelf:
            return f'{self.product_unit.product.name} - {self.origin_storage_type}  -->  {self.destination_storage_type.name} - {self.destination_shelf}'
        
        return f'{self.product_unit.product.name} - {self.origin_storage_type}  -->  {self.destination_storage_type.name}'

    class Meta:
        verbose_name_plural = "Transferências de Estoque"
        verbose_name = "Transferência de Estoque"

    def get_absolute_url(self):
        return reverse('inventory_management:product_unit_detail', kwargs={'product_slug':self.product_unit.product.slug, 'slug': self.product_unit.slug})

class Write_off(models.Model):
    product_unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto", related_name='write_offs')
    origin = models.CharField("Origem", max_length=100, blank=True, null=True)
    storage_type = models.ForeignKey('inventory_management.StorageType',on_delete=models.CASCADE,verbose_name="Tipo de depósito",related_name='writeoff_origin', blank=True, null=True)
    recomission_storage_type = models.ForeignKey('inventory_management.StorageType',on_delete=models.CASCADE,verbose_name="Área de Recomissão",related_name="recomission_destination", blank=True, null=True)
    recomission_building = models.ForeignKey('inventory_management.Building',on_delete=models.CASCADE,verbose_name="Depósito de Recomissão", blank=True, null=True)
    recomission_hall = models.ForeignKey('inventory_management.Hall',on_delete=models.CASCADE,verbose_name="Corredor de Recomissão", blank=True, null=True)
    recomission_room = models.ForeignKey('inventory_management.Rooms',on_delete=models.CASCADE,verbose_name="Sala de Recomissão", blank=True, null=True)
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
            self.product_unit.was_written_off = True
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
    has_hall = models.BooleanField("Possui Corredor?", default=False)
    has_room = models.BooleanField("Possui Sala?", default=False)
    has_shelf = models.BooleanField("Possui Gaveta?", default=False)
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
        verbose_name_plural = "Depósitos"
        verbose_name = "Depósito"


class Hall (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Corredor", max_length=100)
    building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Prédio")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='hall_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='hall_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def clean(self):
      if self.building.has_hall == False:
            raise ValidationError("Esse prédio não possui corredores.")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Hall, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.building.name} - Corredor {self.name}'
        

    class Meta:
        verbose_name_plural = "Corredores"
        verbose_name = "Corredor"
        ordering = ['name']

class Rooms(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Sala", max_length=100)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, verbose_name="Prédio")
    hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor", blank=True, null=True)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='room_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='room_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def clean(self):
        if self.building.has_room == False:
            raise ValidationError("Esse prédio não possui salas.")
        if self.hall and self.building.has_hall == False:
            raise ValidationError("Esse prédio não possui corredores.")

    def address(self):
        return f"{self.building.street}, {self.building.number} - {self.building.neighborhood}, {self.building.city} - {self.building.state}, {self.building.cep} - Sala {self.name} "

    def save(self, *args, **kwargs):
        self.slug = slugify(self.id)
        super(Rooms, self).save(*args, **kwargs)

    def __str__(self):
        if self.hall:
            return f'{self.hall} - Sala {self.name}'
        return f'{self.building} - Sala {self.name}'


    class Meta:
        verbose_name_plural = "Salas"
        verbose_name = "Sala"
        ordering = ['building', 'name']
        
class Shelf (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome da Prateleira", max_length=100)
    building = models.ForeignKey('inventory_management.Building', on_delete=models.CASCADE, verbose_name="Depósito")
    hall = models.ForeignKey('inventory_management.Hall', on_delete=models.CASCADE, verbose_name="Corredor")
    room = models.ForeignKey('inventory_management.Rooms', on_delete=models.CASCADE, verbose_name="Sala")
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='shelf_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='shelf_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def clean(self):
        if self.building.has_shelf == False:
            raise ValidationError("Esse prédio não possui prateleiras.")
        if self.hall and self.building.has_hall == False:
            raise ValidationError("Esse prédio não possui corredores.")
        if self.room and self.building.has_room == False:
            raise ValidationError("Esse prédio não possui salas.")

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

class StorageType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Nome do Local", max_length=100)
    slug = models.SlugField("Slug", max_length=100, blank=True, null=True, editable=False)
    created_by = models.ForeignKey('auth.User', verbose_name=_('Criado por'), on_delete=models.CASCADE, related_name='destinations_created_by', null=True, editable=False)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True, null=True, editable=False)
    updated_by = models.ForeignKey('auth.User', verbose_name=_('Atualizado por'), on_delete=models.CASCADE, related_name='destinations_updated_by', null=True, editable=False)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(StorageType, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tipos de Depósito"	
        verbose_name = "Tipo de Depósito"
        

class WorkSpace(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Usuário")
    product = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, verbose_name="Unidade de Produto")
    
    def __str__(self):
        return f'{self.user} - {self.product}'
    
    class Meta:
        verbose_name_plural = "Áreas de Trabalho"
        verbose_name = "Área de Trabalho"
    
