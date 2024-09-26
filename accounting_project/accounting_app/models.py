from django.db import models
from django.core.exceptions import ValidationError

class Client(models.Model):
    #Клиент справочник
    client_name = models.CharField("Название клиента", max_length=255, blank=False)
    client_phone = models.CharField("Номер телефона", max_length=15, blank=True, null=True)
    client_address = models.CharField("Адрес", max_length=255)
    client_unp = models.CharField("УНП", max_length=150)
    client_payment_code = models.CharField("Код платежа", max_length=255)
    bank = models.ForeignKey('Bank', on_delete=models.CASCADE, verbose_name="Банк")
    client_comment = models.TextField("Комментарий", blank=True, null=True)


    class Meta:
         verbose_name = "Клиент"
         verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.client_name





class Provider(models.Model):
    #Поставщик справочник
    provider_name = models.CharField("Название поставщика", max_length=255)
    provider_phone = models.CharField("Номер телефона", max_length=25)
    provider_address = models.CharField("Адрес", max_length=255)
    provider_unp = models.CharField("УНП", max_length=255)
    provider_payment_code = models.CharField("Код платежа", max_length=255)
    bank = models.ForeignKey('Bank', on_delete=models.CASCADE, verbose_name="Банк")
    provider_comment = models.TextField("Комментарий", blank=True, null=True)


    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.provider_name



class Product(models.Model):
    #Продукты(товар) справочник
    product_name = models.CharField("Название", max_length=255)
    product_group = models.ForeignKey('Group', on_delete=models.PROTECT, blank=True, null=True, verbose_name="Группа")
    product_unit = models.CharField("Единица измерения", max_length=10)

    # Перераспределили метод delete чтоб удалял товар только тогда, когда есть он в других таблицах, иначе - удалить
    def delete(self, *args, **kwargs):
        if (self.income_set.exists() or
                self.price_change_set.exists() or
                self.expense_item_set.exists() or
                self.retail_set.exists() or
                self.stock_set.exists()):
            raise ValidationError("Товар нельзя удалить, так как он связан с другими записями.")
        else:
            super(Product, self).delete(*args, **kwargs)





    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.product_name



class Group(models.Model):
    #Группы справочник
    group_name = models.CharField("Название группы", max_length=100)
    group_level = models.CharField("Уровень раздела", max_length=100, blank=True, null=True)
    group_chapter = models.CharField("Подраздел группы", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.group_name



class Invoice(models.Model):
    #Накладная прихода
    providers = models.ForeignKey('Provider', on_delete=models.CASCADE, verbose_name="Поставщик")
    invoice_number = models.CharField("Номер накладной", max_length=100)
    product_date = models.DateField("Дата поступления ", blank=False)
    product_price = models.CharField("Цена по накладной", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    product_price_nds = models.CharField("Цена с НДС", max_length=100)



    class Meta:
        verbose_name = "Накладная"
        verbose_name_plural = "Накладные"

    def __str__(self):
        return f"id : {self.id} / накладная № #{self.invoice_number} "


class Price_change(models.Model):
    #Изменение цены (корректировка)
    income = models.ForeignKey('Income', on_delete=models.CASCADE, verbose_name="Накладная")
    old_income = models.CharField("Старая накладная", max_length=100, blank=True, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    price_change_date = models.CharField("Дата изменения цены", max_length=100)
    expense_sale_price = models.CharField("Старая цена со склада", max_length=100)
    price_change_new = models.CharField("Новая цена", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    quantity = models.CharField("Количество", blank=True, null=True, max_length=100)

    class Meta:

        verbose_name = "Изменение цены"
        verbose_name_plural = "Изменение цены"

    def __str__(self):
        return str(self.product)




class Income(models.Model):
    #Приход
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, verbose_name="Накладная")
    stock = models.ForeignKey('Stock', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Склад")
    product_vendor_providers = models.CharField("Артикул товара поставщика ", max_length=100, blank=True, null=True)
    income_quantity = models.CharField("Количество",  max_length=255)
    product_country = models.CharField("Страна товара", max_length=255)
    product_barcode = models.CharField("Штрихкод товара", max_length=255)
    income_purchase_price = models.CharField("Закупочная цена", max_length=100)
    income_price = models.CharField("Стоимость зак. цена * количество", max_length=100)
    income_vat = models.CharField("НДС", max_length=255)
    income_total_vat = models.CharField("Сумма НДС", max_length=100)
    income_total_price_vat = models.CharField("Полная цена с ндс", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    income_allowance = models.CharField("Надбавка", max_length=100)



    class Meta:
        verbose_name = "Приход"
        verbose_name_plural = "Приходы"

    def __str__(self):
        return f"Получили товар :{self.product} в количестве {self.income_quantity} "





class Expense(models.Model):
    #Расход
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name="Клиент")
    expense_number = models.CharField("Номер по накладной", max_length=100)
    expense_contract = models.CharField("Номер договора", max_length=100, blank=True, null=True)
    expense_price = models.CharField("Стоимость", max_length=100)
    expense_price_allowance = models.CharField("Стоимость с надбавкой", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    expense_vat = models.CharField("Сумма НДС ", max_length=100, blank=True, null=True)
    expense_date = models.DateField("Дата продажи",  blank=False)
    number_proxy = models.CharField("Номер доверенности", max_length=100, blank=True, null=True)
    date_proxy = models.CharField("Дата доверенности", max_length=100, blank=True, null=True)
    proxy_user = models.CharField("Кем выдана довереннось", max_length=100, blank=True, null=True)
    expense_print = models.CharField("Печатана ли накладная", max_length=100, blank=True, null=True)



    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"

    def __str__(self):
        return f"Продано кому: {self.client}  "

class Expense_item(models.Model):
    #Расходная продажи
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    expense = models.ForeignKey('Expense', on_delete=models.CASCADE, verbose_name="Расходная накладная")
    product_vendor = models.CharField("Артикул товара", max_length=100)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Группа")
    price_allowance = models.CharField("Цена с надбавкой", max_length=100)
    price_mult_quant = models.CharField("Стоимость", max_length=100)
    product_quantity = models.CharField("Количество товара для продажи", max_length=100)
    amount_vat = models.CharField("Сумма НДС", max_length=100)
    price_with_vat = models.CharField("Стоимость с НДС", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    product_vat = models.CharField("НДС", max_length=20)
    product_allowance = models.CharField("Надбавка", max_length=100, blank=True, null=True)
    product_country = models.CharField("Страна товара", max_length=100)
    product_barcode = models.CharField("Штрихкод товара", max_length=100)
    product_discount = models.CharField("Скидка", max_length=100, blank=True, null=True)
    product_stock = models.CharField("Склад", max_length=100, blank=True, null=True)
    note = models.CharField("Примечание", max_length=100, blank=True, null=True)
    recovery = models.BooleanField("Возврат", default=False, blank=True, null=True)
    quantity_recov = models.CharField("Количесвто возврата",max_length=100, blank=True, null=True)



    class Meta:

        verbose_name = "Расходная продажи"
        verbose_name_plural = "Расходная продажи"

    def __str__(self):
        return str(self.product)





class Retail(models.Model):
    #Розничная торговля
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    group = models.ForeignKey('Group', on_delete=models.CASCADE, verbose_name="Группа")
    product_vendor = models.CharField("Артикул товара", max_length=100)
    product_country = models.CharField("Страна товара", max_length=100)
    product_barcode = models.CharField("Штрихкод товара", max_length=100)
    product_vat = models.CharField("НДС", max_length=20)
    product_extra = models.CharField("Надбавка", max_length=100)
    product_quantity = models.CharField("Количество товара", max_length=100)
    total_price_vat = models.CharField("Общая цена с НДС", max_length=100)
    full_price = models.CharField("Общая цена с ндс и надбавкой", max_length=100)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    date_item = models.DateField("Дата выставления чека")
    #paymant оплата картой или наличными добавить


    class Meta:

        verbose_name = "Розничная торговля"
        verbose_name_plural = "Розничная торговля"

    def __str__(self):
        return str(self.product)





class Bank(models.Model):
    #Банк справочник
    bank_name = models.CharField("Название банка", max_length=255)
    bank_bik = models.CharField("БИК банка", max_length=25)


    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"

    def __str__(self):
        return self.bank_name


class Contract(models.Model):
    #Договор
    client = models.ForeignKey('Client', on_delete=models.CASCADE, verbose_name="Kлиент")
    contract_number = models.CharField("Номер договора", max_length=100)
    contract_date = models.DateField("Дата договора")


    class Meta:
        verbose_name = "Договор"
        verbose_name_plural = "Договора"

    def __str__(self):
        return f"Номер договора: {self.contract_number} "



class Stock(models.Model):
    #Склад
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    product_quantity = models.CharField("Количество товара", max_length=255)
    product_country = models.CharField("Страна товара", max_length=255)
    product_vendor = models.CharField("Артикул товара", max_length=255)
    product_reserve = models.CharField("Резерв товара", max_length=255)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, verbose_name="Группа", blank=True, null=True)
    product_price_provider = models.CharField("Цена с надбавкой", max_length=255)
    expense_allowance = models.CharField("Надбавка", max_length=100)
    product_price = models.CharField("Цена", max_length=255)
    currency = models.CharField("Валюта", max_length=100, blank=True, null=True)
    product_vat = models.CharField("НДС", max_length=255)
    expense_full_price = models.CharField("Общая цена с ндс", max_length=250, null=True, blank=True)
    product_barcode = models.CharField("Штрихкод", max_length=255)


    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склад"

    def __str__(self):
        return f" id {self.id} - {self.product} - количество {self.product_quantity} шт "





class Country(models.Model):
    country_name = models.CharField("Hазвание страны", max_length=100)


    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"

    def __str__(self):
         return self.country_name




