using Microsoft.Extensions.Options;
using Minio;
using Minio.DataModel.Args;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Infrastructure.Services;

public class MinioStorageOptions
{
    public string Endpoint { get; set; } = string.Empty;
    public string AccessKey { get; set; } = string.Empty;
    public string SecretKey { get; set; } = string.Empty;
    public string BucketName { get; set; } = string.Empty;
    public bool UseSSL { get; set; } = false;
}

public class MinioStorageService : IStorageService
{
    private readonly IMinioClient _minioClient;
    private readonly MinioStorageOptions _options;

    public MinioStorageService(IOptions<MinioStorageOptions> options)
    {
        _options = options.Value;
        _minioClient = new MinioClient()
            .WithEndpoint(_options.Endpoint)
            .WithCredentials(_options.AccessKey, _options.SecretKey);

        if (_options.UseSSL)
        {
            _minioClient.WithSSL();
        }

        _minioClient.Build();
    }

    public async Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType, CancellationToken cancellationToken = default)
    {
        var objectKey = $"{DateTime.UtcNow:yyyy/MM/dd}/{Guid.NewGuid()}/{fileName}";

        // Ensure bucket exists
        var bucketExistsArgs = new BucketExistsArgs().WithBucket(_options.BucketName);
        var found = await _minioClient.BucketExistsAsync(bucketExistsArgs, cancellationToken);
        if (!found)
        {
            var makeBucketArgs = new MakeBucketArgs().WithBucket(_options.BucketName);
            await _minioClient.MakeBucketAsync(makeBucketArgs, cancellationToken);
        }

        var putObjectArgs = new PutObjectArgs()
            .WithBucket(_options.BucketName)
            .WithObject(objectKey)
            .WithStreamData(fileStream)
            .WithObjectSize(fileStream.Length)
            .WithContentType(contentType);

        await _minioClient.PutObjectAsync(putObjectArgs, cancellationToken);
        return objectKey;
    }

    public async Task<Stream> DownloadFileAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        var memoryStream = new MemoryStream();

        var getObjectArgs = new GetObjectArgs()
            .WithBucket(_options.BucketName)
            .WithObject(objectKey)
            .WithCallbackStream(stream => stream.CopyTo(memoryStream));

        await _minioClient.GetObjectAsync(getObjectArgs, cancellationToken);
        memoryStream.Position = 0;
        return memoryStream;
    }

    public async Task<bool> DeleteFileAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        try
        {
            var removeObjectArgs = new RemoveObjectArgs()
                .WithBucket(_options.BucketName)
                .WithObject(objectKey);

            await _minioClient.RemoveObjectAsync(removeObjectArgs, cancellationToken);
            return true;
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> FileExistsAsync(string objectKey, CancellationToken cancellationToken = default)
    {
        try
        {
            var statObjectArgs = new StatObjectArgs()
                .WithBucket(_options.BucketName)
                .WithObject(objectKey);

            await _minioClient.StatObjectAsync(statObjectArgs, cancellationToken);
            return true;
        }
        catch
        {
            return false;
        }
    }

    public async Task<string> GetFileUrlAsync(string objectKey, TimeSpan? expiry = null, CancellationToken cancellationToken = default)
    {
        var expirySeconds = (int)(expiry?.TotalSeconds ?? 3600); // Default 1 hour

        var presignedGetObjectArgs = new PresignedGetObjectArgs()
            .WithBucket(_options.BucketName)
            .WithObject(objectKey)
            .WithExpiry(expirySeconds);

        return await _minioClient.PresignedGetObjectAsync(presignedGetObjectArgs);
    }
}