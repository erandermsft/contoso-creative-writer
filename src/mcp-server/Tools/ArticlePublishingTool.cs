using System.ComponentModel;
using System.Text.Encodings.Web;
using McpPublishingToolServer.Messaging;
using ModelContextProtocol.Server;

namespace McpPublishingToolServer.Tools;

[McpServerToolType]
public sealed class ArticlePublishingTool
{
    [McpServerTool, Description("Publish an article")]
    public static async Task<string> PublishArticle(
        ServiceBusArticleEventSender eventSender,
        ILogger<ArticlePublishingTool> logger,
        [Description("The article")]
        string article)
    {
        logger.LogInformation("Publishing article {Article}", article);

        try
        {
            var articleEvent = new ArticlePublishingEvent
            {
                ArticleId = Guid.NewGuid().ToString(),
                ArticleContent = article,
                PublishTime = DateTimeOffset.UtcNow
            };

            await eventSender.SendAsync(articleEvent);

            logger.LogInformation("Article published successfully");

            return "Published successfully at " + articleEvent.PublishTime.ToString("s");
        }
        catch (Exception e)
        {
            logger.LogError(e, "Failed to publish article");
            return "Failed to publish article";
        }
    }
}