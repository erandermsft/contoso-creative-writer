import os
import logging
from typing import (
    Any,
    TextIO,
    Union,
    cast
)

from fastapi import FastAPI
from opentelemetry._events import set_event_logger_provider
from opentelemetry.sdk._events import EventLoggerProvider
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prompty.tracer import Tracer, PromptyTracer
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential    
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.ai.inference.tracing import AIInferenceInstrumentor 
from azure.ai.projects.telemetry.agents import AIAgentsInstrumentor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
import json
import contextlib
from opentelemetry import trace as oteltrace

_tracer = "prompty"
logger = logging.getLogger(__name__)

@contextlib.contextmanager
def trace_span(name: str):
    tracer = oteltrace.get_tracer(_tracer)
    with tracer.start_as_current_span(name) as span:
        yield lambda key, value: span.set_attribute(
            key, json.dumps(value).replace("\n", "")
        )

def setup_telemetry(app: FastAPI):

    otel_exporter_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
   
    # Get the connection string from the environment variables
    ai_project_conn_str = os.getenv("AZURE_LOCATION")+".api.azureml.ms;"+os.getenv(
        "AZURE_SUBSCRIPTION_ID")+";"+os.getenv("AZURE_RESOURCE_GROUP")+";"+os.getenv("AZURE_AI_PROJECT_NAME")
    
    # Configure OpenTelemetry using Azure AI Project 
    with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=ai_project_conn_str,
    ) as project_client:
        
        application_insights_connection_string = project_client.telemetry.get_connection_string()
        if not application_insights_connection_string:
            print("Application Insights was not enabled for this project.")
            print("Enable it via the 'Tracing' tab in your AI Foundry project page.")
            exit()

        if otel_exporter_endpoint:
            print("Exporting to OTLP endpoint")
            project_client.telemetry.enable(destination=otel_exporter_endpoint)     
        else:
            print("Exporting to Application Insights")
            configure_azure_monitor(connection_string=application_insights_connection_string)
            project_client.telemetry.enable(destination=None)     

        # Setting upp prompty tracer.
        json_tracer = PromptyTracer()
        Tracer.add("PromptyTracer", json_tracer.tracer)       
        Tracer.add("OpenTelemetry", trace_span)

        # Events: will be stored as logs in application insights
        event_provider = EventLoggerProvider()
        set_event_logger_provider(event_provider)  

    # Instrument FastAPI and exclude the send span to reduce noise
    FastAPIInstrumentor.instrument_app(app,exclude_spans=["send"])


def setup_telemetry_full(app: FastAPI):

    # Configuring exporters
    otel_exporter_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")

    if otel_exporter_endpoint:
        print("Exporting to OTLP endpoint")
        _setup_otel_exporter(destination=otel_exporter_endpoint)

    from azure.core.settings import settings

    settings.tracing_implementation = "OpenTelemetry"
    
    # Instrument AI APIs 
    AIInferenceInstrumentor().instrument() 
    AIAgentsInstrumentor().instrument()
    OpenAIInstrumentor().instrument()

    # Setting upp prompty tracer.
    json_tracer = PromptyTracer()
    Tracer.add("PromptyTracer", json_tracer.tracer)       
    Tracer.add("OpenTelemetry", trace_span)

    # Events: will be stored as logs in application insights
    event_provider = EventLoggerProvider()
    set_event_logger_provider(event_provider)  

    # Instrument FastAPI and exclude the send span to reduce noise
    FastAPIInstrumentor.instrument_app(app,exclude_spans=["send"])


def _setup_otel_exporter(destination: Union[TextIO, str, None]) -> Any:

    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

    _configure_logging(OTLPLogExporter(endpoint=destination))
    _configure_tracing(OTLPSpanExporter(endpoint=destination))

def _configure_logging(log_exporter: Any) -> None:
    if log_exporter is None:
        return

    try:
        # _events and _logs are considered beta (not internal) in
        # OpenTelemetry Python API/SDK.
        # So it's ok to use them for local development, but we'll swallow
        # any errors in case of any breaking changes on OTel side.
        from opentelemetry import _logs, _events
        from opentelemetry.sdk._logs import LoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._events import EventLoggerProvider  # pylint: disable=import-error,no-name-in-module
        from opentelemetry.sdk._logs.export import (
            SimpleLogRecordProcessor,
        )  # pylint: disable=import-error,no-name-in-module

        if not isinstance(_logs.get_logger_provider(), LoggerProvider):
            logger_provider = LoggerProvider()
            _logs.set_logger_provider(logger_provider)

        # get_logger_provider returns opentelemetry._logs.LoggerProvider
        # however, we have opentelemetry.sdk._logs.LoggerProvider, which implements
        # add_log_record_processor method, though we need to cast it to fix type checking.
        logger_provider = cast(LoggerProvider, _logs.get_logger_provider())
        logger_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
        _events.set_event_logger_provider(EventLoggerProvider(logger_provider))
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # since OTel logging is still in beta in Python, we're going to swallow any errors
        # and just warn about them.
        logger.warning("Failed to configure OpenTelemetry logging.", exc_info=ex)

def _configure_tracing(span_exporter: Any) -> None:
    if span_exporter is None:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "OpenTelemetry SDK is not installed. Please install it using 'pip install opentelemetry-sdk'"
        ) from e

    # if tracing was not setup before, we need to create a new TracerProvider
    if not isinstance(trace.get_tracer_provider(), TracerProvider):
        # If the provider is NoOpTracerProvider, we need to create a new TracerProvider
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    # get_tracer_provider returns opentelemetry.trace.TracerProvider
    # however, we have opentelemetry.sdk.trace.TracerProvider, which implements
    # add_span_processor method, though we need to cast it to fix type checking.
    provider = cast(TracerProvider, trace.get_tracer_provider())
    provider.add_span_processor(SimpleSpanProcessor(span_exporter))


    



    
    # application_insights_connection_string = os.getenv("APPINSIGHTS_CONNECTIONSTRING")
    # if application_insights_connection_string:
    #     print("Exporting to Application Insights")
    #     configure_azure_monitor(connection_string=application_insights_connection_string)