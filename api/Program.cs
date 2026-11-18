using MathForge.Api.Clients;

var builder = WebApplication.CreateBuilder(args);

var computeUrl = builder.Configuration["ComputeService:BaseUrl"] ?? throw new InvalidOperationException("ComputeService:BaseUrl is not configured.");

builder.Services.AddHttpClient<ComputeClient>(client =>
{
    client.BaseAddress = new Uri(computeUrl);
    client.Timeout = TimeSpan.FromSeconds(5);
});

var clientOrigin = builder.Configuration["Cors:AllowedOrigin"] ?? throw new InvalidOperationException("Cors:AllowedOrigin is not configured.");

builder.Services.AddCors(options => options.AddDefaultPolicy(policy => policy.WithOrigins(clientOrigin).AllowAnyHeader().AllowAnyMethod()));

var app = builder.Build();

app.UseCors();

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
