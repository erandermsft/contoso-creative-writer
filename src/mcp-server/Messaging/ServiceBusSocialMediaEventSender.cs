using System.Text.Json;
using Azure.Messaging.ServiceBus;

namespace McpPublishingToolServer.Messaging;

public class ServiceBusSocialMediaEventSender
{
    private readonly ServiceBusSender _sender;

    public ServiceBusSocialMediaEventSender(ServiceBusClient client)
    {
        _sender = client.CreateSender("social-media-posts");
    }

    public async Task SendAsync(SocialMediaEvent socialMediaEvent, CancellationToken cancellationToken = default)
    {
        var message = new ServiceBusMessage(JsonSerializer.Serialize(socialMediaEvent));
        message.ApplicationProperties.Add("Type", socialMediaEvent.Type);
        await _sender.SendMessageAsync(message, cancellationToken);
    }
}