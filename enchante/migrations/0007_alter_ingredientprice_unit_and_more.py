# Generated by Django 4.2.6 on 2023-11-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enchante', '0006_recipeingredient_unit_alter_ingredientprice_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientprice',
            name='unit',
            field=models.TextField(choices=[('g', 'Grams'), ('kg', 'Kilograms'), ('ml', 'Milliliters'), ('cl', 'Centiliters'), ('l', 'Liters'), ('tsp', 'Teaspoons'), ('tbsp', 'Tablespoons'), ('cas', 'Cuillère à soupe'), ('cc', 'Cuillère à café'), ('cup', 'Cups'), ('unit', 'Unit')], max_length=200),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='unit',
            field=models.CharField(blank=True, choices=[('g', 'Grams'), ('kg', 'Kilograms'), ('ml', 'Milliliters'), ('cl', 'Centiliters'), ('l', 'Liters'), ('tsp', 'Teaspoons'), ('tbsp', 'Tablespoons'), ('cas', 'Cuillère à soupe'), ('cc', 'Cuillère à café'), ('cup', 'Cups'), ('unit', 'Unit')], max_length=50, null=True),
        ),
    ]
