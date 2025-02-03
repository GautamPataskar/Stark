using Microsoft.AspNetCore.Mvc;
using Stark.Core.Services;
using Stark.Core.Models;
using System.Threading.Tasks;

[ApiController]
[Route("api/[controller]")]
public class MLAnalyticsController : ControllerBase
{
    private readonly IMLService _mlService;
    private readonly ILogger<MLAnalyticsController> _logger;

    public MLAnalyticsController(IMLService mlService, ILogger<MLAnalyticsController> logger)
    {
        _mlService = mlService;
        _logger = logger;
    }

    [HttpPost("predict")]
    public async Task<IActionResult> PredictThreat([FromBody] SecurityEvent securityEvent)
    {
        try
        {
            var prediction = await _mlService.PredictThreatAsync(securityEvent);
            return Ok(new
            {
                threatScore = prediction.ThreatScore,
                confidence = prediction.Confidence,
                riskLevel = prediction.RiskLevel,
                analysisDetails = prediction.Details
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during threat prediction");
            return StatusCode(500, "Prediction service error");
        }
    }

    [HttpGet("model/metrics")]
    public async Task<IActionResult> GetModelMetrics()
    {
        try
        {
            var metrics = await _mlService.GetModelMetricsAsync();
            return Ok(metrics);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching model metrics");
            return StatusCode(500, "Metrics service error");
        }
    }

    [HttpPost("model/retrain")]
    public async Task<IActionResult> RetrainModel([FromBody] RetrainingConfig config)
    {
        try
        {
            var result = await _mlService.RetrainModelAsync(config);
            return Ok(new
            {
                success = true,
                newAccuracy = result.Accuracy,
                improvementPercentage = result.Improvement,
                trainingTime = result.TrainingTime
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error during model retraining");
            return StatusCode(500, "Retraining service error");
        }
    }
}