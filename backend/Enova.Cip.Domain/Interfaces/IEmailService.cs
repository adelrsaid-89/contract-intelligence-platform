namespace Enova.Cip.Domain.Interfaces;

public class EmailMessage
{
    public string To { get; set; } = string.Empty;
    public string Subject { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public bool IsHtml { get; set; } = true;
    public List<string> Cc { get; set; } = new();
    public List<string> Bcc { get; set; } = new();
}

public interface IEmailService
{
    Task SendEmailAsync(EmailMessage message, CancellationToken cancellationToken = default);
    Task SendBulkEmailAsync(IEnumerable<EmailMessage> messages, CancellationToken cancellationToken = default);
}