from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import logging
import json

class TelemetryManager:
    def __init__(self):
        # Initialize tracer
        trace.set_tracer_provider(TracerProvider())
        otlp_exporter = OTLPSpanExporter(
            endpoint="http://collector:4317"
        )
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        # Initialize logger
        self.logger = logging.getLogger("STARK.ML")
        self.logger.setLevel(logging.INFO)
        
    def log_ml_prediction(self, model_name, input_data, prediction, confidence):
        with trace.get_tracer(__name__).start_as_current_span("ml_prediction") as span:
            span.set_attribute("model.name", model_name)
            span.set_attribute("prediction.confidence", confidence)
            
            self.logger.info(
                "ML Prediction",
                extra={
                    "model_name": model_name,
                    "confidence": confidence,
                    "prediction": json.dumps(prediction)
                }
            )
    
    def log_model_metrics(self, metrics):
        with trace.get_tracer(__name__).start_as_current_span("model_metrics") as span:
            span.set_attribute("metrics", json.dumps(metrics))
            
            self.logger.info(
                "Model Metrics Updated",
                extra={"metrics": metrics}
            )