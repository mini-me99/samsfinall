"""Generic helpers for building thin CRUD modules quickly."""
from rest_framework import serializers


def make_serializer(model_cls, exclude=("deleted_at",)):
    model_fields = [f.name for f in model_cls._meta.get_fields()
                    if not f.many_to_many and not f.one_to_many and f.name not in exclude]

    class _S(serializers.ModelSerializer):
        class Meta:
            model = model_cls
            fields = model_fields
            read_only_fields = ["id", "academy", "created_at", "updated_at"]

    _S.__name__ = f"{model_cls.__name__}Serializer"
    return _S
