import pytest
from src.services.pipeline_service import PipelineService
from src.services.file_service import FileService

class TestPipeline:
    def test_pipeline_copies_files_to_processed(self, pipeline, settings):
        # Given: Source file exists
        source_file = settings.FLIGHT_EVENTS_DIR / "2022-10-03.csv"
        assert source_file.exists()
        
        # When: Pipeline runs
        pipeline.run()
        
        # Then: Source file should still exist
        assert source_file.exists()
        
        processed_file = settings.PROCESSED_DIR / "2022-10-03.csv"
        assert processed_file.exists()
