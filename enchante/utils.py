from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db import models as django_models
from enchante.models import Pan, PanServing, RoundPan, SquarePan

def update_related_instances(instance, related_data, related_set, related_model, related_serializer, instance_field_name):
    """
    This function updates related instances of a given instance.

    Parameters:
    - instance: The instance whose related instances are to be updated.
    - related_data: The validated data for the related instances.
    - related_set: The name of the related set on the instance.
    - related_model: The model class of the related instances.
    - related_serializer: The serializer class for the related instances.
    - instance_field_name: The name of the field on the related model that refers to the instance.
    """
    # Get the ids of the related instances to update or create
    update_ids = [data.get('id') for data in related_data if data.get('id') is not None]

    # Delete related instances that are not included in the update_ids
    for related_instance in getattr(instance, related_set).all():
        if related_instance.id not in update_ids:
            related_instance.delete()

    # Update existing related instances and create new ones
    for data in related_data:
        data_id = data.get('id', None)
        if data_id:
            related_instance = get_object_or_404(related_model, id=data_id, **{instance_field_name: instance})
            # Ensure the related field is a primary key, not a model instance
            for field, value in data.items():
                if isinstance(value, django_models.Model):
                    data[field] = value.id
            serializer = related_serializer(data=data, instance=related_instance)
            if serializer.is_valid():
                serializer.save()
            else:
                raise serializers.ValidationError(serializer.errors)
        else:
            related_model.objects.create(**{instance_field_name: instance}, **data)

def scale_sub_recipe(sub_recipe, required_quantity):
    # Get the default quantity of the sub-recipe
    default_quantity = sub_recipe.quantity

    # Calculate the scaling factor
    scaling_factor = required_quantity / default_quantity

    # Scale the quantities of the ingredients
    for recipe_ingredient in sub_recipe.recipeingredient_set.all():
        recipe_ingredient.quantity *= scaling_factor
        recipe_ingredient.save()

def estimate_servings(pan):
    # Get the two entries in the reference table with the closest volumes
    lower_entry = PanServing.objects.filter(pan_type=pan.pan_type, volume__lte=pan.volume).order_by('-volume').first()
    upper_entry = PanServing.objects.filter(pan_type=pan.pan_type, volume__gte=pan.volume).order_by('volume').first()

    # If there's no lower or upper entry, return the servings of the available entry
    if lower_entry is None:
        return upper_entry.servings
    if upper_entry is None:
        return lower_entry.servings

    # If the pan's volume matches exactly with an entry, return its servings
    if lower_entry.volume == pan.volume:
        return lower_entry.servings

    # Interpolate between the two closest volumes
    volume_diff = upper_entry.volume - lower_entry.volume
    servings_diff = upper_entry.servings - lower_entry.servings
    volume_ratio = (pan.volume - lower_entry.volume) / volume_diff
    estimated_servings = lower_entry.servings + servings_diff * volume_ratio

    return estimated_servings

def estimate_volume(pan_type, servings):
    # Get the two entries in the reference table with the closest servings
    lower_entry = PanServing.objects.filter(pan_type=pan_type, servings__lte=servings).order_by('-servings').first()
    upper_entry = PanServing.objects.filter(pan_type=pan_type, servings__gte=servings).order_by('servings').first()

    # If there's no lower or upper entry, return the volume of the available entry
    if lower_entry is None:
        return upper_entry.volume
    if upper_entry is None:
        return lower_entry.volume

    # If the servings match exactly with an entry, return its volume
    if lower_entry.servings == servings:
        return lower_entry.volume

    # Interpolate between the two closest servings
    servings_diff = upper_entry.servings - lower_entry.servings
    volume_diff = upper_entry.volume - lower_entry.volume
    servings_ratio = (servings - lower_entry.servings) / servings_diff
    estimated_volume = lower_entry.volume + volume_diff * servings_ratio

    return estimated_volume

PAN_MODELS = {db_type: globals()[model_type + 'Pan'] for db_type, model_type in Pan.PAN_TYPES}

def get_pan_model(pan_type):
    return PAN_MODELS.get(pan_type.upper())