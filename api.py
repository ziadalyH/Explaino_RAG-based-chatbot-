"""Flask API for RAG System."""

import logging
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.rag_system import RAGSystem
from src.config import Config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize RAG system
config = Config.from_env("config/config.example.yaml")
rag_system = RAGSystem(config)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "RAG System API"
    }), 200


@app.route('/query', methods=['POST'])
def query():
    """
    Query endpoint for asking questions.
    
    Request body:
    {
        "question": "What is OpenStax?"
    }
    
    Response:
    {
        "answer_type": "pdf" | "video" | "no_answer",
        "answer": "Generated answer text",
        "source": {
            "pdf_filename": "...",
            "page_number": 5,
            "paragraph_index": 2,
            "score": 0.95
        }
    }
    """
    try:
        # Get question from request
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "error": "Missing 'question' in request body"
            }), 400
        
        question = data['question']
        
        if not question or not question.strip():
            return jsonify({
                "error": "Question cannot be empty"
            }), 400
        
        logger.info(f"Received query: {question}")
        
        # Process query through RAG system
        response = rag_system.answer_question(question)
        
        # Format response based on type
        if response.answer_type == "pdf":
            return jsonify({
                "answer_type": "pdf",
                "answer": response.generated_answer,
                "source": {
                    "pdf_filename": response.pdf_filename,
                    "page_number": response.page_number,
                    "paragraph_index": response.paragraph_index,
                    "title": response.title,
                    "snippet": response.source_snippet,
                    "score": response.score,
                    "document_id": response.document_id
                }
            }), 200
        
        elif response.answer_type == "video":
            return jsonify({
                "answer_type": "video",
                "answer": response.generated_answer,
                "source": {
                    "video_id": response.video_id,
                    "start_timestamp": response.start_timestamp,
                    "end_timestamp": response.end_timestamp,
                    "start_token_id": response.start_token_id,
                    "end_token_id": response.end_token_id,
                    "transcript_snippet": response.transcript_snippet,
                    "score": response.score,
                    "document_id": response.document_id
                }
            }), 200
        
        else:  # no_answer
            # Load knowledge summary to provide suggestions
            summary = rag_system.knowledge_summary_generator.load_summary()
            
            response_data = {
                "answer_type": "no_answer",
                "answer": response.message,
                "suggestion": "The retrieved content wasn't relevant enough. Try rephrasing your question."
            }
            
            # Add knowledge summary if available
            if summary:
                response_data["knowledge_base"] = {
                    "overview": summary.get("overview", ""),
                    "topics": summary.get("topics", []),
                    "suggested_questions": summary.get("suggested_questions", [])
                }
            
            return jsonify(response_data), 200
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500


@app.route('/index/status', methods=['GET'])
def index_status():
    """Check if index exists and get statistics."""
    try:
        exists = rag_system.check_index_exists()
        
        if exists:
            indexed_pdfs, indexed_videos = rag_system._get_indexed_files()
            return jsonify({
                "index_exists": True,
                "statistics": {
                    "total_pdfs": len(indexed_pdfs),
                    "total_videos": len(indexed_videos),
                    "pdf_files": list(indexed_pdfs),
                    "video_ids": list(indexed_videos)
                }
            }), 200
        else:
            return jsonify({
                "index_exists": False,
                "message": "Index not found. Please build the index first."
            }), 200
    
    except Exception as e:
        logger.error(f"Error checking index status: {str(e)}")
        return jsonify({
            "error": "Failed to check index status",
            "message": str(e)
        }), 500


@app.route('/index/build', methods=['POST'])
def build_index():
    """
    Build or rebuild the index.
    
    Request body (optional):
    {
        "force_rebuild": true
    }
    """
    try:
        data = request.get_json() or {}
        force_rebuild = data.get('force_rebuild', False)
        
        logger.info(f"Starting index build (force_rebuild={force_rebuild})")
        
        # Build index
        rag_system.build_index(force_rebuild=force_rebuild)
        
        # Get final statistics
        indexed_pdfs, indexed_videos = rag_system._get_indexed_files()
        
        return jsonify({
            "status": "success",
            "message": "Index built successfully",
            "statistics": {
                "total_pdfs": len(indexed_pdfs),
                "total_videos": len(indexed_videos)
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error building index: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to build index",
            "message": str(e)
        }), 500


@app.route('/knowledge/summary', methods=['GET'])
def get_knowledge_summary():
    """
    Get knowledge summary and suggested questions.
    
    Response:
    {
        "overview": "Brief overview of topics...",
        "topics": ["Topic 1", "Topic 2", ...],
        "suggested_questions": ["Question 1?", "Question 2?", ...]
    }
    """
    try:
        summary = rag_system.knowledge_summary_generator.load_summary()
        
        if summary:
            return jsonify(summary), 200
        else:
            return jsonify({
                "error": "No knowledge summary available",
                "message": "Please build the index first to generate a knowledge summary."
            }), 404
    
    except Exception as e:
        logger.error(f"Error loading knowledge summary: {str(e)}")
        return jsonify({
            "error": "Failed to load knowledge summary",
            "message": str(e)
        }), 500


if __name__ == '__main__':
    logger.info("Starting RAG System API...")
    logger.info("API will be available at http://localhost:8000")
    logger.info("Endpoints:")
    logger.info("  GET  /health - Health check")
    logger.info("  POST /query - Ask a question")
    logger.info("  GET  /index/status - Check index status")
    logger.info("  POST /index/build - Build/rebuild index")
    logger.info("  GET  /knowledge/summary - Get knowledge summary and suggested questions")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
