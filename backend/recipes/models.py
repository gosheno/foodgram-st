from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name="Единица измерения"
    )

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"

    class Meta:
        ordering = ['name']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Название рецепта"
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="Ингредиенты"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (минуты)",
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        null=True,
        blank=True,
        verbose_name="Изображение рецепта"
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient"
            )
        ]
        verbose_name = (
            "Ингредиент в рецепте"
        )
        verbose_name_plural = (
            "Ингредиенты в рецептах"
        )

    def __str__(self):
        return (
            f"{self.ingredient.name} - {self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_favorite"
            )
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"

    def __str__(self):
        return f"{self.user.username} → {self.recipe.name}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_carts",
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="Рецепт"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_shopping_cart"
            )
        ]
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"
