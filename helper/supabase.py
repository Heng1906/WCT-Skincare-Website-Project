from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseService:
    __url = os.getenv("__URL")
    __key = os.getenv("__KEY")
    __storage_bucket = os.getenv("__STORAGE_BUCKET")
    supabase = create_client(__url, __key)

    @classmethod
    def upload_file(cls, bucket: str, file, report_id: str) -> str:
        if bucket is None:
            bucket = cls.__storage_bucket

        file_name = f"{report_id}.{file.filename.split('.')[-1]}"
        file_content = file.file.read()
        response = cls.supabase.storage.from_(bucket).upload(
            path=file_name,
            file=file_content,
            file_options={
                'content-type': file.content_type,
            }
        )
        if response.status_code == 200:
            image_url = cls.supabase.storage.from_(bucket).get_public_url(file_name)
            return image_url.removesuffix('?')
        return None

    @classmethod
    def delete_file(cls, bucket: str, filename: str) -> bool:
        if bucket is None:
            bucket = cls.__storage_bucket

        response = cls.supabase.storage.from_(bucket).remove(filename)
        if response is not []:
            return True
        return False
