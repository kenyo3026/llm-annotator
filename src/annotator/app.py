"""
FastAPI-based API interface for LLM Tag Annotator
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from dataclasses import asdict

from .main import Main
from .annotator import AnnotationResponse
from .utils import resolve_config_path


# Pydantic models for request/response
class AnnotateRequest(BaseModel):
    """Request model for annotation"""
    context: str = Field(..., description="Text context to annotate", examples=["今天美股如何"])
    annotator: Optional[str] = Field(
        None,
        description="Annotator name to use. Leave empty or null to use first annotator in config.",
        examples=["stock-chat-tagging", "open-tagging"]
    )
    model: Optional[str] = Field(
        None,
        description="Model name to use. Leave empty or null to use first model in config.",
        examples=["gemini-flash"]
    )

    @field_validator('annotator', 'model', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None"""
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return None
        return v


class AnnotateResponse(BaseModel):
    """Response model for annotation"""
    tags: List[str] = Field(..., description="List of assigned tags")
    status: str = Field(..., description="Annotation status (success/error)")
    confidence: Optional[float] = Field(None, description="Confidence score if available")
    metadata: Optional[dict] = Field(None, description="Additional metadata from annotation")


class ListResponse(BaseModel):
    """Response model for listing annotators/models"""
    annotators: List[str] = Field(..., description="List of available annotator names")
    models: List[str] = Field(..., description="List of available model names")


class AnnotatorsResponse(BaseModel):
    """Response model for listing annotators only"""
    annotators: List[str] = Field(..., description="List of available annotator names")


class ModelsResponse(BaseModel):
    """Response model for listing models only"""
    models: List[str] = Field(..., description="List of available model names")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="API health status")
    version: str = Field(..., description="API version")


def create_app(config_path: str = "configs/config.yaml") -> FastAPI:
    """
    Create and configure FastAPI application

    Args:
        config_path: Path to configuration file

    Returns:
        Configured FastAPI application
    """
    # Resolve config path
    config_path = resolve_config_path(config_path)

    app = FastAPI(
        title="LLM Tag Annotator API",
        description="API for LLM-based multi-label text annotation",
        version="0.1.0",
    )

    # Initialize Main instance
    try:
        main = Main(config_path=config_path)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize annotator: {e}")

    @app.get("/", response_model=HealthResponse)
    async def health_check():
        """Health check endpoint"""
        return HealthResponse(
            status="healthy",
            version="0.1.0"
        )

    @app.get("/list", response_model=ListResponse)
    async def list_resources():
        """
        List all available annotators and models

        Returns:
            List of annotator names and model names
        """
        try:
            annotators = main.list_annotators()
            models = main.list_models()
            return ListResponse(
                annotators=annotators,
                models=models
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/annotators", response_model=AnnotatorsResponse)
    async def get_annotators():
        """
        Get all available annotators

        Returns:
            List of annotator names
        """
        try:
            annotators = main.list_annotators()
            return AnnotatorsResponse(annotators=annotators)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/models", response_model=ModelsResponse)
    async def get_models():
        """
        Get all available models

        Returns:
            List of model names
        """
        try:
            models = main.list_models()
            return ModelsResponse(models=models)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/annotate", response_model=AnnotateResponse)
    async def annotate(request: AnnotateRequest):
        """
        Annotate text with tags

        Args:
            request: AnnotateRequest with context and optional annotator/model names

        Returns:
            AnnotateResponse with tags and metadata
        """
        try:
            result: AnnotationResponse = main.annotate(
                context=request.context,
                annotator_name=request.annotator,
                model_name=request.model
            )

            # Convert metadata to dict if present
            metadata_dict = None
            if result.metadata:
                metadata_dict = asdict(result.metadata)

            return AnnotateResponse(
                tags=result.tags,
                status=result.status,
                confidence=result.confidence,
                metadata=metadata_dict
            )

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/annotate", response_model=AnnotateResponse)
    async def annotate_get(
        context: str = Query(..., description="Text context to annotate"),
        annotator: Optional[str] = Query(None, description="Annotator name to use"),
        model: Optional[str] = Query(None, description="Model name to use")
    ):
        """
        Annotate text with tags (GET method for simple queries)

        Args:
            context: Text context to annotate
            annotator: Optional annotator name (empty string will be treated as None)
            model: Optional model name (empty string will be treated as None)

        Returns:
            AnnotateResponse with tags and metadata
        """
        # Convert empty strings to None for GET requests
        if annotator == "":
            annotator = None
        if model == "":
            model = None

        request = AnnotateRequest(
            context=context,
            annotator=annotator,
            model=model
        )
        return await annotate(request)

    return app


# Create default app instance
app = create_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    config_path: str = "configs/config.yaml",
    reload: bool = False
):
    """
    Run the FastAPI server

    Args:
        host: Host to bind to
        port: Port to bind to
        config_path: Path to configuration file
        reload: Enable auto-reload for development
    """
    import uvicorn

    # Create app with custom config path
    app = create_app(config_path=config_path)

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload
    )


def main():
    """
    Main entry point for annotator-api command
    """
    import argparse

    parser = argparse.ArgumentParser(description="Run LLM Tag Annotator API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("-c", "--config", default="configs/config.yaml", help="Path to config file")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        config_path=args.config,
        reload=args.reload
    )


if __name__ == "__main__":
    # For direct execution: python -m annotator.app
    main()
