from typing import Any
import tablib

from djangospice.jobs import Job, JobStatus
from djangospice.realtime.broadcast import Broadcast
from djangospice.resources import BaseResource
from .dataset import TemporaryDataset 


class ResourceImport(Job):
    
    queue = "data-imports"

    def __init__(self, resource: BaseResource, file_path: str, user_id: str, raise_errors: bool = True) -> None:
        self.resource = resource
        self.file_path = file_path
        self.user_id = user_id
        self.raise_errors = raise_errors

    def handle(self) -> dict[str, Any]:
        # 1. The Context Manager handles all IO, parsing, and guaranteed cleanup
        with TemporaryDataset(self.file_path) as dataset:
            total_rows = len(dataset)
            
            if total_rows == 0:
                return {"imported": 0, "message": "No valid data found in file."}

            batch_size = 500
            
            # 2. Process and report
            for start in range(0, total_rows, batch_size):
                end = min(start + batch_size, total_rows)
                
                # Create a chunked dataset keeping original headers
                batch = tablib.Dataset(headers=dataset.headers)
                batch.extend(dataset[start:end])

                self.resource.import_data(
                    dataset=batch, 
                    raise_errors=self.raise_errors
                )
                
                self.progress(
                    current=end,
                    total=total_rows,
                    message=f"Importing records. {self.percent}% completed."
                )
            
            payload = {
                "total_rows": total_rows,
                "message":  f"Successfully imported {total_rows} records.",
                "status": JobStatus.SUCCESS
            }
            
            Broadcast.user(user=self.user_id, data=payload)