using Microsoft.Extensions.Options;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Infrastructure.Services;

public class LocalStorageOptions
{
    public string BasePath { get; set; } = "uploads";
    public string BaseUrl { get; set; } = "/files";
}

public class LocalFileStorageService : IStorageService
{
    private readonly LocalStorageOptions _options;

    public LocalFileStorageService(IOptions<LocalStorageOptions> options)
    {
        _options = options.Value;

        if (!Directory.Exists(_options.BasePath))
        {
            Directory.CreateDirectory(_options.BasePath);
        }
    }

    public async Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType, CancellationToken cancellationToken = default)
    {
        var objectKey = $"{DateTime.UtcNow:yyyy/MM/dd}/{Guid.NewGuid()}/{fileName}";
        var fullPath = Path.Combine(_options.BasePath, objectKey);
        var directory = Path.GetDirectoryName(fullPath);

        if (directory != null && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        using var fileStreamOut = File.Create(fullPath);
        await fileStream.CopyToAsync(fileStreamOut, cancellationToken);

        return objectKey;
    }

    public async Task<Stream> DownloadFileAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        var fullPath = Path.Combine(_options.BasePath, objectKey);

        if (!File.Exists(fullPath))
        {
            throw new FileNotFoundException($"File not found: {objectKey}");
        }

        var fileBytes = await File.ReadAllBytesAsync(fullPath, cancellationToken);
        return new MemoryStream(fileBytes);
    }

    public Task<bool> DeleteFileAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        try
        {
            var fullPath = Path.Combine(_options.BasePath, objectKey);

            if (File.Exists(fullPath))
            {
                File.Delete(fullPath);
                return Task.FromResult(true);
            }

            return Task.FromResult(false);
        }
        catch
        {
            return Task.FromResult(false);
        }
    }

    public Task<bool> FileExistsAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        var fullPath = Path.Combine(_options.BasePath, objectKey);
        return Task.FromResult(File.Exists(fullPath));
    }

    public Task<string> GetFileUrlAsync(string objectKey, TimeSpan? expiry = null, CancellationToken cancellationToken = default)
    {
        var url = $"{_options.BaseUrl}/{objectKey.Replace('\\', '/')}";
        return Task.FromResult(url);
    }
}