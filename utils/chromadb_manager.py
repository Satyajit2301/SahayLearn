import streamlit as st
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    st.error("ChromaDB not available. Please install it.")
    st.stop()

import os
from typing import List, Dict, Optional

class ChromaDBManager:
    def __init__(self):
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists"""
        try:
            collections = self.client.list_collections()
            return any(col.name == collection_name for col in collections)
        except Exception:
            return False
    
    def store_chunks(self, chunks: List[Dict], collection_name: str):
        """Store text chunks in ChromaDB"""
        try:
            # Create or get collection
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Chunks for {collection_name}"}
            )
            
            # Prepare data for storage
            documents = [chunk['content'] for chunk in chunks]
            metadatas = [
                {
                    'chapter': str(chunk['chapter']),
                    'part_number': int(chunk['part_number']),
                    'chunk_id': str(chunk['id'])
                } for chunk in chunks
            ]
            ids = [chunk['id'] for chunk in chunks]
            
            # Store in ChromaDB
            collection.upsert(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            st.success(f"Stored {len(chunks)} chunks in {collection_name}")
            
        except Exception as e:
            st.error(f"Error storing chunks: {str(e)}")
    
    def get_chunk_by_part(self, collection_name: str, part_number: int) -> Optional[Dict]:
        """Retrieve a specific part/chunk"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            results = collection.query(
                query_texts=[""],  # Empty query to get all
                where={"part_number": part_number},
                n_results=1
            )
            
            if results['documents'] and results['documents'][0]:
                return {
                    'content': results['documents'][0][0],
                    'metadata': results['metadatas'][0][0] if results['metadatas'] and results['metadatas'][0] else {},
                    'id': results['ids'][0][0] if results['ids'] and results['ids'][0] else ""
                }
            return None
            
        except Exception as e:
            st.error(f"Error retrieving chunk: {str(e)}")
            return None
    
    def search_similar_content(self, collection_name: str, query: str, n_results: int = 3) -> List[Dict]:
        """Search for similar content"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            similar_content = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    similar_content.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] and i < len(results['metadatas'][0]) else {},
                        'id': results['ids'][0][i] if results['ids'] and results['ids'][0] and i < len(results['ids'][0]) else ""
                    })
            
            return similar_content
            
        except Exception as e:
            st.error(f"Error searching content: {str(e)}")
            return []
    
    def get_total_parts(self, collection_name: str) -> int:
        """Get total number of parts in a collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            result = collection.count()
            return result
        except Exception:
            return 0
    
    def get_content_by_text_selection(self, collection_name: str, selected_text: str) -> Optional[Dict]:
        """Find content chunk containing selected text"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            # Search for chunks containing the selected text
            results = collection.query(
                query_texts=[selected_text],
                n_results=1
            )
            
            if results['documents'] and results['documents'][0]:
                # Verify the selected text is actually in the document
                doc_content = results['documents'][0][0]
                if selected_text.lower() in doc_content.lower():
                    return {
                        'content': doc_content,
                        'metadata': results['metadatas'][0][0] if results['metadatas'] and results['metadatas'][0] else {},
                        'id': results['ids'][0][0] if results['ids'] and results['ids'][0] else ""
                    }
            
            return None
            
        except Exception as e:
            st.error(f"Error finding content: {str(e)}")
            return None
