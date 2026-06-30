from typing import List, Dict, Optional
from pathlib import Path
import sys
import logging

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import ChromaConfig, KnowledgeBaseConfig
from .vector_store import VectorStore
from .document_loader import DocumentLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGSearch:
    def __init__(self, collection_name: str = "computer_network"):
        try:
            self.vector_store = VectorStore(collection_name)
            self.initialized = True
        except Exception as e:
            logger.error(f"RAGSearch 初始化失败: {str(e)}")
            self.vector_store = None
            self.initialized = False

    def search(self, query: str, n_results: int = 5, threshold: float = 2.0) -> Dict:
        if not self.initialized or not self.vector_store:
            return {
                "query": query,
                "total_found": 0,
                "results": [],
                "raw_count": 0,
                "error": "向量库未初始化"
            }
        
        try:
            results = self.vector_store.query(query, n_results)
            
            filtered_results = []
            for i in range(results["count"]):
                if results["distances"][i] <= threshold:
                    filtered_results.append({
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i],
                        "distance": results["distances"][i]
                    })
            
            return {
                "query": query,
                "total_found": len(filtered_results),
                "results": filtered_results,
                "raw_count": results["count"]
            }
        except Exception as e:
            logger.error(f"RAG搜索失败: {str(e)}")
            return {
                "query": query,
                "total_found": 0,
                "results": [],
                "raw_count": 0,
                "error": f"搜索失败: {str(e)}"
            }

    def build_context(self, query: str, n_results: int = 5, threshold: float = 2.0) -> str:
        try:
            search_results = self.search(query, n_results, threshold)
            
            if search_results.get("error") or search_results["total_found"] == 0:
                return ""
            
            context_parts = []
            for idx, result in enumerate(search_results["results"], 1):
                source_info = f"【来源：{result['metadata']['file_name']} 片段{result['metadata']['chunk_index']+1}/{result['metadata']['total_chunks']}】"
                context_parts.append(f"{source_info}\n{result['content']}\n")
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"上下文构建失败: {str(e)}")
            return ""

    def get_relevant_knowledge(self, query: str, max_context_length: int = 2000) -> Dict:
        try:
            context = self.build_context(query)
            
            if len(context) > max_context_length:
                context = context[:max_context_length] + "\n...（内容已截断）"
            
            return {
                "query": query,
                "has_context": len(context) > 0,
                "context": context,
                "context_length": len(context)
            }
        except Exception as e:
            logger.error(f"获取相关知识失败: {str(e)}")
            return {
                "query": query,
                "has_context": False,
                "context": "",
                "context_length": 0,
                "error": str(e)
            }

    def query_with_context(self, query: str, n_results: int = 5) -> Dict:
        try:
            search_results = self.search(query, n_results)
            
            context = ""
            if not search_results.get("error") and search_results["total_found"] > 0:
                context = self.build_context(query, n_results)
            
            return {
                "query": query,
                "search_results": search_results,
                "context": context,
                "context_length": len(context)
            }
        except Exception as e:
            logger.error(f"带上下文查询失败: {str(e)}")
            return {
                "query": query,
                "search_results": {"total_found": 0, "results": []},
                "context": "",
                "context_length": 0,
                "error": str(e)
            }

    def ensure_index(self):
        if not self.initialized or not self.vector_store:
            return {
                "total_documents": 0,
                "error": "向量库未初始化"
            }
        
        try:
            stats = self.vector_store.get_collection_stats()
            if stats["total_documents"] == 0:
                logger.info("向量库为空，正在构建索引...")
                loader = DocumentLoader()
                chunks = loader.process_all_pdfs()
                if chunks:
                    self.vector_store.add_documents(chunks)
                    logger.info(f"已添加 {len(chunks)} 个文档片段到向量库")
                else:
                    logger.warning("未找到PDF文件，请将《计算机网络》课程资料放入知识库目录")
            else:
                logger.info(f"向量库已有 {stats['total_documents']} 个文档片段")
            return stats
        except Exception as e:
            logger.error(f"索引构建失败: {str(e)}")
            return {
                "total_documents": 0,
                "error": str(e)
            }

    def rebuild_index(self):
        if not self.initialized or not self.vector_store:
            return {"total_documents": 0, "error": "向量库未初始化"}
        
        try:
            self.vector_store.clear_collection()
            return self.ensure_index()
        except Exception as e:
            logger.error(f"索引重建失败: {str(e)}")
            return {"total_documents": 0, "error": str(e)}
