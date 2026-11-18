namespace MathForge.Api.Clients;

public record ComputeHealth(string Status, string Service, string Sympy);

public class ComputeClient(HttpClient http)
{
    public Task<ComputeHealth?> GetHealthAsync(CancellationToken ct = default) => http.GetFromJsonAsync<ComputeHealth>("/health", ct);
}