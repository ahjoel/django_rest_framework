from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from shop.models import Category, Product, Article
from shop.permissions import IsAdminAuthenticated
from shop.serializers import CategoryDetailSerializer, CategoryListSerializer, ProductListSerializer, ProductDetailSerializer, ArticleSerializer


# class CategoryAPIView(APIView):
#
#    def get(self, *args, **kwargs):
#        categories = Category.objects.all()
#        serializer = CategorySerializer(categories, many=True)
#        return Response(serializer.data)


'''class ProductAPIView(APIView):

    def get(self, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)'''


class MultipleSerializerMixin:
    # Un mixin est une classe qui ne fonctionne pas de façon autonome
    # Elle permet d'ajouter des fonctionnalités aux classes qui les étendent

    detail_serializer_class = None

    def get_serializer_class(self):
        # Notre mixin détermine quel serializer à utiliser
        # même si elle ne sait pas ce que c'est ni comment l'utiliser
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            # Si l'action demandée est le détail alors nous retournons le serializer de détail
            return self.detail_serializer_class
        return super().get_serializer_class()


# Permet de faire du CRUD sur la category (old)
class CategoryViewsets(ModelViewSet):

    serializer_class = CategoryListSerializer

    def get_queryset(self):
        return Category.objects.all()


# Permet uniquement la lecture sur la category
class CategoryViewset(ReadOnlyModelViewSet):

    serializer_class = CategoryListSerializer
    detail_serializer_class = CategoryDetailSerializer

    def get_queryset(self):
        return Category.objects.filter(active=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    # Action de désactiver une catégorie et ses produits associés dans le model
    # avec la méthode POST
    @action(detail=True, methods=['POST'])
    def disable(self, request, pk):
        self.get_object().disable()
        return Response()


# Permet uniquement la lecture sur le produit (old)
class ProductViewsets(ModelViewSet):

    serializer_class = ProductListSerializer

    def get_queryset(self):
        return Product.objects.all()


# Permet uniquement la lecture sur le produit
class ProductViewset(ReadOnlyModelViewSet):

    serializer_class = ProductListSerializer
    detail_serializer_class = ProductDetailSerializer

    # cas de filtre
    def get_queryset(self):
        # Recuperation de tous les produits dans une variable nommé queryset
        queryset = Product.objects.filter(active=True)
        # verification de la présence du paramètre 'category_id' dans l'url
        # et si oui appliquons le filtre
        category_id = self.request.GET.get('category_id')
        if category_id is not None:
            queryset = queryset.filter(category_id=category_id)
        return queryset

    # l'attribut action permet de savoir l'action en cours sur l'endpoint
    # cas de detail sur une entité fille
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    # Action de désactiver un produits et ses articles associés dans le model
    # avec la méthode POST
    @action(detail=True, methods=['POST'])
    def disable(self, request, pk):
        self.get_object().disable()
        return Response()


class ArticleViewset(ModelViewSet):

    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = Article.objects.filter(active=True)
        product_id = self.request.GET.get('product_id')
        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class AdminCategoryViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CategoryListSerializer
    detail_serializer_class = CategoryDetailSerializer
    # Nous avons simplement à appliquer la permission sur le viewset
    # permission_classes = [IsAuthenticated]
    # Permission aux administrateurs authentifiés
    permission_classes = [IsAdminAuthenticated]

    def get_queryset(self):
        return Category.objects.all()


class AdminArticleViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ArticleSerializer
    detail_serializer_class = None

    def get_queryset(self):
        return Article.objects.all()


