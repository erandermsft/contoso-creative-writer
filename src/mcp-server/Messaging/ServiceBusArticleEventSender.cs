using System.Text.Json;
using Azure.Messaging.ServiceBus;

namespace McpPublishingToolServer.Messaging;

public class ServiceBusArticleEventSender
{
    private readonly ServiceBusSender _sender;

    public ServiceBusArticleEventSender(ServiceBusClient client)
    {
        _sender = client.CreateSender("published-articles");
    }

    public async Task SendAsync(ArticlePublishingEvent articlePublishingEvent, CancellationToken cancellationToken = default)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(articlePublishingEvent));
        message.ApplicationProperties.Add("Type", articlePublishingEvent.Type);
        await _sender.SendMessageAsync(message, cancellationToken);
    }
}