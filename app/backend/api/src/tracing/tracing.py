from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from traceloop.sdk import Traceloop


Traceloop.init()

resource = Resource(attributes={
    SERVICE_NAME: "sample-service"
})
traceProvider = TracerProvider(
    resource=resource
)
processor = BatchSpanProcessor(
    OTLPSpanExporter(
        endpoint="http://localhost:4318/v1/traces",
    )
)
traceProvider.add_span_processor(processor)

span_exporter = ConsoleSpanExporter()
traceProvider.add_span_processor(SimpleSpanProcessor(span_exporter))

# Sets the global default tracer provider
trace.set_tracer_provider(traceProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.sample")
