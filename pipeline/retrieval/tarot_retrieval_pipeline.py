"""
Tarot Retrieval Pipeline for Digital Human Server
Implements RAG (Retrieval Augmented Generation) for tarot knowledge
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.template_node_pipeline import TemplateNodePipeline
from logs import logger
from typing import Dict, Any, List, Optional, Tuple
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import re

class TarotRetrievalPipeline(TemplateNodePipeline):
    """
    Pipeline for retrieving relevant tarot information using RAG approach
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.stage = "Tarot Retrieval"
        self.config = config or {}
        
        # Initialize components
        self.vectorizer = None
        self.card_vectors = None
        self.card_database = []
        self.conversation_database = []
        
        # Load tarot data
        self._load_tarot_database()
        self._build_vector_index()
        
    def initiate(self):
        """Main pipeline execution for retrieval"""
        try:
            logger.info("Starting Tarot Retrieval Pipeline")
            
            # Get query input
            input_data = self.get_query_input()
            
            # Perform retrieval
            retrieval_results = self.retrieve_relevant_information(input_data)
            
            # Format results for downstream pipeline
            formatted_results = self.format_retrieval_results(retrieval_results)
            
            logger.info("Tarot Retrieval Pipeline completed successfully")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in Tarot Retrieval Pipeline: {e}")
            raise e
    
    def get_query_input(self) -> Dict[str, Any]:
        """Get query input for retrieval"""
        # In production, this would come from previous pipeline stage
        return {
            "user_query": "Ý nghĩa lá bài The Fool trong tình yêu là gì?",
            "query_type": "card_meaning",
            "context": {
                "topic": "love",
                "card_mentioned": "The Fool"
            }
        }
    
    def _load_tarot_database(self):
        """Load tarot data from JSON file"""
        try:
            data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tarot_dataset.json")
            
            with open(data_path, 'r', encoding='utf-8') as f:
                tarot_data = json.load(f)
            
            # Process cards data
            all_cards = []
            
            # Major Arcana
            for card in tarot_data.get("tarot_cards", {}).get("major_arcana", []):
                all_cards.append({
                    "type": "major_arcana",
                    "name": card["name"],
                    "content": self._create_card_content(card),
                    "metadata": card
                })
            
            # Minor Arcana
            for suit in ["cups", "wands", "swords", "pentacles"]:
                for card in tarot_data.get("tarot_cards", {}).get(suit, []):
                    all_cards.append({
                        "type": f"minor_arcana_{suit}",
                        "name": card["name"],
                        "content": self._create_card_content(card),
                        "metadata": card
                    })
            
            self.card_database = all_cards
            
            # Load conversation samples
            self.conversation_database = tarot_data.get("conversation_samples", [])
            
            logger.info(f"Loaded {len(self.card_database)} cards and {len(self.conversation_database)} conversation samples")
            
        except FileNotFoundError:
            logger.warning("Tarot dataset file not found. Using minimal data.")
            self._create_minimal_database()
        except Exception as e:
            logger.error(f"Error loading tarot database: {e}")
            self._create_minimal_database()
    
    def _create_card_content(self, card: Dict[str, Any]) -> str:
        """Create searchable content from card data"""
        content_parts = [
            card.get("name", ""),
            " ".join(card.get("keywords_upright", [])),
            " ".join(card.get("keywords_reversed", [])), 
            card.get("meaning_upright", ""),
            card.get("meaning_reversed", ""),
            card.get("description", ""),
            " ".join(card.get("questions", []))
        ]
        
        return " ".join(filter(None, content_parts))
    
    def _create_minimal_database(self):
        """Create minimal database for testing"""
        self.card_database = [
            {
                "type": "major_arcana",
                "name": "The Fool",
                "content": "The Fool new beginnings innocence adventure leap faith khởi đầu mới ngây thơ phiêu lưu",
                "metadata": {
                    "name": "The Fool",
                    "keywords_upright": ["new beginnings", "innocence"],
                    "meaning_upright": "Khởi đầu mới đầy tiềm năng"
                }
            }
        ]
        self.conversation_database = []
    
    def _build_vector_index(self):
        """Build TF-IDF vector index for retrieval"""
        try:
            # Combine all searchable content
            all_content = [card["content"] for card in self.card_database]
            
            if not all_content:
                logger.warning("No content available for vector indexing")
                return
            
            # Initialize TF-IDF vectorizer with Vietnamese text support
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=None,  # Could add Vietnamese stop words
                lowercase=True
            )
            
            # Fit and transform content
            self.card_vectors = self.vectorizer.fit_transform(all_content)
            
            logger.info(f"Built vector index with {self.card_vectors.shape[0]} documents")
            
        except Exception as e:
            logger.error(f"Error building vector index: {e}")
            self.vectorizer = None
            self.card_vectors = None
    
    def retrieve_relevant_information(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant tarot information based on query"""
        user_query = input_data.get("user_query", "")
        query_type = input_data.get("query_type", "general")
        context = input_data.get("context", {})
        
        results = {
            "query": user_query,
            "relevant_cards": [],
            "similar_conversations": [],
            "suggestions": []
        }
        
        if not self.vectorizer or self.card_vectors is None:
            logger.warning("Vector index not available, using fallback retrieval")
            return self._fallback_retrieval(user_query, context)
        
        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([user_query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.card_vectors)[0]
            
            # Get top relevant cards
            top_indices = np.argsort(similarities)[::-1][:5]  # Top 5 matches
            
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    card_data = self.card_database[idx]
                    results["relevant_cards"].append({
                        "card": card_data,
                        "similarity": float(similarities[idx]),
                        "relevance_reason": self._explain_relevance(user_query, card_data)
                    })
            
            # Add conversation samples if relevant
            results["similar_conversations"] = self._find_similar_conversations(user_query)
            
            # Generate suggestions
            results["suggestions"] = self._generate_suggestions(user_query, context, results["relevant_cards"])
            
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return self._fallback_retrieval(user_query, context)
        
        return results
    
    def _fallback_retrieval(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback retrieval using simple keyword matching"""
        query_lower = query.lower()
        relevant_cards = []
        
        for card in self.card_database:
            card_name_lower = card["name"].lower()
            if card_name_lower in query_lower or any(
                keyword.lower() in query_lower 
                for keyword in card["metadata"].get("keywords_upright", [])
            ):
                relevant_cards.append({
                    "card": card,
                    "similarity": 0.8,  # Fixed similarity for fallback
                    "relevance_reason": f"Khớp từ khóa với '{card['name']}'"
                })
        
        return {
            "query": query,
            "relevant_cards": relevant_cards[:3],  # Limit to top 3
            "similar_conversations": [],
            "suggestions": ["Hãy hỏi về ý nghĩa cụ thể của lá bài", "Thử rút bài để được tư vấn"]
        }
    
    def _explain_relevance(self, query: str, card_data: Dict[str, Any]) -> str:
        """Explain why a card is relevant to the query"""
        card_name = card_data["name"]
        
        # Simple relevance explanation
        if card_name.lower() in query.lower():
            return f"Được đề cập trực tiếp trong câu hỏi"
        
        keywords = card_data["metadata"].get("keywords_upright", [])
        matching_keywords = [kw for kw in keywords if kw.lower() in query.lower()]
        
        if matching_keywords:
            return f"Liên quan qua từ khóa: {', '.join(matching_keywords)}"
        
        return "Có nội dung tương tự với câu hỏi"
    
    def _find_similar_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Find similar conversation samples"""
        similar_conversations = []
        query_lower = query.lower()
        
        for conv in self.conversation_database:
            user_question = conv.get("user_question", "").lower()
            
            # Simple similarity check
            common_words = set(query_lower.split()) & set(user_question.split())
            if len(common_words) >= 2:  # At least 2 common words
                similar_conversations.append({
                    "conversation": conv,
                    "similarity": len(common_words) / max(len(query_lower.split()), len(user_question.split()))
                })
        
        # Sort by similarity
        similar_conversations.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_conversations[:2]  # Top 2 similar conversations
    
    def _generate_suggestions(self, query: str, context: Dict[str, Any], relevant_cards: List[Dict]) -> List[str]:
        """Generate helpful suggestions based on query and results"""
        suggestions = []
        
        if not relevant_cards:
            suggestions.extend([
                "Thử hỏi về ý nghĩa của một lá bài cụ thể",
                "Yêu cầu rút bài tarot để được tư vấn",
                "Hỏi về các loại bài trí khác nhau"
            ])
        else:
            topic = context.get("topic", "")
            if topic == "love":
                suggestions.append("Thử bài trí 'Tam giác tình yêu' để hiểu rõ hơn")
            elif topic == "career":
                suggestions.append("Xem xét bài trí 'Con đường sự nghiệp'")
            else:
                suggestions.append("Rút thêm lá bài để có cái nhìn toàn diện hơn")
            
            # Add card-specific suggestions
            for result in relevant_cards[:2]:
                card_name = result["card"]["name"]
                suggestions.append(f"Tìm hiểu thêm về vị trí nghịch của {card_name}")
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def format_retrieval_results(self, retrieval_results: Dict[str, Any]) -> Dict[str, Any]:
        """Format retrieval results for downstream pipeline"""
        return {
            "retrieval_query": retrieval_results["query"],
            "context_cards": [
                {
                    "card_name": result["card"]["name"],
                    "card_data": result["card"]["metadata"],
                    "relevance_score": result["similarity"],
                    "reason": result["relevance_reason"]
                }
                for result in retrieval_results["relevant_cards"]
            ],
            "conversation_examples": retrieval_results["similar_conversations"],
            "suggestions": retrieval_results["suggestions"],
            "retrieval_success": len(retrieval_results["relevant_cards"]) > 0
        }

# Demo usage
if __name__ == "__main__":
    print("=== Testing Tarot Retrieval Pipeline ===")
    
    retrieval_pipeline = TarotRetrievalPipeline()
    results = retrieval_pipeline.initiate()
    
    print(json.dumps(results, ensure_ascii=False, indent=2))
