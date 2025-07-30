def get_droughts_index():
    # SPI drought index thresholds and color mapping in ascending order
    spi_thresholds = [
        (float('-inf'), -1.99, '#820a0a'),   # Extreme drought (dark red)
        (-1.99, -1.49, '#ff0303'),            # Severe drought (red)
        (-1.49, -1.0, 'orange'),               # Moderate drought
        (-1.0, 0.0, 'yellow'),                 # Mildly dry
        (0.0, float('inf'), '#4603ff')         # No drought (blue)
    ]

    legend_labels = [
        'Extreme drought',
        'Severe drought',
        'Moderate drought',
        'Mildly dry',
        'No drought'
    ]

    # Generate HTML legend with colored dots for Streamlit display
    legend_html = """
    <div style='display: flex; align-items: center; gap: 16px;'>
        <span style='font-size: 1.1em; font-weight: 600; margin: 0;'>SPI Threshold:</span>
        <div style='display: flex; gap: 15px; align-items: center;'>
    """
    for label, (_, _, color) in zip(legend_labels, spi_thresholds):
        legend_html += (
            f"<span style='display: flex; align-items: center; font-size: 15px;'>"
            f"<span style='display:inline-block;width:15px;height:15px;background:{color};"
            "border-radius:50%;margin-right:6px;border:1px solid #000;'></span>"
            f"{label}</span>"
        )
    legend_html += """
        </div>
    </div>
    """

    # Function to return color based on value
    def get_spi_color(val):
        for lower, upper, color in spi_thresholds:
            if lower <= val < upper:
                return color
        return "#cccccc"  # fallback color if out of range

    return legend_html, get_spi_color
