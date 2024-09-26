from django.contrib import admin
from .models import Product, Client, Provider, Group, Invoice, Bank, Expense, Stock, Price_change, Income, Retail, \
    Expense_item, Contract, Country



admin.site.register(Product)
admin.site.register(Provider)
admin.site.register(Client)
admin.site.register(Group)
admin.site.register(Invoice)
admin.site.register(Bank)
admin.site.register(Expense)
admin.site.register(Stock)
admin.site.register(Price_change)
admin.site.register(Income)
admin.site.register(Retail)
admin.site.register(Expense_item)
admin.site.register(Contract)
admin.site.register(Country)

