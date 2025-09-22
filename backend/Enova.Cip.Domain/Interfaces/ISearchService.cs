namespace Enova.Cip.Domain.Interfaces;

public class SearchResult<T>
{
    public IEnumerable<T> Items { get; set; } = new List<T>();
    public long TotalCount { get; set; }
    public int Page { get; set; }
    public int PageSize { get; set; }
}

public interface ISearchService
{
    Task<SearchResult<T>> SearchAsync<T>(string indexName, string query, int page = 1, int pageSize = 20, CancellationToken cancellationToken = default) where T : class;
    Task IndexDocumentAsync<T>(string indexName, string documentId, T document, CancellationToken cancellationToken = default) where T : class;
    Task DeleteDocumentAsync(string indexName, string documentId, CancellationToken cancellationToken = default);
    Task BulkIndexAsync<T>(string indexName, IEnumerable<(string Id, T Document)> documents, CancellationToken cancellationToken = default) where T : class;
}