import time
import uuid
from database.mongo import Database

# Fallback In-Memory Storage if MongoDB is offline
IN_MEMORY_RASTERS = {}

class RasterModel:

    @staticmethod
    def save_raster_metadata(meta_dict):
        """Saves metadata record to MongoDB or In-Memory fallback."""
        raster_id = uuid.uuid4().hex[:12]
        record = {
            "_id": raster_id,
            "raster_id": raster_id,
            "created_at": time.time(),
            **meta_dict
        }

        collection = Database.get_collection("uploads")
        if collection is not None:
            try:
                collection.insert_one(record)
            except Exception as e:
                print(f"MongoDB Insert Error: {e}")
                IN_MEMORY_RASTERS[raster_id] = record
        else:
            IN_MEMORY_RASTERS[raster_id] = record

        return raster_id

    @staticmethod
    def get_raster_by_id(raster_id):
        """Retrieves metadata record by raster_id."""
        collection = Database.get_collection("uploads")
        if collection is not None:
            try:
                res = collection.find_one({"raster_id": raster_id})
                if res:
                    return res
            except Exception as e:
                print(f"MongoDB Fetch Error: {e}")

        return IN_MEMORY_RASTERS.get(raster_id)