namespace McpPublishingToolServer.Messaging;

public class ArticlePublishingEvent
{
    public required string ArticleId { get; init; }
    public required string ArticleContent { get; init; }
    public required DateTimeOffset PublishTime { get; init; }
    public string Type => "ArticlePublishingEvent";
}