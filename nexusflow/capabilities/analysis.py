"""
Analysis Capability for NexusFlow.ai

This module implements the AnalysisCapability class, which represents
the data analysis ability of agents in the NexusFlow system.
"""

from typing import Dict, List, Any, Optional, Set, Union
import logging
import re

from nexusflow.core.capability import Capability, CapabilityType

logger = logging.getLogger(__name__)

class AnalysisCapability(Capability):
    """
    Capability for data analysis
    
    This capability enables agents to:
    - Analyze and interpret data
    - Identify patterns, trends, and insights
    - Perform statistical calculations
    - Create data visualizations
    - Provide data-driven recommendations
    """
    
    def __init__(self):
        """Initialize the analysis capability"""
        super().__init__(
            type=CapabilityType.DATA_ANALYSIS.value,
            name="Data Analysis",
            description="Ability to analyze data and generate insights",
            requires_tools=["data_analysis"],
            provides_output=["analysis", "insights", "visualization"],
            requires_input=["data"]
        )
        
        # Analysis methods
        self.analysis_methods = [
            "descriptive", "exploratory", "statistical", "predictive", 
            "causal", "prescriptive", "clustering", "classification",
            "correlation", "regression", "time_series", "anomaly_detection"
        ]
        
        # Patterns that indicate analysis needs
        self.analysis_patterns = [
            r"(analyze|analyse|examine|study|investigate) .*(data|dataset|information|results|numbers|statistics)",
            r"(find|identify|discover) .*(patterns|trends|correlations|relationships|insights|anomalies)",
            r"(perform|conduct|run) .*(analysis|analytics|statistics|statistical analysis)",
            r"(create|generate|produce|make) .*(chart|graph|plot|visualization|dashboard)",
            r"(summarize|summarise|interpret|understand) .*(data|dataset|statistics|results)",
            r"(calculate|compute|determine) .*(mean|median|average|variance|standard deviation|correlation|regression)"
        ]
        
        # Data type indicators
        self.data_type_indicators = {
            "numeric": ["number", "numeric", "integer", "float", "decimal", "count", "quantity", "amount"],
            "categorical": ["category", "categorical", "label", "class", "group", "type", "kind"],
            "time_series": ["time", "series", "temporal", "date", "period", "interval", "sequence", "trend"],
            "text": ["text", "string", "word", "document", "content", "language", "sentence"],
            "geospatial": ["location", "geographic", "spatial", "coordinate", "map", "region", "area"]
        }
        
        # Example use cases
        self.examples = [
            {
                "name": "Statistical analysis",
                "description": "Analyzing numerical data for statistical insights",
                "input": "Analyze this sales data and provide key insights: [Sales data CSV attached]",
                "output": "# Sales Data Analysis\n\n## Summary Statistics\n\n| Metric | Value |\n|--------|-------|\n| Total Sales | $2,458,932 |\n| Average Order Value | $156.73 |\n| Number of Transactions | 15,689 |\n| Top Product Category | Electronics (32%) |\n| Highest Growth Region | Northeast (+24%) |\n\n## Key Insights\n\n1. **Seasonal Patterns**: Sales show strong seasonality with peaks in November-December (43% above average) and a smaller peak in July (21% above average).\n\n2. **Product Category Analysis**:\n   - Electronics drives the highest revenue (32%) but has the smallest profit margin (18%)\n   - Home goods have the highest profit margin (37%) and show the most consistent growth\n   - Apparel shows the highest variability and is most affected by seasonality\n\n3. **Customer Segmentation**:\n   - Repeat customers (38% of total) generate 62% of revenue\n   - First-time customers have a 27% conversion rate to repeat customers\n   - The 90-day retention rate has increased from 34% to 41% over the past year\n\n4. **Regional Performance**:\n   - Northeast region shows highest growth (+24% YoY)\n   - Western region has highest average order value ($187.45)\n   - Southern region has highest customer loyalty (repeat purchase rate of 46%)\n\n## Recommendations\n\n1. Increase marketing budget allocation for Northeast region to capitalize on growth momentum\n2. Develop targeted promotions for Electronics to improve margins\n3. Invest in customer retention strategies, as data indicates significant ROI on repeat customer acquisition\n4. Prepare inventory adjustments for seasonal patterns, especially for Apparel category\n\n## Visualization\n[Note: Charts would be included here in an actual report]"
            },
            {
                "name": "Time series analysis",
                "description": "Analyzing time-based data for trends and patterns",
                "input": "Analyze this website traffic data and identify patterns or trends over time.",
                "output": "# Website Traffic Analysis\n\n## Overview\nI've analyzed the website traffic data across the time period provided (Jan 2023 - Mar 2024) and identified several significant patterns and trends.\n\n## Key Findings\n\n### 1. Overall Traffic Trend\n- **15.3% YoY Growth**: Total traffic increased from 234,567 monthly visitors (Jan-Mar 2023) to 270,456 monthly visitors (Jan-Mar 2024)\n- **Consistent Growth Pattern**: Traffic shows steady month-over-month growth of ~1.2% on average\n\n### 2. Seasonal Patterns\n- **Strong Weekday-Weekend Cycle**: Traffic is 32% higher on weekdays vs. weekends\n- **Morning Peak**: Highest traffic occurs between 9am-11am (27% of daily total)\n- **Monthly Pattern**: Traffic peaks in the middle of each month (10th-20th)\n- **Quarterly Surge**: End-of-quarter months (Mar, Jun, Sep, Dec) show 18-22% higher traffic\n\n### 3. Content Engagement\n- **Page Depth Increasing**: Average pages per session increased from 3.2 to 4.1 (+28%)\n- **Session Duration**: Average time on site increased from 3:45 to 4:12 (+12%)\n- **Bounce Rate Improvement**: Decreased from 42% to 36% over the analyzed period\n\n### 4. Traffic Sources\n- **Organic Search**: Increased from 45% to 52% of total traffic (strongest growth)\n- **Direct Traffic**: Stable at ~18% throughout the period\n- **Social Media**: Decreased from 24% to 19% (further investigation recommended)\n- **Referral**: Slight decrease from 13% to 11%\n\n### 5. Device Distribution\n- **Mobile Dominance**: Mobile traffic increased from 58% to 64%\n- **Desktop Decline**: Decreased from 37% to 31%\n- **Tablet Stable**: Consistent at ~5% throughout the period\n\n## Anomalies Detected\n1. **March 15, 2023**: Traffic spike of 3.2x normal volume (correlates with major product launch)\n2. **November 24-27, 2023**: 47% drop in traffic (holiday period - expected)\n3. **January 12-14, 2024**: 38% drop followed by 45% increase (coincides with site maintenance)\n\n## Recommendations\n1. Optimize site for mobile experience given the increasing trend\n2. Investigate social media traffic decline and adjust strategy\n3. Schedule content releases during peak traffic periods (weekday mornings, mid-month)\n4. Consider timing major announcements to align with natural traffic patterns\n5. Investigate strategies to maintain weekend engagement\n\n## Statistical Significance\nAll reported trends show p-values < 0.05 using time series regression analysis, indicating statistical significance."
            },
            {
                "name": "Predictive analysis",
                "description": "Using data to make predictions and recommendations",
                "input": "Based on our customer churn data, can you predict which factors most strongly indicate a customer will leave our service?",
                "output": "# Customer Churn Prediction Analysis\n\n## Predictive Factors for Customer Churn\n\nAfter analyzing your customer churn data using multiple statistical models (logistic regression, random forest, and gradient boosting), I've identified the following factors as the strongest predictors of customer churn, ranked by importance:\n\n### Primary Factors (Very Strong Correlation)\n\n1. **Service Usage Decline** (Coefficient: 0.87)\n   - Customers who show a 30%+ reduction in service usage over 60 days have an 81% churn probability\n   - This is the single strongest predictor across all models\n\n2. **Support Ticket Frequency** (Coefficient: 0.76)\n   - Customers with 3+ support tickets in 30 days have a 68% churn probability\n   - The correlation strengthens if tickets involve similar issues\n\n3. **Contract Type** (Coefficient: 0.71)\n   - Month-to-month contracts have a 5.8x higher churn rate than annual contracts\n   - This factor becomes more significant after the 6-month customer mark\n\n### Secondary Factors (Moderate Correlation)\n\n4. **Price Sensitivity** (Coefficient: 0.62)\n   - Customers who have previously questioned pricing have a 53% higher churn rate\n   - This effect amplifies after any price increase (even minor ones)\n\n5. **Competitor Engagement** (Coefficient: 0.58)\n   - Engagement with competitor content (via email clicks, website visits tracked through remarketing) increases churn probability by 47%\n\n6. **Feature Utilization** (Coefficient: 0.56)\n   - Customers using fewer than 40% of available features have a 49% higher churn probability\n   - This is especially true for premium subscription tiers\n\n### Tertiary Factors (Significant but Lower Correlation)\n\n7. **Onboarding Completion** (Coefficient: 0.42)\n   - Incomplete onboarding correlates with 38% higher churn\n   - The effect diminishes over time but remains significant\n\n8. **Payment Issues** (Coefficient: 0.39)\n   - Customers with 2+ payment failures have a 36% higher churn probability\n\n9. **Communication Engagement** (Coefficient: 0.34)\n   - Declining email open/click rates correlate with 31% higher churn\n\n## Model Accuracy\n\nThe ensemble prediction model achieves:\n- 87.3% accuracy in identifying high-risk customers\n- 79.6% precision in predicting actual churners\n- 82.1% recall rate for identifying churners\n\n## Actionable Recommendations\n\n1. **Implement Usage Monitoring Alerts**\n   - Trigger customer success interventions when usage declines by 15%+ over 30 days\n\n2. **Support Ticket Intervention Protocol**\n   - Create a specialized retention team to handle accounts with multiple support tickets\n\n3. **Contract Incentive Strategy**\n   - Develop targeted incentives for month-to-month customers to upgrade to annual plans\n\n4. **Feature Adoption Program**\n   - Launch a proactive feature education campaign targeting users with low feature utilization\n\n5. **Onboarding Enhancement**\n   - Redesign onboarding to ensure higher completion rates and feature discovery\n\nBy focusing interventions on these indicators, particularly the top 3-4 factors, our model predicts a potential 23-31% reduction in overall churn rate."
            }
        ]
    
    def matches_input(self, input_data: Dict[str, Any]) -> float:
        """
        Check if the input requires data analysis capability
        
        Args:
            input_data: Input data to analyze
            
        Returns:
            Match score between 0.0 and 1.0
        """
        query = input_data.get("query", "").lower()
        
        # Check if any analysis patterns are present
        for pattern in self.analysis_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return 0.9  # High match if analysis indicators are present
        
        # Check for specific analysis methods
        for method in self.analysis_methods:
            if method in query:
                return 0.85  # Strong match for specific analysis methods
        
        # Check for mentions of visualization
        visualization_terms = ["visualize", "visualization", "chart", "graph", "plot", "diagram", "dashboard"]
        if any(term in query for term in visualization_terms):
            return 0.8  # Strong match for visualization requests
        
        # Check for specific data types
        data_type_score = 0.0
        for data_type, indicators in self.data_type_indicators.items():
            if any(indicator in query for indicator in indicators):
                data_type_score = max(data_type_score, 0.75)  # Moderate-to-strong match for data type indicators
        
        if data_type_score > 0:
            return data_type_score
        
        # Check for general data-related terms
        data_terms = ["data", "dataset", "information", "statistics", "numbers", "metrics", "kpi"]
        if any(term in query for term in data_terms):
            return 0.6  # Moderate match for general data terms
        
        return 0.3  # Low default match
    
    def get_prompt_enhancement(self, input_data: Dict[str, Any]) -> str:
        """
        Get prompt enhancement for analysis tasks
        
        Args:
            input_data: Input data for the task
            
        Returns:
            Prompt enhancement text
        """
        # Detect the type of analysis needed
        query = input_data.get("query", "").lower()
        
        # Base prompt enhancement
        enhancement = """
When analyzing data:

1. Start with an exploratory approach to understand the data
2. Identify key metrics, patterns, trends, and outliers
3. Apply appropriate statistical methods
4. Generate visualizations that best communicate insights
5. Provide clear, data-driven conclusions
6. Offer actionable recommendations based on the analysis
"""
        
        # Check for specific analysis types and add specialized guidance
        if any(term in query for term in ["predict", "forecasting", "future", "will", "expect"]):
            enhancement += """
For predictive analysis:
- Identify which variables have predictive power
- Consider both the strength and reliability of predictors
- Discuss confidence levels of predictions
- Acknowledge limitations and edge cases
"""
        elif any(term in query for term in ["why", "cause", "effect", "impact", "result"]):
            enhancement += """
For causal analysis:
- Distinguish correlation from causation
- Consider confounding variables
- Evaluate the strength of causal evidence
- Discuss alternative explanations
"""
        elif any(term in query for term in ["compare", "difference", "versus", "vs", "against"]):
            enhancement += """
For comparative analysis:
- Define clear comparison metrics
- Ensure fair comparison methodology
- Highlight key differences and similarities
- Provide context for interpreting the differences
"""
        
        return enhancement
    
    def get_system_message_guidance(self) -> str:
        """
        Get guidance for system message related to data analysis
        
        Returns:
            System message guidance
        """
        return """
You excel at data analysis. When analyzing data:
- Approach data with a curious, systematic mindset
- Apply appropriate statistical and analytical methods
- Create clear, informative visualizations
- Identify meaningful patterns, trends, and insights
- Provide context for interpreting results
- Express confidence levels and limitations
- Translate technical findings into actionable insights
- Present conclusions in a clear, organized manner
"""
    
    def detect_analysis_method(self, query: str) -> Optional[str]:
        """
        Detect the analysis method requested in the query
        
        Args:
            query: The query to analyze
            
        Returns:
            Detected analysis method or None
        """
        for method in self.analysis_methods:
            if method in query.lower():
                return method
        
        # Check for common method indicators
        if any(term in query.lower() for term in ["predict", "forecast", "future"]):
            return "predictive"
        elif any(term in query.lower() for term in ["cause", "effect", "why", "impact"]):
            return "causal"
        elif any(term in query.lower() for term in ["describe", "summary", "overview"]):
            return "descriptive"
        elif any(term in query.lower() for term in ["explore", "discover", "find patterns"]):
            return "exploratory"
        elif any(term in query.lower() for term in ["correlate", "relationship", "connection"]):
            return "correlation"
        elif any(term in query.lower() for term in ["cluster", "segment", "group"]):
            return "clustering"
        elif any(term in query.lower() for term in ["classify", "categorize", "identify type"]):
            return "classification"
        elif any(term in query.lower() for term in ["time", "trend", "period", "seasonal"]):
            return "time_series"
        
        return None
