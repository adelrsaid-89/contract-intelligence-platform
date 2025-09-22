using Microsoft.Extensions.Options;
using Microsoft.Extensions.Logging;
using System.Net;
using System.Net.Mail;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Infrastructure.Services;

public class SmtpOptions
{
    public string Host { get; set; } = string.Empty;
    public int Port { get; set; } = 587;
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public bool EnableSsl { get; set; } = true;
    public string FromEmail { get; set; } = string.Empty;
    public string FromName { get; set; } = string.Empty;
}

public class SmtpEmailService : IEmailService
{
    private readonly SmtpOptions _options;
    private readonly ILogger<SmtpEmailService> _logger;

    public SmtpEmailService(IOptions<SmtpOptions> options, ILogger<SmtpEmailService> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public async Task SendEmailAsync(EmailMessage message, CancellationToken cancellationToken = default)
    {
        try
        {
            using var client = CreateSmtpClient();
            using var mailMessage = CreateMailMessage(message);

            await client.SendMailAsync(mailMessage, cancellationToken);
            _logger.LogInformation("Email sent successfully to {To}", message.To);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email to {To}", message.To);
            throw;
        }
    }

    public async Task SendBulkEmailAsync(IEnumerable<EmailMessage> messages, CancellationToken cancellationToken = default)
    {
        using var client = CreateSmtpClient();

        foreach (var message in messages)
        {
            try
            {
                using var mailMessage = CreateMailMessage(message);
                await client.SendMailAsync(mailMessage, cancellationToken);
                _logger.LogInformation("Email sent successfully to {To}", message.To);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send email to {To}", message.To);
                // Continue with other emails even if one fails
            }
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        var client = new SmtpClient(_options.Host, _options.Port)
        {
            EnableSsl = _options.EnableSsl,
            UseDefaultCredentials = false,
            Credentials = new NetworkCredential(_options.Username, _options.Password)
        };

        return client;
    }

    private MailMessage CreateMailMessage(EmailMessage message)
    {
        var mailMessage = new MailMessage
        {
            From = new MailAddress(_options.FromEmail, _options.FromName),
            Subject = message.Subject,
            Body = message.Body,
            IsBodyHtml = message.IsHtml
        };

        mailMessage.To.Add(message.To);

        foreach (var cc in message.Cc)
        {
            mailMessage.CC.Add(cc);
        }

        foreach (var bcc in message.Bcc)
        {
            mailMessage.Bcc.Add(bcc);
        }

        return mailMessage;
    }
}