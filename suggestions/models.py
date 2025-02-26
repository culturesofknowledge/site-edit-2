from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import datetime
from suggestions import utils as sug_utils
from person      import person_suggestion_fields
from location    import location_suggestion_fields
from institution import institution_suggestion_fields
from publication import publication_suggestion_fields

class CofkSuggestions(models.Model):
    suggestion_id = models.AutoField(primary_key=True)
    suggestion_new = models.BooleanField(default=True)
    suggestion_type = models.CharField(max_length=200)
    suggestion_suggestion = models.TextField()
    # suggestion_relation = models.CharField(max_length=200, default="None")
    # suggestion_related_record = models.ForeignKey('CofkRecords', on_delete=models.CASCADE, null=True, blank=True)
    suggestion_status = models.CharField(max_length=256, default="New")

    # Automatic fields
    suggestion_created_at = models.DateTimeField(auto_now_add=True)
    suggestion_updated_at = models.DateTimeField(auto_now=True)
    suggestion_resolved_at = models.DateTimeField(null=True, blank=True)
    suggestion_author = models.ForeignKey('login.CofkUser',  on_delete=models.SET_NULL,
                     related_name='suggestions', null=True, blank=True
    )

    # Default = -1 means there is no related record for this suggestion
    suggestion_related_record_int = models.IntegerField(null=True, blank=True, default=-1)

    # Relation fields for ForeignKey-like feature. No idea how to use this though
    # To be removed?
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggestion_relation'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    suggestion_related_record = GenericForeignKey('content_type', 'suggestion_id')

    class Meta:
        db_table = 'cofk_union_suggestions'

    @property
    def is_updated(self):
        # Updated date-time is always a few microseconds ahead of created date-time
        created = self.suggestion_created_at + datetime.timedelta(seconds=1)
        updated = self.suggestion_updated_at
        return updated > created

    def fields(self):
        match self.suggestion_type:
            case "Person":
                return sug_utils.suggestion_fields(person_suggestion_fields.suggestion_fields_map())
            case "Location":
                return sug_utils.suggestion_fields(location_suggestion_fields.suggestion_fields_map())
            case "Institution":
                return sug_utils.suggestion_fields(institution_suggestion_fields.suggestion_fields_map())
            case "Publication":
                return sug_utils.suggestion_fields(publication_suggestion_fields.suggestion_fields_map())

    def new_suggestion_text(self):
        return ":\n\n".join(self.fields()) + ":"

    @property
    def parsed_suggestion(self):
        keys = self.fields()
        key1 = ""
        key2 = ""
        text_key = ""
        suggestion_hash = {}
        for line in self.suggestion_suggestion.split("\n"):
            keyword = False
            for key in keys:
                if line.startswith(key):
                    if key1 == "":
                        key1 = key
                    else:
                        key1 = key2
                    key2 = key
                    suggestion_hash[key1] = text_key.strip()
                    text_key = line.split(key)[1].strip().lstrip(":")
                    keyword = True
                    break
            if not keyword:
                text_key = text_key + " " + line.strip()
        suggestion_hash[key2] = text_key.strip()
        return suggestion_hash
