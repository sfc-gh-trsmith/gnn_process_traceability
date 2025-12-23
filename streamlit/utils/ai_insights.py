"""
Cortex AI integration for natural language insights.

Uses Cortex Complete to generate explanations of root causes and risk summaries.
Includes graceful fallback when Cortex is unavailable.
"""

import streamlit as st


def get_root_cause_explanation(session, pattern_data: dict) -> str:
    """
    Generate natural language explanation of a root cause pattern.
    
    Uses Cortex Complete with specific prompt engineering to produce
    concise, actionable explanations without preamble.
    
    Args:
        session: Snowpark session
        pattern_data: Dict with pattern details (type, entity_name, score, defect_count, defect_types)
    
    Returns:
        Natural language explanation string
    """
    prompt = f"""Analyze this manufacturing root cause pattern and provide a concise explanation:

Pattern Type: {pattern_data.get('type', 'unknown')}
Entity: {pattern_data.get('entity_name', 'unknown')}
Correlation Score: {pattern_data.get('score', 0):.2f}
Affected Defects: {pattern_data.get('defect_count', 0)}
Defect Types: {pattern_data.get('defect_types', 'various')}

Explain the likely root cause and recommend immediate actions in 2-3 sentences.
No preamble, headers, or follow-up questions."""
    
    try:
        # Escape single quotes in prompt
        safe_prompt = prompt.replace("'", "''")
        
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{safe_prompt}'
            ) as response
        """).collect()
        
        if result and len(result) > 0:
            return result[0]['RESPONSE']
        return _fallback_explanation(pattern_data)
        
    except Exception as e:
        # Graceful fallback
        return _fallback_explanation(pattern_data)


def _fallback_explanation(pattern_data: dict) -> str:
    """Provide rule-based fallback when Cortex is unavailable."""
    pattern_type = pattern_data.get('type', '')
    entity_name = pattern_data.get('entity_name', 'Unknown')
    score = pattern_data.get('score', 0)
    defect_count = pattern_data.get('defect_count', 0)
    
    if 'supplier' in pattern_type.lower():
        return f"High correlation ({score:.0%}) between {entity_name} materials and defects. {defect_count} defects are linked to this supplier. Recommend immediate supplier audit and batch quarantine."
    elif 'process' in pattern_type.lower():
        return f"Process configuration issue detected at {entity_name}. {defect_count} defects linked to parameter deviations. Recommend immediate parameter verification and recalibration."
    else:
        return f"Pattern detected with {entity_name} showing {score:.0%} correlation to {defect_count} defects. Requires further investigation by quality team."


def get_risk_summary(session, risk_scores_df) -> str:
    """
    Generate a summary of top risks using Cortex AI.
    
    Args:
        session: Snowpark session
        risk_scores_df: DataFrame with component risk scores
    
    Returns:
        Natural language summary of top risks
    """
    if risk_scores_df.empty:
        return "No risk scores available. Run the GNN analysis notebook first."
    
    # Get top 5 risks
    top_risks = risk_scores_df.head(5)
    
    risk_list = []
    for _, row in top_risks.iterrows():
        risk_list.append(f"- {row['COMPONENT_NAME']}: {row['RISK_SCORE']:.2f} risk score, {row['RELATED_DEFECTS']} defects")
    
    risks_text = "\n".join(risk_list)
    
    prompt = f"""Summarize these manufacturing risk findings and recommend prioritized actions:

{risks_text}

Provide a 2-3 sentence executive summary with specific recommendations.
No preamble, headers, or follow-up questions."""
    
    try:
        safe_prompt = prompt.replace("'", "''")
        
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{safe_prompt}'
            ) as response
        """).collect()
        
        if result and len(result) > 0:
            return result[0]['RESPONSE']
        return _fallback_risk_summary(top_risks)
        
    except Exception as e:
        return _fallback_risk_summary(top_risks)


def _fallback_risk_summary(top_risks) -> str:
    """Provide fallback risk summary when Cortex is unavailable."""
    if top_risks.empty:
        return "No significant risks identified."
    
    highest_risk = top_risks.iloc[0]
    total_defects = top_risks['RELATED_DEFECTS'].sum()
    
    return f"Top risk: {highest_risk['COMPONENT_NAME']} with {highest_risk['RISK_SCORE']:.0%} risk score. The top 5 components are associated with {total_defects} defects total. Prioritize investigation of highest-risk components."

