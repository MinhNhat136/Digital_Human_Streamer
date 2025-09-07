"""
Tarot Reading Pipeline for Digital Human Server
Integrates with the main pipeline architecture to provide tarot reading capabilities
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.template_node_pipeline import TemplateNodePipeline
from components.tarot_knowledge import TarotKnowledge, TarotSpread
from logs import logger
from typing import Dict, Any, List, Optional
import json

class TarotReadingPipeline(TemplateNodePipeline):
    """
    Pipeline chuyên xử lý yêu cầu xem tarot
    Tích hợp với kiến trúc pipeline hiện có
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.stage = "Tarot Reading"
        self.config = config or {}
        self.tarot_knowledge = TarotKnowledge()
        
    def initiate(self):
        """Main pipeline execution"""
        try:
            logger.info("Starting Tarot Reading Pipeline")
            
            # Get input from previous pipeline stage or direct input
            input_data = self.get_input_data()
            
            # Process tarot reading request
            result = self.process_tarot_request(input_data)
            
            # Save result for next pipeline stage
            self.save_output_data(result)
            
            logger.info("Tarot Reading Pipeline completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in Tarot Reading Pipeline: {e}")
            raise e
    
    def get_input_data(self) -> Dict[str, Any]:
        """Get input data from previous pipeline or direct input"""
        # In a real implementation, this would get data from the previous pipeline stage
        # For demo purposes, we'll use sample data
        return {
            "user_question": "Tình yêu của tôi sẽ ra sao trong năm tới?",
            "spread_type": "three_card",
            "user_context": {
                "age_range": "20-30",
                "topic": "love"
            }
        }
    
    def process_tarot_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the tarot reading request"""
        question = input_data.get("user_question", "")
        spread_type = input_data.get("spread_type", "single_card")
        user_context = input_data.get("user_context", {})
        
        # Determine number of cards based on spread type
        spread_info = TarotSpread.get_spread_info(spread_type)
        num_cards = len(spread_info["positions"])
        
        # Draw cards
        drawn_cards = self.tarot_knowledge.draw_cards(num_cards, spread_type)
        
        # Generate interpretation
        interpretation = self.tarot_knowledge.interpret_reading(drawn_cards, question)
        
        # Create structured response
        response = {
            "question": question,
            "spread_type": spread_type,
            "spread_description": spread_info["description"],
            "cards": [
                {
                    "position": card.position,
                    "card_name": card.card.name,
                    "orientation": card.orientation.value,
                    "meaning": card.card.get_meaning(card.orientation),
                    "keywords": card.card.get_keywords(card.orientation)
                }
                for card in drawn_cards
            ],
            "interpretation": interpretation,
            "advice": self.generate_advice(drawn_cards, user_context),
            "timestamp": self.get_current_timestamp()
        }
        
        return response
    
    def generate_advice(self, drawn_cards: List, user_context: Dict[str, Any]) -> str:
        """Generate personalized advice based on cards and user context"""
        topic = user_context.get("topic", "general")
        
        if topic == "love":
            advice = "💕 Trong tình yêu, hãy mở lòng và tin tương vào những cơ hội mới. "
        elif topic == "career":
            advice = "🎯 Về sự nghiệp, đây là thời điểm để bạn tập trung vào mục tiêu và hành động quyết đoán. "
        else:
            advice = "🌟 Dựa trên các lá bài, bạn đang ở một giai đoạn quan trọng trong cuộc đời. "
        
        advice += "Hãy tin vào trực giác của mình và đừng ngại thay đổi khi cần thiết."
        
        return advice
    
    def save_output_data(self, result: Dict[str, Any]):
        """Save output for next pipeline stage"""
        # In a real implementation, this would save to a shared data store
        output_file = "tarot_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Tarot reading result saved to {output_file}")
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

class TarotConversationPipeline(TemplateNodePipeline):
    """
    Pipeline xử lý hội thoại về tarot - tích hợp với LLM pipeline
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.stage = "Tarot Conversation"
        self.config = config or {}
        self.tarot_knowledge = TarotKnowledge()
        
    def initiate(self):
        """Execute conversation pipeline"""
        try:
            logger.info("Starting Tarot Conversation Pipeline")
            
            # Get conversation context
            input_data = self.get_conversation_input()
            
            # Generate contextual tarot response
            response = self.generate_tarot_response(input_data)
            
            # Format for LLM pipeline
            formatted_response = self.format_for_llm(response)
            
            logger.info("Tarot Conversation Pipeline completed")
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in Tarot Conversation Pipeline: {e}")
            raise e
    
    def get_conversation_input(self) -> Dict[str, Any]:
        """Get conversation input"""
        return {
            "user_message": "Bạn có thể giải thích ý nghĩa lá bài The Fool không?",
            "conversation_history": [],
            "user_profile": {
                "tarot_experience": "beginner",
                "interests": ["spirituality", "self_development"]
            }
        }
    
    def generate_tarot_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual response about tarot"""
        user_message = input_data.get("user_message", "")
        user_profile = input_data.get("user_profile", {})
        
        # Simple keyword-based response (in production, use more sophisticated NLP)
        if "the fool" in user_message.lower():
            card = self.tarot_knowledge.get_card_by_name("The Fool")
            if card:
                response_text = f"""
🃏 **Lá bài The Fool (Kẻ Ngốc)**

{card.description}

**Ý nghĩa thuận:**
{card.meaning_upright}

**Ý nghĩa nghịch:**  
{card.meaning_reversed}

**Từ khóa chính:** {', '.join(card.keywords_upright)}

Đây là lá bài mở đầu hành trình tarot, tượng trưng cho những khởi đầu mới và tinh thần phiêu lưu!
                """.strip()
            else:
                response_text = "Xin lỗi, tôi không tìm thấy thông tin về lá bài này."
        else:
            response_text = "Tôi có thể giúp bạn hiểu về các lá bài tarot, trải bài, hoặc giải đáp thắc mắc về tarot. Bạn muốn hỏi về điều gì?"
        
        return {
            "response_text": response_text,
            "response_type": "tarot_explanation",
            "confidence": 0.9
        }
    
    def format_for_llm(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Format response for LLM pipeline consumption"""
        return {
            "tarot_context": response,
            "system_prompt": "Bạn là một thầy bói tarot chuyên nghiệp và thân thiện.",
            "response_ready": True
        }

# Demo usage
if __name__ == "__main__":
    # Test Tarot Reading Pipeline
    print("=== Testing Tarot Reading Pipeline ===")
    tarot_pipeline = TarotReadingPipeline()
    result = tarot_pipeline.initiate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + "="*60 + "\n")
    
    # Test Tarot Conversation Pipeline  
    print("=== Testing Tarot Conversation Pipeline ===")
    conversation_pipeline = TarotConversationPipeline()
    conv_result = conversation_pipeline.initiate()
    print(json.dumps(conv_result, ensure_ascii=False, indent=2))
