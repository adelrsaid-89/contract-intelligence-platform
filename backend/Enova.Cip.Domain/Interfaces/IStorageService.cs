namespace Enova.Cip.Domain.Interfaces;

public interface IStorageService
{
    Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType, CancellationToken cancellationToken = default);
    Task<Stream> DownloadFileAsync(string objectKey, CancellationToken cancellationToken = default);
    Task<bool> DeleteFileAsync(string objectKey, CancellationToken cancellationToken = default);
    Task<bool> FileExistsAsync(string objectKey, CancellationToken cancellationToken = default);
    Task<string> GetFileUrlAsync(string objectKey, TimeSpan? expiry = null, CancellationToken cancellationToken = default);
}