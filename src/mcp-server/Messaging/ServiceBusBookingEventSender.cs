using System.Text.Json;
using Azure.Messaging.ServiceBus;

namespace McpPublishingToolServer.Messaging;

public class ServiceBusArticleEventSender(ServiceBusClient client)
{
    private readonly ServiceBusSender _sender = client.CreateSender("published-articles");

    public async Task SendAsync(ArticlePublishingEvent articlePublishingEvent, CancellationToken cancellationToken = default)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(articlePublishingEvent));
        message.ApplicationProperties.Add("Type", articlePublishingEvent.Type);
        await _sender.SendMessageAsync(message, cancellationToken);
    }
}

public class ArticlePublishingEvent
{
    public required string ArticleId { get; init; }
    public required string ArticleContent { get; init; }
    public required DateTimeOffset PublishTime { get; init; }
    public string Type => "ArticlePublishingEvent";
}