import os
import logging

class HanaVectorStore:
    def __init__(self):
        self.host = os.getenv("HANA_HOST", "mock_host")
        logging.info("HANA Vector Driver Initialized (Enterprise clean-core ready).")
        
    def query_similarity(self, vector_embeddings: list) -> list:
        return [{"chunk_text": "Manual de Seguridad Minera EHS v4. Seccion 12", "distance": 0.12}]
