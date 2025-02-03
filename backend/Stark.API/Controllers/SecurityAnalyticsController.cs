using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;
using Stark.Core.Services;
using Stark.Core.Models;

namespace Stark.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class SecurityAnalyticsController : ControllerBase
    {
        private readonly ISecurityAnalyticsService _analyticsService;
        private readonly IThreatDetectionService _threatService;
        private readonly ILogger<SecurityAnalyticsController> _logger;

        public SecurityAnalyticsController(
            ISecurityAnalyticsService analyticsService,
            IThreatDetectionService threatService,
            ILogger<SecurityAnalyticsController> logger)
        {
            _analyticsService = analyticsService;
            _threatService = threatService;
            _logger = logger;
        }

        [HttpPost("analyze")]
        public async Task<IActionResult> AnalyzeSecurityEvent([FromBody] SecurityEvent securityEvent)
        {
            try
            {
                var analysis = await _analyticsService.AnalyzeEventAsync(securityEvent);
                var threatAssessment = await _threatService.AssessThreatsAsync(securityEvent);

                return Ok(new
                {
                    analysis = analysis,
                    threats = threatAssessment,
                    timestamp = DateTime.UtcNow
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error analyzing security event");
                return StatusCode(500, "Internal server error during analysis");
            }
        }

        [HttpGet("dashboard")]
        public async Task<IActionResult> GetDashboardMetrics()
        {
            try
            {
                var metrics = await _analyticsService.GetDashboardMetricsAsync();
                return Ok(metrics);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error fetching dashboard metrics");
                return StatusCode(500, "Internal server error");
            }
        }

        [HttpPost("realtime")]
        public async Task<IActionResult> ProcessRealTimeEvent([FromBody] SecurityEvent securityEvent)
        {
            try
            {
                var result = await _analyticsService.ProcessRealTimeEventAsync(securityEvent);
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing real-time event");
                return StatusCode(500, "Internal server error");
            }
        }
    }
}