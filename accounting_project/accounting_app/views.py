from django.db import transaction
from django.db.models import Q
from rest_framework import viewsets, filters
from django.http import Http404
from .paginations import *
from rest_framework.decorators import action
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
import re
from django.db.models.functions import Lower
from collections import defaultdict


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer




class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all().order_by('-id')
    serializer_class = ProviderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['provider_name'] #?search
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):          #сериализатор для POST и PATCH-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return ProviderCreateSerializer
        elif self.request.method == 'PATCH':
            return ProviderCreateSerializer
        return ProviderSerializer



     #Еслли в накладой есть поставщик - TRUE, иначе FALSE
     # /api/providers/5/check_invoice
    @action(detail=True, methods=['GET'])
    def check_invoice(self, request, pk=None):
        providers = self.get_object()
        invoice_exists = providers.invoice_set.exists()
        return Response({'exists': invoice_exists})

    # Поиск поставшика по букве в независимости от регистра и сортировка 5 по ID
    # api/providers/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '').strip()

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if query:  # Если запрос не пустой, фильтруем записи по нему
            providers = Provider.objects.filter(provider_name__iregex=query).order_by('-id')
        else:
            # Если запрос пустой, выводим все записи
            providers = Provider.objects.all().order_by('-id')

        # Применяем пагинацию к результатам
        paginated_providers = paginator.paginate_queryset(providers, request)

        serializer = ProviderSerializer(paginated_providers, many=True)
        return paginator.get_paginated_response(serializer.data)






class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-id')
    serializer_class = InvoiceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['invoice_number', 'provider__provider_name']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]




    def get_serializer_class(self):          #сериализатор для POST и PATCH-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return InvoiceCreateSerializer
        elif self.request.method == 'PATCH':
            return InvoiceCreateSerializer
        return InvoiceSerializer




    # Поиск с даты по дату по двум параметрам + пагинация
    # http://127.0.0.1:8000/api/invoices/?date=min (max)
    def get_queryset(self):
        queryset = super().get_queryset()

        # Получаем параметр order_by из запроса
        order_by = self.request.query_params.get('date', None)

        # Сортируем записи в зависимости от параметра order_by
        if order_by == 'min':
            # Если указан date=min, сортируем по возрастанию
            queryset = queryset.order_by('product_date')
        elif order_by == 'max':
            # Если указан date=max, сортируем по убыванию
            queryset = queryset.order_by('-product_date')

        return queryset





    # Поиск invoice по invoice_number в независимости от регистра и сортировка 5 по ID
    # api/invoices/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '')

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            invoices = Invoice.objects.all().order_by('-id')  # Возвращает все записи, если 'name' не задан
        else:
            invoices = Invoice.objects.filter(invoice_number__iregex=query).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_invoices = paginator.paginate_queryset(invoices, request)

        serializer = InvoiceSerializer(paginated_invoices, many=True)
        return paginator.get_paginated_response(serializer.data)





class ClientViewSet(viewsets.ModelViewSet):  #справочник
    queryset = Client.objects.all().order_by('-id')
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['client_name']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]


    def get_serializer_class(self):          #сериализатор для POST и PATCH-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return ClientCreateSerializer
        elif self.request.method == 'PATCH':
            return ClientCreateSerializer
        return ClientSerializer


    # Поиск клиента по букве в независимости от регистра и сортировка 5 по ID
    # api/clients/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', ' ').strip()


        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            clients = Client.objects.all().order_by('-id')  # Возвращает все записи, если 'name' не задан
        else:
            clients = Client.objects.filter(client_name__iregex=query).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_clients = paginator.paginate_queryset(clients, request)

        serializer = ClientSerializer(paginated_clients, many=True)
        return paginator.get_paginated_response(serializer.data)






class ProductViewSet(viewsets.ModelViewSet):  #справочник
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['product_name']  #?search=AAAA
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]




    def get_serializer_class(
            self):  # сериализатор для POST и PATCH-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return ProductCreateSerializer
        elif self.request.method == 'PATCH':
            return ProductCreateSerializer
        return ProductSerializer

    # Поиск записей по id группы и поиск по названии товара из этой категории товаров
    # http://127.0.0.1:8000/api/products/search/?group_id=&product_name=apple
    @action(detail=False, methods=['get'])
    def search(self, request):
        group_id = request.query_params.get('group_id')
        product_name = request.query_params.get('product_name', '')

        if not group_id:
            return Response({"error": "Group ID is required."}, status=400)

        products = self.queryset.filter(
            product_group_id=group_id,
            product_name__iregex=product_name  # __icontains для поиска без учета регистра
        )

        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    # Поск по продуктам если запись group_chapter соответсвтует id группы то и выводим эти записи
    # http://127.0.0.1:8000/api/products/search_product_by_name/?product_name=apple
    @action(detail=False, methods=['get'])
    def search_product_by_name(self, request):
        product_name = request.query_params.get('product_name', None)
        if product_name is not None:
            try:
                products = Product.objects.filter(product_name__iregex=product_name)
                grouped_data = {}
                for product in products:
                    group = product.product_group
                    key = (group.id, group.group_name, group.group_level, group.group_chapter)
                    if key not in grouped_data:
                        grouped_data[key] = {'group_id': group.id,
                                             'group_name': group.group_name,
                                             'group_level': group.group_level,
                                             'group_chapter': group.group_chapter,
                                             'product_names': [product.product_name]}
                    else:
                        grouped_data[key]['product_names'].append(product.product_name)

                response_data = list(grouped_data.values())

                # Дополнительно добавляем записи, где group_chapter совпадает с id группы
                for group_id, group_data in grouped_data.items():
                    if str(group_id[0]) == group_data['group_chapter']:
                        products = Product.objects.filter(product_group=group_id[0])
                        for product in products:
                            if product.product_name not in group_data['product_names']:
                                group_data['product_names'].append(product.product_name)

                # Если group_chapter соответствует id группы, добавляем эту группу в ответ
                for group_data in response_data:
                    if group_data['group_chapter'] in [str(group['group_id']) for group in response_data]:
                        group_id = int(group_data['group_chapter'])
                        group = Group.objects.get(id=group_id)
                        if group_data['product_names'] == []:
                            group_products = Product.objects.filter(product_group=group_id)
                            group_data['product_names'] = [product.product_name for product in group_products]

                # Добавляем группы, где id совпадает с group_chapter
                group_chapters = set(group['group_chapter'] for group in response_data)
                for group_chapter in group_chapters:
                    try:
                        if group_chapter and group_chapter != '-':  # Добавлены дополнительные проверки
                            group = Group.objects.get(id=group_chapter)
                            group_data = {
                                'group_id': group.id,
                                'group_name': group.group_name,
                                'group_level': group.group_level,
                                'group_chapter': group.group_chapter,
                                'product_names': [product.product_name for product in
                                                  Product.objects.filter(product_group=group.id)]
                            }
                            if group_data not in response_data:
                                response_data.append(group_data)
                    except (Group.DoesNotExist, ValueError):  # Обрабатываем исключение, если id не является числом
                        pass

                # Делаем пагинацию
                paginator = PageNumberPagination()
                # Получаем количество записей на странице из параметра запроса, по умолчанию 5
                page_size = int(request.query_params.get('page_size', 5))
                paginator.page_size = page_size
                result_page = paginator.paginate_queryset(response_data, request)

                return paginator.get_paginated_response(result_page)
            except Product.DoesNotExist:
                return Response({'error_message': 'Product does not exist'}, status=404)
        else:
            return Response({'error_message': 'Product name parameter is required'}, status=400)





    # Поиск товара по букве в независимости от регистра и сортировка 5 по ID
    # api/products/search_by_name/?name=
    # если в название товара много пробелов а в поиске пишем один пробел то работает!
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '').strip()

        # Экранируем специальные символы в запросе
        escaped_query = re.escape(query)

        # Нормализуем пробелы в запросе
        normalized_query = ' '.join(escaped_query.split())

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            products = Product.objects.all().order_by('-id')  # Возвращает все записи, если 'name' не задан
        else:
            # Нормализуем пробелы в именах продуктов и фильтруем их
            products = Product.objects.annotate(
                normalized_name=Replace(
                    Replace(
                        Replace('product_name', Value('  '), Value(' ')),
                        Value('  '), Value(' ')
                    ),
                    Value('  '), Value(' ')
                )
            ).filter(
                normalized_name__iregex=normalized_query
            ).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)


    # Фильтрация по product_name, group_name
    # /api/products/filter_products/?sort=product_name  /  group_name  / group_id
    @action(detail=False, methods=['GET'])
    def filter_products(self, request, *args, **kwargs):
        product_name = self.request.query_params.get('product_name', None)
        product_group = self.request.query_params.get('product_group', None)
        sort_by = self.request.query_params.get('sort', None)

        queryset = self.get_queryset()

        if product_name:
            queryset = queryset.filter(product_name__icontains=product_name)

        if product_group:
            queryset = queryset.filter(product_group__group_name__icontains=product_group)

        if sort_by:
            if sort_by == 'product_name':
                queryset = queryset.order_by('product_name')
            elif sort_by == 'group_name':
                queryset = queryset.order_by('product_group__group_name')

        # Добавляем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        # Создаем пагинированный объект с вашими данными
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)



    # Поиск товара по id группы
    # api/products/search_by_id/?id=
    @action(detail=False, methods=['GET'])
    def search_by_id(self, request):
        query = request.query_params.get('id', '').strip()

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            products = Product.objects.all().order_by('-id')  # Возвращает все записи, если 'id' не задан
        else:
            products = Product.objects.filter(product_group__id=query).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)





class GroupViewSet(viewsets.ModelViewSet): #справочник
    queryset = Group.objects.all().order_by('-id')
    serializer_class = GroupSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id']   #?search=AAAA
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]



    # Запрос на вывод всех записей таблицы Group без пагинации
    # http://127.0.0.1:8000/api/groups/get_all_groups/
    @action(detail=False, methods=['GET'])
    def get_all_groups(self, request):
        groups = self.get_queryset()
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)

    # Поиск по названию в независимости от регистра и сортировка 5 по ID + поиск по group+chapter
    # http://127.0.0.1:8000/api/groups/search_by_name/?name=   / chapter=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        name_query = request.query_params.get('name', '').strip()
        chapter_query = request.query_params.get('chapter', '').strip()

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        # Получаем группы, отсортированные по названию в алфавитном порядке (в нижнем регистре)
        groups = Group.objects.annotate(
            lowercase_group_name=Lower('group_name')
        ).order_by('lowercase_group_name')

        if name_query:
            groups = groups.filter(lowercase_group_name__iregex=name_query)

        if chapter_query:
            groups = groups.filter(group_chapter__iregex=chapter_query)

        # Применяем пагинацию к результатам
        paginated_groups = paginator.paginate_queryset(groups, request)

        serializer = GroupSerializer(paginated_groups, many=True)
        return paginator.get_paginated_response(serializer.data)

    # Поиск записей где group_level=1 ( 1 = True, 0 = False)
    # http://127.0.0.1:8000/api/groups/filter_by_group_level/?group_level=1
    @action(detail=False, methods=['get'])
    def filter_by_group_level(self, request):
        group_level = request.query_params.get('group_level', None)

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        queryset = self.get_queryset()

        # Если указан параметр group_level, фильтруем по нему
        if group_level is not None:
            group_level = int(group_level)
            if group_level not in [0, 1]:
                return Response({"detail": "Неверное значение параметра group_level. Используйте 0 или 1."}, status=400)

            queryset = queryset.filter(group_level=group_level)

        # Сортировка по алфавиту в поле group_name без учёта регистра
        queryset = queryset.order_by(Lower('group_name'))

        # Применяем пагинацию к результатам
        paginated_groups = paginator.paginate_queryset(queryset, request)

        serializer = GroupSerializer(paginated_groups, many=True)
        return paginator.get_paginated_response(serializer.data)


    # Поиск по group_chapter по точному значению числовому
    # http://127.0.0.1:8000/api/groups/search_by_group_chapter/?chapter=1
    @action(detail=False, methods=['GET'])
    def search_by_group_chapter(self, request):
        chapter_query = request.query_params.get('chapter', '').strip()

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size
        groups = Group.objects.all().order_by('-id')
        if chapter_query:
            groups = groups.filter(group_chapter=chapter_query)

        # Применяем пагинацию к результатам
        paginated_groups = paginator.paginate_queryset(groups, request)
        serializer = GroupSerializer(paginated_groups, many=True)
        return paginator.get_paginated_response(serializer.data)

    # Сделать если имя полностью совпадает с group_name выводим - TRUE, если не совпадает - FALSE
    # http://127.0.0.1:8000/api/groups/check_group_name/?group_name=овощи
    @action(detail=False, methods=['get'])
    def check_group_name(self, request):
        group_name = request.query_params.get('group_name', '').strip()

        if not group_name:
            return Response({'error': 'Имя группы не указано'}, status=status.HTTP_400_BAD_REQUEST)

        group_exists = Group.objects.filter(group_name__iregex=group_name).exists()

        return Response({'group_exists': group_exists})





class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    queryset = Income.objects.all().order_by('-id')
    filter_backends = [filters.SearchFilter]
    search_fields = [] #?search=AAAA
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]



    def get_serializer_class(
            self):  # сериализатор для POST и PACT-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return IncomeCreateSerializer
        elif self.request.method == 'PATCH':
            return IncomeCreateSerializer
        return IncomeSerializer





    # Поиск с даты по дату по двум параметрам + пагинация
    # http://127.0.0.1:8000/api/incomes/?date=min (max))?
    def get_queryset(self):
        queryset = super().get_queryset()

        # Получаем параметр order_by из запроса
        order_by = self.request.query_params.get('date', None)

        # Сортируем записи в зависимости от параметра order_by
        if order_by == 'min':
            # Если указан date=min, сортируем по возрастанию
            queryset = queryset.order_by('invoice__product_date')
        elif order_by == 'max':
            # Если указан date=max, сортируем по убыванию
            queryset = queryset.order_by('-invoice__product_date')

        return queryset




     # Поиск получить где параметрами будут : 1) даты с по, 2) дата с по + клиент, 3) дата с по + товар, 4)дата с по + клиент + товар
     # api/incomes/filter_by_income/?start_date=2023-01-01&end_date=2023-12-31&providers_id=2&product_id=1
    @action(detail=False, methods=['get'])
    def filter_by_income(self, request):
        queryset = self.get_queryset()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        provider_id = request.query_params.get('providers_id')
        product_id = request.query_params.get('product_id')

        filters = Q()

        if start_date and end_date:
            filters &= Q(invoice__product_date__range=(start_date, end_date))
        elif start_date:
            filters &= Q(invoice__product_date__gte=start_date)
        elif end_date:
            filters &= Q(invoice__product_date__lte=end_date)

        if provider_id:
            filters &= Q(invoice__providers_id=provider_id)

        if product_id:
            filters &= Q(product_id=product_id)

        queryset = queryset.filter(filters)

        serializer = IncomeSerializer(queryset, many=True)
        return Response(serializer.data)




    # Поиск income по invoice_id от даты и по дату
    # api/incomes/filter_by_date_and_invoice/?invoice_id=476&start_date=2023-11-01&end_date=2023-12-31
    @action(detail=False, methods=['GET'])
    def filter_by_date_and_invoice(self, request):
        queryset = self.get_queryset()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))

        invoice_id = request.query_params.get('invoice_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if invoice_id:
            queryset = queryset.filter(invoice__id=invoice_id)

        if start_date:
            queryset = queryset.filter(invoice__product_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(invoice__product_date__lte=end_date)

        # Делаем пагинацию
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)




    # Поиск income по product_name от даты и по дату
    # api/incomes/filter_by_date_and_product_name/?product_name=476&start_date=2023-11-01&end_date=2023-12-31
    @action(detail=False, methods=['GET'])
    def filter_by_date_and_product_name(self, request):
        queryset = self.get_queryset()

        product_name = request.query_params.get('product_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if product_name:
            queryset = queryset.filter(product__product_name__iregex=product_name)

        if start_date:
            queryset = queryset.filter(invoice__product_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(invoice__product_date__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)






class BankViewSet(viewsets.ModelViewSet): #справочник
    queryset = Bank.objects.all().order_by('-id')
    serializer_class = BankSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['bank_name']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]



    # Поиск банка по букве в независимости от регистра и сортировка 5 по ID
    # api/banks/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '').strip()
        #strip Добавили чтобы при вводе пробела (%20) выводило всю строку

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            banks = Bank.objects.all().order_by('-id')  # Возвращает все записи, если 'name' не задан
        else:
            banks = Bank.objects.filter(bank_name__iregex=query).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_banks = paginator.paginate_queryset(banks, request)

        serializer = BankSerializer(paginated_banks, many=True)
        return paginator.get_paginated_response(serializer.data)




class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-id')
    serializer_class = ExpenseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(
            self):  # сериализатор для POST и PATCH-запросов (GET показывает весь список, POST оставляет ID ключа другой таблицы)
        if self.request.method == 'POST':
            return ExpenseCreateSerializer
        elif self.request.method == 'PATCH':
            return ExpenseCreateSerializer
        return ExpenseSerializer



    # Поиск expense по expense_number букве в независимости от регистра и сортировка 5 по ID
    # api/expenses/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '')

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            expenses = Expense.objects.all().order_by('-id')  # Возвращает все записи, если 'name' не задан
        else:
            expenses = Expense.objects.filter(expense_number__iregex=query).order_by('-id')

        # Применяем пагинацию к результатам
        paginated_expenses = paginator.paginate_queryset(expenses, request)

        serializer = ExpenseSerializer(paginated_expenses, many=True)
        return paginator.get_paginated_response(serializer.data)





class Expense_itemViewSet(viewsets.ModelViewSet):
    queryset = Expense_item.objects.all().order_by('-id')
    serializer_class = Expense_itemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return Expense_itemCreateSerializer  #сериализатор для POST-запросов (GET показывает весь список, POST оставляет ID)
        return Expense_itemDetailSerializer




    # Поиск расхода по id_накладной расхода
    # api/expenses_item/?expense_id=1
    def get_queryset(self):
        expense_id = self.request.query_params.get('expense_id')
        if expense_id:
            return Expense_item.objects.filter(expense_id=expense_id)
        return super().get_queryset()



    # Поиск по параметрам : 1) даты с по, 2) дата с по + клиент, 3) дата с по + товар, 4)дата с по + клиент + товар
    # filter_by_expense_item/?start_date=2023-01-01&end_date=2023-12-31&client_id=10&product_id=94
    @action(detail=False, methods=['get'])
    def filter_by_expense_item(self, request):
        queryset = self.get_queryset()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        client_id = request.query_params.get('client_id')
        product_id = request.query_params.get('product_id')

        if start_date:
            queryset = queryset.filter(expense__expense_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(expense__expense_date__lte=end_date)

        if client_id:
            queryset = queryset.filter(expense__client__id=client_id)

        if product_id:
            queryset = queryset.filter(product__id=product_id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



    # Поиск expense_item по product_name от даты и по дату
    # expenses_item/filter_by_date_and_product_name/?product_name=476&start_date=2023-11-01&end_date=2023-12-31
    @action(detail=False, methods=['GET'])
    def filter_by_date_and_product_name(self, request):
        queryset = self.get_queryset()

        product_name = request.query_params.get('product_name')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if product_name:
            queryset = queryset.filter(product__product_name__iregex=product_name)

        if start_date:
            queryset = queryset.filter(expense__expense_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(expense__expense_date__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Поиск expense по товару без учеба регистра в таблице expense_item
    @action(detail=False, methods=['get'])
    def expenses_by_product(self, request):
        product_name = request.query_params.get('product_name')

        # Если product_name пустой или не определен, вернуть все записи
        if not product_name:
            expenses = Expense.objects.all()
        else:
            expense_items = Expense_item.objects.filter(product__product_name__iregex=product_name)
            if not expense_items:
                return Response({'error': 'No expense items found for the provided product name'}, status=404)

            expenses = Expense.objects.filter(expense_item__in=expense_items)

        page = self.paginate_queryset(expenses)
        if page is not None:
            serializer = ExpenseSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        expense_serializer = ExpenseSerializer(expenses, many=True)
        return Response(expense_serializer.data)





# Замена строк где есть одинаковые параметры ввода и обновление последневведенных +
# замена id обновленного stock в таблицу income

class UpdateStock(APIView):
    """ Объединение записей """

    def post(self, request, prod_id):
        try:
            prod = Stock.objects.get(pk=prod_id)
        except Stock.DoesNotExist:
            raise Http404("Товар не существует")

        with transaction.atomic():
            # Находим все записи с заданными параметрами товаров
            existing_stocks = Stock.objects.filter(
                product_id=prod.product_id,
                product_price=prod.product_price,
                product_country=prod.product_country,
                product_vendor=prod.product_vendor
            ).exclude(product_barcode="").order_by('id')

            # Если единственная запись - это исходная запись, возвращаем ее без изменений
            if existing_stocks.count() == 1 and existing_stocks.first().id == prod.id:
                return Response({
                    "message": "Only one stock found. No merge needed.",
                    "new_stock": {"id": prod.id},
                    "merged_stocks": []
                })

            if existing_stocks.exists():
                # Проверяем, что не существует уже объединенной записи для данной группы товаров
                existing_merged_stock = Stock.objects.filter(
                    product_id=prod.product_id,
                    product_price=prod.product_price,
                    product_country=prod.product_country,
                    product_vendor=prod.product_vendor,
                    product_barcode__isnull=False
                ).exclude(id__in=existing_stocks).first()

                if not existing_merged_stock:
                    # Создаем список для объединения всех найденных записей
                    stocks_to_merge = existing_stocks

                    earliest_barcode = min(stock.product_barcode for stock in stocks_to_merge)

                    # Вычисляем суммы для объединения
                    total_expense_full_price = sum(float(stock.expense_full_price) for stock in stocks_to_merge)
                    total_product_quantity = sum(int(stock.product_quantity) for stock in stocks_to_merge)

                    # Проверяем количество товара
                    if total_product_quantity == 0:
                        # Если количество равно 0, сохраняем значение stock
                        last_deleted_stock = stocks_to_merge.first().id

                        # Удаляем все объединенные записи, кроме последней
                        stocks_to_merge.exclude(id=last_deleted_stock).delete()

                        # Удаление из модели Income связанных записей с удаленными Stock
                        Income.objects.filter(stock=last_deleted_stock).delete()
                    else:
                        # Создаем новую запись Stock с общими значениями
                        new_stock = Stock.objects.create(
                            product_id=prod.product_id,
                            product_price=prod.product_price,
                            product_country=prod.product_country,
                            product_vendor=prod.product_vendor,
                            product_reserve=prod.product_reserve,
                            product_price_provider=prod.product_price_provider,
                            expense_allowance=prod.expense_allowance,
                            product_vat=prod.product_vat,
                            product_barcode=earliest_barcode,
                            expense_full_price=str(total_expense_full_price),
                            product_quantity=str(total_product_quantity)
                        )

                        # Обновляем связанные записи в модели Income
                        Income.objects.filter(stock__in=stocks_to_merge).update(stock_id=new_stock.id)

                        # Удаляем все объединенные записи, кроме новой
                        stocks_to_merge.exclude(id=new_stock.id).delete()

                        # Возвращаем информацию о новой записи и объединенных записях
                        merged_stocks_info = {
                            "new_stock": {"id": new_stock.id},
                            "merged_stocks": [{"id": stock.id} for stock in stocks_to_merge]
                        }
                        return Response(merged_stocks_info)

            # Если нет записей для объединения, возвращаем пустой ответ
            return Response({"message": "No identical stocks to merge."})


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all().order_by('-id')
    serializer_class = StockSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__product_name', 'product__id']  #?search=AAAA (имя товара / ID товара)
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Http404:
            return Response([])  # Возвращаем пустой массив, если объект не найден по ID


    def get_serializer_class(self):
        if self.action == 'create':
            return StockCreateSerializer  #сериализатор для POST-запросов (GET показывает весь список, POST оставляет ID)
        return StockDetailSerializer




    # Поиск с даты по дату + товар
    # filter_by_stock/?start_date=2023-01-01&end_date=2023-12-31&product_id=84
    @action(detail=False, methods=['get'])
    def filter_by_stock(self, request):
        queryset = self.get_queryset()

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        product_id = request.query_params.get('product_id')

        if start_date:
            queryset = queryset.filter(income__invoice__product_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(income__invoice__product_date__lte=end_date)

        if product_id:
            queryset = queryset.filter(product_id=product_id)


        serializer = StockSerializer(queryset, many=True)
        return Response(serializer.data)




    # Поиск товаров от одного до пяти слов и артикула. Список всех товаров связанных с первым словом +  список всех товаров с вторым словом и так далее
    # /api/stocks/filter_by_keyword/?query=рамка+дом+артикул+страна+имя группы

    @action(detail=False, methods=['GET'])
    def filter_by_keyword(self, request):
        query = request.query_params.get('query', '')
        country_filter = request.query_params.get('country', '')
        group_name_filter = request.query_params.get('group_name', '')

        queryset = Stock.objects.all().order_by('-id')

        # Проверка наличия условий фильтрации
        if query or country_filter or group_name_filter:
            # Экранирование слэшей в запросе
            escaped_query = query.replace('\\', '\\\\')
            keywords = escaped_query.split()
            query_filters = Q()

            # Построение фильтров для каждого ключевого слова
            for keyword in keywords:
                query_filters &= (Q(product__product_name__iregex=keyword) |
                                  Q(product_vendor__icontains=keyword) |
                                  Q(product_country__iregex=keyword) |
                                  Q(product__product_group__group_name__iregex=keyword))

            # Применение фильтров к запросу
            results = queryset.filter(query_filters)

            # Дополнительная фильтрация по стране
            if country_filter:
                results = results.filter(product_country__icontains=country_filter)

            # Дополнительная фильтрация по имени группы
            if group_name_filter:
                results = results.filter(product__product_group__group_name__icontains=group_name_filter)
        else:
            # Если условия фильтрации отсутствуют, использовать все объекты
            results = queryset

        # Пагинация результатов
        page = self.paginate_queryset(results)

        if page is not None:
            serializer = StockSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)




    # Поиск на складе по названию товара по любой букве без учета регистра
    # api/stocks/search_by_name/?name=а
    # Поиск по названию без учета регистра - iregex, если по любой букве - icontains
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        search_query = request.query_params.get('name', '')

        if not search_query:
            # Если запрос пуст, возвращает все строки
            stock = Stock.objects.all()
        else:
            # Поле, связанное с моделью Product для поиска по названию без учета регистра
            products = Product.objects.filter(product_name__iregex=search_query)
            stock = Stock.objects.filter(product__in=products)

        stock = stock.order_by('-product')[:25] #Упорядочиваем результаты по продукту в убывающем порядке

        if stock:
            serializer = StockSerializer(stock, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Товары не найдены'}, status=status.HTTP_404_NOT_FOUND)





    # Поиск на складе товара и группы по его ID
    # /api/stocks/search_by_product_id/?product_id=2 / ?group_id=1
    @action(detail=False, methods=['GET'])
    def search_by_product_id(self, request):
        product_id = request.query_params.get('product_id')
        group_id = request.query_params.get('group_id')

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        try:
            # Проверяем наличие параметров и строим фильтр соответственно
            if product_id and group_id:
                stocks = Stock.objects.filter(
                    Q(product__id=product_id) | Q(group__id=group_id)
                )
            elif product_id:
                stocks = Stock.objects.filter(product__id=product_id)
            elif group_id:
                stocks = Stock.objects.filter(group__id=group_id)
            else:
                # Если ни один из параметров не указан, выводим все записи
                stocks = Stock.objects.all()
        except Stock.DoesNotExist:
            return Response({"response": "false"}, status=status.HTTP_200_OK)

        # Применяем пагинацию к результатам
        paginated_queryset = paginator.paginate_queryset(stocks, request)

        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


    # Поиск на складе по точному количеству товара
    # api/stocks/search_by_quantity/?quantity=0
    @action(detail=False, methods=['GET'])
    def search_by_quantity(self, request):
        quantity = request.query_params.get('quantity')

        if quantity is not None:
            try:
                quantity = int(quantity)
                products_with_exact_quantity = Stock.objects.filter(product_quantity=quantity)
                serializer = StockSerializer(products_with_exact_quantity, many=True)
                return Response(serializer.data)
            except ValueError:
                return Response({'error': 'Некорректно введено количество товара. Укажите целое число'}, status=400)

    # Поиск товала по id группы и названию
    # http://127.0.0.1:8000/api/stocks/search_by_product_name_and_group/?product_name=пе&group_id=5
    @action(detail=False, methods=['GET'])
    def search_by_product_name_and_group(self, request):
        product_name = request.query_params.get('product_name')
        group_id = request.query_params.get('group_id')

        paginator = PageNumberPagination()
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        try:
            if product_name and group_id:
                stocks = Stock.objects.filter(
                    (Q(product__product_name__iregex=product_name) | Q(product_vendor__iregex=product_name)) &
                    Q(product__product_group__id=group_id)
                )
            elif product_name:
                stocks = Stock.objects.filter(
                    Q(product__product_name__iregex=product_name) | Q(product_vendor__iregex=product_name)
                )
            elif group_id:
                stocks = Stock.objects.filter(product__product_group__id=group_id)
            else:
                stocks = Stock.objects.all()
        except Stock.DoesNotExist:
            return Response({"response": "false"}, status=status.HTTP_200_OK)

        paginated_queryset = paginator.paginate_queryset(stocks, request)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)




class Price_changeViewSet(viewsets.ModelViewSet):
    queryset = Price_change.objects.all().order_by('-id')
    serializer_class = Price_changeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['income__id'] #?search
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return Price_changeCreateSerializer  #сериализатор для POST-запросов (GET показывает весь список, POST оставляет ID)
        return Price_changeDetailSerializer

    # Поиск по номеру инвойса и название товара с учетом фильтров
    # api/prices_change/search_by_invoice_product/?invoice_number=1&product_name=асфа
    @action(detail=False, methods=['GET'])
    def search_by_invoice_product(self, request):
        invoice_number = request.GET.get('invoice_number')
        product_name = request.GET.get('product_name')

        if invoice_number is not None:
            # Создаем фильтр для поиска по номеру инвойса
            invoice_filter = Q(invoice_number__iexact=invoice_number)

            # Создаем фильтр для поиска по названию товара (если указано)
            product_filter = Q()
            if product_name:
                # Переносим в нижний регистр и разделяем на слова
                product_name = product_name.lower()
                product_name_parts = product_name.split()

                # Создаем фильтра для поиска по названию товара (без учета регистра и частичное совпадение)
                for part in product_name_parts:
                    product_filter |= Q(product_name__iregex=part)

            # Искать и фильтровать записи в таблицах Invoice и Product
            invoices = Invoice.objects.filter(invoice_filter)
            products = Product.objects.filter(product_filter)

            # Если найдены соответствующие записи, вернуть их сериализованные данные
            if invoices.exists() and products.exists():
                invoice_serializer = InvoiceSerializer(invoices, many=True)
                product_serializer = ProductSerializer(products, many=True)
                return Response({
                    'invoices': invoice_serializer.data,
                    'products': product_serializer.data
                })
            else:
                return Response({'message': 'Записей не найдено.'}, status=404)
        else:
            # Если номер инвойса не указан, вернуть всю таблицу Price_Change
            price_changes = Price_change.objects.all()
            price_change_serializer = Price_changeSerializer(price_changes, many=True)
            return Response({'price_changes': price_change_serializer.data})


class RetailViewSet(viewsets.ModelViewSet):
    queryset = Retail.objects.all().order_by('-id')
    serializer_class = RetailSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['']
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RetailCreateSerializer  #сериализатор для POST-запросов (GET показывает весь список, POST оставляет ID)
        return RetailDetailSerializer



class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all().order_by('-id')
    serializer_class = ContractSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['client__id']    #?search=1
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ContractCreateSerializer  #сериализатор для POST-запросов (GET показывает весь список, POST оставляет ID)
        return ContractDetailSerializer

    # Поиск договоров по номеру договора
    # api/contracts/?contract_number=123
    def get_queryset(self):
        contract_number = self.request.query_params.get('contract_number')
        if contract_number:
            return Contract.objects.filter(contract_number=contract_number)
        return super().get_queryset()



   #Поиск по двум параметрам где номер контракта по цифре все данные,или есть пустой запрос то весь список выдает
    # api/contracts/search_by_client_and_number/?client_id=4&contract_number=1234
    @action(detail=False, methods=['GET'])
    def search_by_client_and_number(self, request):
        client_id = request.query_params.get('client_id')
        contract_number = request.query_params.get('contract_number')

        if not client_id:
            return Response({"message": "Не указан параметр client_id"}, status=status.HTTP_400_BAD_REQUEST)

        contracts = Contract.objects.filter(client_id=client_id)

        if contract_number:
            contracts = contracts.filter(contract_number__icontains=contract_number)

        #Сортируем записи по дате создания в обратном порядке в количестве 5 записей
        contracts = contracts.order_by('-contract_number')[:5]

        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)





class CountryViewSet(viewsets.ModelViewSet):  #справочник
    queryset = Country.objects.all().order_by('-id')
    serializer_class = CountrySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['country_name']  #?search=AAAA
    pagination_class = APIListPagination
    permission_classes = [IsAuthenticated]

    # Поиск страны по букве в независимости от регистра и сортировка 5 по ID
    # api/countries/search_by_name/?name=
    @action(detail=False, methods=['GET'])
    def search_by_name(self, request):
        query = request.query_params.get('name', '')

        # Делаем пагинацию
        paginator = PageNumberPagination()

        # Получаем количество записей на странице из параметра запроса, по умолчанию 5
        page_size = int(request.query_params.get('page_size', 5))
        paginator.page_size = page_size

        if not query:
            countries = Country.objects.all()  # Возвращает все записи, если 'name' не задан
        else:
            countries = Country.objects.filter(country_name__iregex=query).order_by('-id') #Поиск по имени по любой букве

        # Применяем пагинацию к результатам
        paginated_countries = paginator.paginate_queryset(countries, request)

        serializer = CountrySerializer(paginated_countries, many=True)
        return paginator.get_paginated_response(serializer.data)












