namespace McpPublishingToolServer.Messaging;

public class SocialMediaEvent
{
    public required string PostId { get; init; }
    public required string PostContent { get; init; }
    public required DateTimeOffset PublishTime { get; init; }
    public string Type => "SocialMediaEvent";
}