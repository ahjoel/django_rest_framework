from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from shop.models import Category, Product, Article


class ArticleSerializer(ModelSerializer):

    class Meta:
        model = Article
        fields = ['id', 'name', 'price', 'active', 'product', 'date_created', 'date_updated']

    def validate_price(self, value):
        if value < 1:
            raise serializers.ValidationError('Price must be greater than 1')
        return value

    def validate_product(self, value):
        if value.active is False:
            raise serializers.ValidationError('Inactive product')
        return value


class ProductListSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'active', 'category', 'date_created', 'date_updated']


# Optimisation du serializer avec la liste des articles actifs et leurs produits respectives
class ProductDetailSerializer(ModelSerializer):

    # En utilisant un `SerializerMethodField', il est nécessaire d'écrire une méthode
    # nommée 'get_XXX' où XXX est le nom de l'attribut, ici 'products'
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'active', 'category', 'date_created', 'date_updated', 'articles']

    def get_articles(self, instance):
        # Le paramètre 'instance' est l'instance du produit consulté.
        # Dans le cas d'une liste, cette méthode est appelée autant de fois qu'il y a
        # d'entités dans la liste

        # On applique le filtre sur notre queryset pour n'avoir que les articles actifs
        queryset = instance.articles.filter(active=True)
        # Le serializer est créé avec le queryset défini et toujours défini en tant que many=True
        serializer = ArticleSerializer(queryset, many=True)
        # la propriété '.data' est le rendu de notre serializer que nous retournons ici
        return serializer.data


class CategoryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'date_created', 'date_updated', 'name', 'description']

    def validate_name(self, value):
        # Nous vérifions que la catégorie existe
        if Category.objects.filter(name=value).exists():
            # En cas d'erreur, DRF nous met à disposition l'exception ValidationError
            raise serializers.ValidationError('Category already exists')
        return value

    # Controle pour que le nom soit dans la description
    def validate(self, data):
        # Effectuons le contrôle sur la présence du nom dans la description
        if data['name'] not in data['description']:
            # Levons une ValidationError si ça n'est pas le cas
            raise serializers.ValidationError('Name must be in description')
        return data


# Optimisation du serializer avec la liste des produits actifs et leurs categories respectives
class CategoryDetailSerializer(serializers.ModelSerializer):

    # En utilisant un `SerializerMethodField', il est nécessaire d'écrire une méthode
    # nommée 'get_XXX' où XXX est le nom de l'attribut, ici 'products'
    products = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'date_created', 'date_updated', 'name', 'products']

    def get_products(self, instance):
        # Le paramètre 'instance' est l'instance de la catégorie consultée.
        # Dans le cas d'une liste, cette méthode est appelée autant de fois qu'il y a
        # d'entités dans la liste

        # On applique le filtre sur notre queryset pour n'avoir que les produits actifs
        queryset = instance.products.filter(active=True)
        # Le serializer est créé avec le queryset défini et toujours défini en tant que many=True
        serializer = ProductListSerializer(queryset, many=True)
        # la propriété '.data' est le rendu de notre serializer que nous retournons ici
        return serializer.data

