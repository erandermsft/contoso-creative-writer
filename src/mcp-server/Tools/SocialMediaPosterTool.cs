using System.ComponentModel;
using McpPublishingToolServer.Messaging;
using ModelContextProtocol.Server;

namespace McpPublishingToolServer.Tools;

[McpServerToolType]
public sealed class SocialMediaPosterTool
{
    [McpServerTool, Description("Post an influencer post to social media")]
    public static async Task<string> PostSocialMedia(
        ServiceBusSocialMediaEventSender eventSender,
        ILogger<SocialMediaPosterTool> logger,
        [Description("The target customer")] string customer,
        [Description("The social media post")] string socialMediaPost,
        CancellationToken cancellationToken)
    {
        logger.LogInformation("Posting influencer post to {Customer}", customer);
        
        try
        {
            var socialMediaEvent = new SocialMediaEvent
            {
                PostId = Guid.NewGuid().ToString(),
                PostContent = socialMediaPost,
                PublishTime = DateTimeOffset.UtcNow
            };
        
            await eventSender.SendAsync(socialMediaEvent, cancellationToken);
        
            logger.LogInformation("Social media post");
        
            return "Social media posted successfully at " + socialMediaEvent.PublishTime.ToString("s");
        }
        catch (Exception e)
        {
            logger.LogError(e, "Failed to post social media post");
            return "Failed to post social media post";
        }
    }
}