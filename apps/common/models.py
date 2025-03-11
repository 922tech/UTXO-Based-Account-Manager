"""
This module includes the models that are supposed to be used by any other apps.
Do not write models that are related to other models in here.
"""
from pydantic import BaseModel as PydanticBaseModel

from django.db import models


class BaseQuerySet(models.QuerySet):
    """
    Every queryset in the application must be a subclass to this class.
    """

    def soft_delete(self):
        self.update(is_deleted=True)


class BaseManager(models.Manager.from_queryset(BaseQuerySet)):
    """
    Every custom managers in the application must be a subclass to class.
    """
    pass


class BaseModel(models.Model):
    """
    Every model in the application must be a subclass to this model.
    User is the only model that does not inherit from AbstractUser i.e. it cannot inherit from BaseModel
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = BaseManager()

    class Meta:
        abstract = True


class SingletonQuerySet(BaseQuerySet):
    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance."""
        raise NotImplementedError('Singleton object is not deletable')


class SingletonModel(BaseModel):
    objects = SingletonQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance."""
        raise NotImplementedError('Singleton object is not deletable')

    @classmethod
    def get_instance(cls, **kwargs):
        """Get the singleton instance, create one if none exists."""
        instance = cls.objects.first()
        if not instance:
            instance = cls.objects.create(**kwargs)
        return instance


class ConfigSchema(PydanticBaseModel):
    storage_id: int

    @classmethod
    def validate_schema(cls, config_dict: dict):
        return cls.parse_obj(config_dict).model_dump()


class Config(SingletonModel):
    """
    This model holds the base configurations for the service
    Due to the frequent changes to this sort of models, the logic is written in a way that does not create a new
    migration on every change
    NOTE: for each update the attributes declared on the class. Validation and intelligence should match
    """
    storage_id: int

    config = models.JSONField(default=dict, validators=[ConfigSchema.validate_schema])
