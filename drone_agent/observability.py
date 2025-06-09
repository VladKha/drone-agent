import os
import base64
from dotenv import load_dotenv

load_dotenv()

def setup_observability():
    # Load environment variables
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

    # configure tracing
    LANGFUSE_AUTH = base64.b64encode(
        f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}".encode()
    ).decode()
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = LANGFUSE_HOST + "/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

    from opentelemetry.sdk.trace import TracerProvider
    from openinference.instrumentation.smolagents import SmolagentsInstrumentor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor

    # Create a TracerProvider for OpenTelemetry
    trace_provider = TracerProvider()

    # Add a SimpleSpanProcessor with the OTLPSpanExporter to send traces
    trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

    # Set the global default tracer provider
    from opentelemetry import trace

    trace.set_tracer_provider(trace_provider)
    tracer = trace.get_tracer(__name__)

    # Instrument smolagents with the configured provider
    SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

    # phoenix
    # from phoenix.otel import register
    # from openinference.instrumentation.smolagents import SmolagentsInstrumentor
    #
    # register()
    # SmolagentsInstrumentor().instrument()
