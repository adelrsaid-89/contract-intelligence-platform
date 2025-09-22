using Microsoft.Extensions.Options;
using Microsoft.Extensions.Logging;
using System.Text;
using System.Text.Json;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Infrastructure.Services;

public class AiServiceOptions
{
    public string BaseUrl { get; set; } = string.Empty;
    public string ApiKey { get; set; } = string.Empty;
    public int TimeoutSeconds { get; set; } = 120;
}

public class HttpAiService : IAiService
{
    private readonly HttpClient _httpClient;
    private readonly AiServiceOptions _options;
    private readonly ILogger<HttpAiService> _logger;

    public HttpAiService(HttpClient httpClient, IOptions<AiServiceOptions> options, ILogger<HttpAiService> logger)
    {
        _httpClient = httpClient;
        _options = options.Value;
        _logger = logger;

        _httpClient.BaseAddress = new Uri(_options.BaseUrl);
        _httpClient.Timeout = TimeSpan.FromSeconds(_options.TimeoutSeconds);

        if (!string.IsNullOrEmpty(_options.ApiKey))
        {
            _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_options.ApiKey}");
        }
    }

    public async Task<ContractExtractionResult> ExtractContractDataAsync(string fileContent, CancellationToken cancellationToken = default)
    {
        try
        {
            var request = new { content = fileContent };
            var json = JsonSerializer.Serialize(request);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("/api/extract/text", content, cancellationToken);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
            return JsonSerializer.Deserialize<ContractExtractionResult>(responseJson, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            }) ?? new ContractExtractionResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to extract contract data from text content");
            throw;
        }
    }

    public async Task<ContractExtractionResult> ExtractContractDataFromFileAsync(Stream fileStream, string fileName, CancellationToken cancellationToken = default)
    {
        try
        {
            using var form = new MultipartFormDataContent();
            using var streamContent = new StreamContent(fileStream);
            form.Add(streamContent, "file", fileName);

            var response = await _httpClient.PostAsync("/api/extract/file", form, cancellationToken);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
            return JsonSerializer.Deserialize<ContractExtractionResult>(responseJson, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            }) ?? new ContractExtractionResult();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to extract contract data from file: {FileName}", fileName);
            throw;
        }
    }
}