from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Client, Product, Provider, Group, Invoice, Bank, Expense, Stock, Price_change, Income, Expense_item,\
    Retail, Contract, Country
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        return data

class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    bank = BankSerializer()
    class Meta:
        model = Client
        fields = '__all__'


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientDetailSerializer(serializers.ModelSerializer):
    bank = BankSerializer()

    class Meta:
        model = Client
        fields = '__all__'




class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    product_group = GroupSerializer()
    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'


class ProductDetailsSerializer(serializers.ModelSerializer):
    product_group = GroupSerializer()

    class Meta:
        model = Product
        fields = '__all__'





class BankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = '__all__'

class ProviderSerializer(serializers.ModelSerializer):
    bank = BankSerializer()

    class Meta:
        model = Provider
        fields = '__all__'


class ProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'



class ProviderDetailSerializer(serializers.ModelSerializer):
    bank = BankSerializer()
    class Meta:
        model = Provider
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    providers = ProviderSerializer()
    class Meta:
        model = Invoice
        fields = '__all__'






class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'







class StockSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = Stock
        fields = '__all__'



class StockCreateSerializer(serializers.ModelSerializer):
    #product = ProductSerializer() #в пост только ID но в PATCH полный список
    class Meta:
        model = Stock
        fields = '__all__'





class StockDetailSerializer(serializers.ModelSerializer):
    #Вывод всех продуктов в GET запросе
    product = ProductSerializer()
    #invoice = InvoiceSerializer()

    class Meta:
        model = Stock
        fields = '__all__'






class IncomeSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    invoice = InvoiceSerializer()

    class Meta:
        model = Income
        fields = '__all__'




class IncomeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Income
        fields = '__all__'





class IncomeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Income
        fields = '__all__'


class Price_changeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price_change
        fields = '__all__'



class Price_changeDetailSerializer(serializers.ModelSerializer):  #Чтобы в GET запросе был выведен весь список
    product = ProductSerializer()
    income = IncomeSerializer()


    class Meta:
        model = Price_change
        fields = '__all__'


class Price_changeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price_change
        fields = '__all__'




class ExpenseSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    class Meta:
        model = Expense
        fields = '__all__'




class ExpenseCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = '__all__'



class ExpenseDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = Expense
        fields = '__all__'






class Expense_itemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense_item
        fields = '__all__'

class Expense_itemDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    group = GroupSerializer()
    expense = ExpenseSerializer()


    class Meta:
        model = Expense_item
        fields = '__all__'

class Expense_itemCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense_item
        fields = '__all__'










class RetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Retail
        fields = '__all__'



class RetailCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Retail
        fields = '__all__'


class RetailDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    group = GroupSerializer()

    class Meta:
        model = Retail
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = '__all__'


class ContractCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = '__all__'


class ContractDetailSerializer(serializers.ModelSerializer):
    client = ClientSerializer()           #get запрос выдает весь список, post - только ID
    class Meta:
        model = Contract
        fields = '__all__'




class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'








