using Microsoft.Extensions.Options;
using Nest;
using Enova.Cip.Domain.Interfaces;

namespace Enova.Cip.Infrastructure.Services;

public class ElasticsearchOptions
{
    public string Url { get; set; } = "http://localhost:9200";
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}

public class ElasticsearchService : ISearchService
{
    private readonly IElasticClient _client;

    public ElasticsearchService(IOptions<ElasticsearchOptions> options)
    {
        var settings = new ConnectionSettings(new Uri(options.Value.Url));

        if (!string.IsNullOrEmpty(options.Value.Username) && !string.IsNullOrEmpty(options.Value.Password))
        {
            settings.BasicAuthentication(options.Value.Username, options.Value.Password);
        }

        _client = new ElasticClient(settings);
    }

    public async Task<SearchResult<T>> SearchAsync<T>(string indexName, string query, int page = 1, int pageSize = 20, CancellationToken cancellationToken = default) where T : class
    {
        var from = (page - 1) * pageSize;

        var searchResponse = await _client.SearchAsync<T>(s => s
            .Index(indexName)
            .Query(q => q
                .QueryString(qs => qs
                    .Query(query)
                    .DefaultOperator(Operator.And)
                )
            )
            .From(from)
            .Size(pageSize)
        );

        return new SearchResult<T>
        {
            Items = searchResponse.Documents,
            TotalCount = searchResponse.Total,
            Page = page,
            PageSize = pageSize
        };
    }

    public async Task IndexDocumentAsync<T>(string indexName, string documentId, T document, CancellationToken cancellationToken = default) where T : class
    {
        await _client.IndexDocumentAsync(document, idx => idx
            .Index(indexName)
            .Id(documentId)
        );
    }

    public async Task DeleteDocumentAsync(string indexName, string documentId, CancellationToken cancellationToken = default)
    {
        await _client.DeleteAsync<object>(documentId, d => d.Index(indexName));
    }

    public async Task BulkIndexAsync<T>(string indexName, IEnumerable<(string Id, T Document)> documents, CancellationToken cancellationToken = default) where T : class
    {
        var bulkRequest = new BulkRequest(indexName)
        {
            Operations = documents.Select(doc => new BulkIndexOperation<T>(doc.Document)
            {
                Id = doc.Id
            }).Cast<IBulkOperation>().ToList()
        };

        await _client.BulkAsync(bulkRequest);
    }
}