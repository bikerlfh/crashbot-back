# Standard Library
import uuid

# Django
from django.db import models
from cacheops import invalidate_obj


class BaseSimpleModel(models.Model):
    """
    this model does not have created_at and updated_at
    """

    CASE_STYLE = "lower"

    def clean(self):
        fields_to_clean = getattr(self, "FIELDS_TO_CLEAN", None)
        fields = self._meta.fields

        if not fields_to_clean:
            return

        for field in fields:
            name = field.name
            if name in fields_to_clean:
                value = getattr(self, name)

                if value is None:
                    continue

                cleaned_value = value.strip()
                if self.CASE_STYLE and hasattr(str, self.CASE_STYLE):
                    cleaned_value = getattr(cleaned_value, self.CASE_STYLE)()

                setattr(self, name, cleaned_value)

    def save(self, *args, **kwargs):
        self.full_clean()
        invalidate_obj(self)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseModel(BaseSimpleModel):
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="created at"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    def save(self, *args, **kwargs):
        self.full_clean()
        invalidate_obj(self)
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseModelUUID(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
