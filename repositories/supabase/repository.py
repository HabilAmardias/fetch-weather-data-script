import os
from supabase import create_client, Client
import pandas as pd
from abc import ABC, abstractmethod
from typing import List
from postgrest.base_request_builder import _ReturnT

class AbstractSupabaseRepository(ABC):
    @abstractmethod
    def insert_data(self, data: pd.DataFrame, table_name: str):
        pass

    @abstractmethod
    def get_data(self, table_name: str) -> List[_ReturnT]:
        pass

class SupabaseRepositoryImpl(AbstractSupabaseRepository):
    def __init__(self, client: Client):
        self.client = client
    
    def insert_data(self, data, table_name):
        records = data.to_dict("records")
        self.client.table(table_name).upsert(records).execute()
    
    def get_data(self, table_name):
        return self.client.table(table_name).select("*").execute().data

def create_supabase_repository() -> AbstractSupabaseRepository:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_API_KEY")
    client: Client = create_client(url, key)
    return SupabaseRepositoryImpl(client)