from foodgram_api.image_field import Base64ImageField
from rest_framework import serializers
from users.models import User

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source="ingredient.id",
    )
    name = serializers.ReadOnlyField(
        source="ingredient.name",
    )
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            "id",
            "name",
            "measurement_unit",
            "amount",
        )


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientInRecipeSerializer(
        many=True, 
        source="recipe_ingredients",
        read_only=True  # Добавляем явное указание, что поле только для чтения
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def get_author(self, obj):
        from users.serializers import UserSerializer
        return UserSerializer(obj.author, context=self.context).data

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return obj.in_shopping_carts.filter(user=user).exists()
        return False


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("ingredients", "image", "name", "text", "cooking_time")

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(
            author=self.context["request"].user,  # Автор только здесь
            **validated_data
        )
        self._add_ingredients(recipe, ingredients_data)
        return recipe
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        instance = super().update(instance, validated_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._add_ingredients(instance, ingredients_data)
        return instance

    def _add_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients_data
        ])
        
    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать хотя бы один ингредиент.")

        ids = [item["id"].id for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Ингредиенты в рецепте не должны повторяться.")
        return value

    def validate(self, data):
        request = self.context.get("request")
        if not self.context.get("request").user.is_authenticated:
            raise serializers.ValidationError("Для создания или изменения рецепта требуется авторизация.")
        
        if request.method in ['PUT', 'PATCH'] and 'ingredients' not in data:
            raise serializers.ValidationError({
                "ingredients": ["Это поле обязательно при обновлении рецепта."]
            }, code='required')
            
        return data
    
    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = "__all__"
        

class FollowSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username", "first_name", "last_name",
            "is_subscribed", "recipes", "recipes_count", "avatar",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and obj.follower.filter(user=user).exists()

    def get_recipes(self, obj):
        limit = self.context.get("recipes_limit")
        queryset = obj.recipes.all()
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return RecipeMinifiedSerializer(queryset, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"
