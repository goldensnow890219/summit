import pickle

from django.db import models


class SystemVariable(models.Model):
    key = models.CharField(max_length=32, blank=False, unique=True)
    value = models.BinaryField()
    editable = models.BooleanField(default=False)

    @classmethod
    def set(cls, key, value):
        value = pickle.dumps(value)
        try:
            variable = cls.objects.get(key=key)
        except cls.DoesNotExist:
            cls.objects.create(key=key, value=value)
        else:
            variable.value = value
            variable.save()

    @classmethod
    def get(cls, key):
        try:
            return pickle.loads(cls.objects.get(key=key).value)
        except cls.DoesNotExist:
            return None
