import logging
from typing import Tuple
from django_tables2.export import TableExport
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from djangospice.filters.helpers import dynamic_queryset



logger = logging.getLogger(__name__)


class TableExporter:
    def __init__(self, table_class, model_class, export_format, rename_file=False, **kwargs):
        super().__init__(rename_file, **kwargs)
        self.table_class = table_class
        self.model_class = model_class
        self.export_format = export_format
        
    def get_query_set(self, model):
        qs = model.objects.all()
        
        filters = self.kwargs.get("filters", {})

        # No filters? Return normal queryset
        if not filters:
            return qs

        try:
            return dynamic_queryset(qs, filters)
        except Exception as e:
            logger.error(
                f"Filtering failed for {model.__name__} with filters {filters}: {e}"
            )
            return qs

    def handle(self) -> Tuple[str, str]:
        queryset = self.get_query_set(self.model_class)
        table = self.table_class(queryset)
        
        exporter = TableExport(self.export_format, table)
        file_content = exporter.export()

        name = self.table_class.__name__ or self.model_class.__name__

        filename = self.make_file_name(self.export_format, name)
        
        self.file_path = default_storage.save(filename, ContentFile(file_content))
        self.file_url = default_storage.url(self.file_path)
        
        return self.file_path, self.file_url

