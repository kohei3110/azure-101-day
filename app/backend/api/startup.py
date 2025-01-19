import os
import logging
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile
from apscheduler.schedulers.background import BackgroundScheduler

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from services.code_interpreter_service import CodeInterpreterService

logging.basicConfig(
    level=logging.DEBUG
)

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

# Sets the global default tracer provider
trace.set_tracer_provider(traceProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="http://localhost:4318/v1/metrics")
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("my.tracer.sample")

app = FastAPI()

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))

def delete_files():
    """Delete all files in the data directory."""
    with tracer.start_as_current_span("delete_files"):
        for file in DATA_DIR.iterdir():
            if file.is_file():
                print(f"Deleting {file}")
                os.remove(file)

scheduler = BackgroundScheduler()
scheduler.add_job(delete_files, 'interval', seconds=30)
scheduler.start()

project_client: AIProjectClient = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

code_interpreter_service = CodeInterpreterService(project_client)

import controller
app.include_router(controller.router)