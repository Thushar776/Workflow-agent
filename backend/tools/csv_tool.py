import pandas as pd
import io

def analyze_csv(query: str, csv_content_or_path: str = None) -> str:
    """
    Analyzes a CSV based on the natural language query.
    
    Args:
        query: What the user wants to know about the CSV.
        csv_content_or_path: Optional. Leave empty or omit to use the default system sales data.
    
    Returns:
        A string containing the analysis result.
    """
    try:
        # For our mock implementation, we provide a generic sales dataset if none is provided
        if not csv_content_or_path:
            mock_data = """date,product,sales,region
2026-01-01,Widget A,150,North
2026-01-02,Widget B,200,South
2026-01-03,Widget A,120,East
2026-01-04,Widget C,300,West
2026-01-05,Widget B,250,North"""
            df = pd.read_csv(io.StringIO(mock_data))
        else:
            # If path is provided, read it
            df = pd.read_csv(csv_content_or_path)
        
        # Simple heuristics for our mock analyzer
        query_lower = query.lower()
        if "total sales" in query_lower:
            total = df["sales"].sum()
            return f"The total sales across all regions is ${total}."
        elif "region" in query_lower:
            region_sales = df.groupby("region")["sales"].sum().to_dict()
            return f"Sales by region: {region_sales}"
        elif "product" in query_lower:
            product_sales = df.groupby("product")["sales"].sum().to_dict()
            return f"Sales by product: {product_sales}"
        
        return f"Successfully parsed CSV with {len(df)} rows. Columns: {list(df.columns)}. (I am a mock analyzer, try asking for 'total sales')."
    
    except Exception as e:
        return f"Failed to analyze CSV: {str(e)}"
