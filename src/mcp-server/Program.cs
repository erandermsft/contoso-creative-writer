using Azure.Identity;
using Azure.Monitor.OpenTelemetry.Exporter;
using McpPublishingToolServer.Messaging;
using McpPublishingToolServer.Tools;
using OpenTelemetry.Metrics;
using OpenTelemetry.Trace;
using Serilog;
using Serilog.Sinks.SystemConsole.Themes;

// This is to enable tracing for the Service Bus Azure SDK, currently in preview
AppContext.SetSwitch("Azure.Experimental.EnableActivitySource", true);

var builder = WebApplication.CreateBuilder(args);
builder.Configuration.AddJsonFile("appsettings.local.json", true);
builder.Configuration.AddEnvironmentVariables();
builder.Host.UseSerilog((context, configuration) =>
{
    configuration
        .ReadFrom.Configuration(context.Configuration)
        .Enrich.FromLogContext()
        .WriteTo.OpenTelemetry()
        .WriteTo.Console(theme: AnsiConsoleTheme.Sixteen);
});

// Service Bus Configuration
builder.AddAzureServiceBusClient("publishing_fullyQualifiedNamespace", settings =>
{
    if (builder.Configuration["AZURE_CLIENT_ID"] != null)
    {
        if (builder.Configuration["AZURE_TENANT_ID"] == null ||
            builder.Configuration["AZURE_CLIENT_SECRET"] == null)
        {
            settings.Credential = new ManagedIdentityCredential(ManagedIdentityId.FromUserAssignedClientId(builder.Configuration["AZURE_CLIENT_ID"]));
        }
        else
        {
            settings.Credential = new ClientSecretCredential(builder.Configuration["AZURE_TENANT_ID"], builder.Configuration["AZURE_CLIENT_ID"], builder.Configuration["AZURE_CLIENT_SECRET"]);
        }
    }
    else
    {
        settings.Credential = new DefaultAzureCredential();
    }
});
builder.Services.AddScoped<ServiceBusArticleEventSender>();

// OpenTelemetry Configuration
builder.Services.AddOpenTelemetry()
    .WithTracing(tracerProviderBuilder =>
    {
        tracerProviderBuilder
            .AddAspNetCoreInstrumentation()
            .AddHttpClientInstrumentation();

        var connectionString = builder.Configuration["APPINSIGHTS_CONNECTIONSTRING"] ?? builder.Configuration["APPLICATIONINSIGHTS_CONNECTION_STRING"];
        if (connectionString != null)
        {
            tracerProviderBuilder.AddAzureMonitorTraceExporter(options =>
            {
                options.ConnectionString = connectionString;
            });
        }
        var otelEndpoint = builder.Configuration["OTEL_EXPORTER_OTLP_ENDPOINT"];
        if (otelEndpoint != null)
        {
            tracerProviderBuilder.AddOtlpExporter();
        }
    })
    .WithMetrics(b => b
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter());

// MCP Configuration
builder.Services.AddMcpServer().WithHttpTransport()
    .WithTools<ArticlePublishingTool>();

var app = builder.Build();

app.MapMcp();

app.Run();