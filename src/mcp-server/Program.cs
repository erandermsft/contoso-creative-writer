using Azure.Identity;
using McpPublishingToolServer.Messaging;
using McpPublishingToolServer.Tools;
using OpenTelemetry;
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
builder.AddAzureServiceBusClient("publishing_fullyQualifiedNamespace", settings => settings.Credential
    = new ChainedTokenCredential(
        new ManagedIdentityCredential(), 
        new ClientSecretCredential(builder.Configuration["AZURE_TENANT_ID"], builder.Configuration["AZURE_CLIENT_ID"], builder.Configuration["AZURE_CLIENT_SECRET"])));
builder.Services.AddSingleton<ServiceBusArticleEventSender>();

// OpenTelemetry Configuration
builder.Services.AddOpenTelemetry()
    .WithTracing(b => b.AddSource("*")
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation())
    .WithMetrics(b => b.AddMeter("*")
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation())
    .UseOtlpExporter();

// MCP Configuration
builder.Services.AddMcpServer().WithHttpTransport()
    .WithTools<ArticlePublishingTool>();

var app = builder.Build();

app.MapMcp();

app.MapGet("testing", async (ServiceBusArticleEventSender sender) =>
{
    // This is just a test to send an event to the Service Bus
    var articleEvent = new ArticlePublishingEvent
    {
        ArticleId = Guid.NewGuid().ToString(),
        ArticleContent = "Test content",
        PublishTime = DateTimeOffset.UtcNow
    };
    await sender.SendAsync(articleEvent);
    return Results.Ok();
});
app.Run();
