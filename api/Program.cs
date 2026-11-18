using MathForge.Api.Clients;

var builder = WebApplication.CreateBuilder(args);

var computeUrl = builder.Configuration["ComputeService:BaseUrl"] ?? throw new InvalidOperationException("ComputeService:BaseUrl is not configured.");

builder.Services.AddHttpClient<ComputeClient>(client =>
{
    client.BaseAddress = new Uri(computeUrl);
    client.Timeout = TimeSpan.FromSeconds(5);
});

var app = builder.Build();

app.MapGet("/health", () => new { status = "ok", service = "api" });

app.MapGet("/health/compute", async (ComputeClient compute, ILogger<Program> logger, CancellationToken ct) =>
{
    try
    {
        var health = await compute.GetHealthAsync(ct);
        return Results.Ok(health);
    }
    catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException)
    {
        logger.LogWarning(ex, "Compute service health check failed");
        return Results.Problem(title: "Compute service unavailable", statusCode: StatusCodes.Status503ServiceUnavailable);
    }
});

app.Run();
