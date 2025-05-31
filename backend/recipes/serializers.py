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
        many=True, source="recipe_ingredients")
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

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(
            recipe=obj
        ).select_related("ingredient")
        return IngredientInRecipeSerializer(ingredients, many=True).data

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

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Ingredients cannot be empty.")

        ids = [item["id"].id for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Ingredients must be unique.")
        return value

    def create_ingredients(self, recipe, ingredients_data):
        ingredients = [
            RecipeIngredient(
                recipe=recipe, ingredient=item["id"], amount=item["amount"]
            )
            for item in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

    def validate(self, data):
        if not self.context["request"].user.is_authenticated:
            raise serializers.ValidationError(
                "You must be authenticated to create or update recipes."
            )

        if self.context["request"].method in ["PATCH", "PUT"]:
            if "ingredients" not in data:
                raise serializers.ValidationError(
                    {"ingredients": """
                    This field is required when updating a recipe."""},
                    code="required",
                )
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients_data)
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", None)
        instance = super().update(instance, validated_data)
        if ingredients_data is not None:
            instance.recipe_ingredients.all().delete()
            self._add_ingredients(instance, ingredients_data)
        return instance

    def _add_ingredients(self, recipe, ingredients_data):
        ingredients = [
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )
            for ingredient_data in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(ingredients)

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
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        f = user.is_authenticated and obj.follower.filter(user=user).exists()
        return f

    def get_recipes(self, obj):
        limit = self.context.get("recipes_limit")

        recipes = Recipe.objects.filter(author=obj)
        if limit is not None and limit.isdigit():
            recipes = recipes[:int(limit)]

        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = "__all__"
