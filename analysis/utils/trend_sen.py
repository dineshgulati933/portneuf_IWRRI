import pandas as pd
import pymannkendall as mk
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colors import Normalize, TwoSlopeNorm
import contextily as ctx


def irr_year(df):
    """
    Assigns irrigation year and calendar year based on a date.

    The irrigation year is defined as starting in November and ending in October of the following calendar year.
    For example, November 2022 through October 2023 is considered the irrigation year 2023.

    Parameters:
    -----------
    df : pandas.DataFrame
        A DataFrame containing a 'Date' column of datetime type.

    Returns:
    --------
    tuple
        A tuple containing:
        - month (int): The calendar month (1–12).
        - calendar_year (int): The calendar year of the date.
        - irrigation_year (int): The irrigation year the date belongs to.
    
    Example:
    --------
    >>> df['Date'] = pd.to_datetime(['2022-11-15', '2023-03-10'])
    >>> df.apply(irr_year, axis=1)
    (11, 2022, 2023)
    (3, 2023, 2023)
    """
    month = df['Date'].month
    if month >= 11:
        return month, df['Date'].year, df['Date'].year + 1
    else:
        return month, df['Date'].year, df['Date'].year




def analyze_trends(df, var_list, sort_yr='irr_year'):
    """
    Computes the Sen's slope, p-value, and trend direction (increasing/decreasing/no trend) 
    for each variable across years grouped by HUC12.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame with at least columns: 'huc12', time sorting column (e.g. 'irr_year'), and the target variables.

    var_list : list of str
        List of column names in the DataFrame for which trend analysis will be performed.

    sort_yr : str, optional
        Column name to sort the data chronologically (default is 'irr_year').

    Returns:
    --------
    pandas.DataFrame
        A DataFrame where each row corresponds to a unique HUC12 and columns include:
        - `{variable}_slope`: Sen's slope estimate.
        - `{variable}_p`: p-value of the Mann-Kendall test.
        - `{variable}_trend`: Trend direction ('increasing', 'decreasing', 'no trend').

    Notes:
    ------
    - Uses `pymannkendall.original_test()` for trend detection.
    - Missing or invalid input will result in None values for that HUC12-variable combination.

    Example:
    --------
    >>> analyze_trends(df, var_list=['ppt', 'et'], sort_yr='irr_year')
    """

    results = []

    for huc12, group in df.groupby('huc12'):
        group_sorted = group.sort_values(sort_yr)
        trend_data = {'huc12': huc12}

        for var in var_list:
            series = group_sorted[var].values

            try:
                result = mk.original_test(series)
                trend_data[f'{var}_slope'] = result.slope
                trend_data[f'{var}_p'] = result.p
                trend_data[f'{var}_trend'] = result.trend
            except Exception:
                trend_data[f'{var}_slope'] = None
                trend_data[f'{var}_p'] = None
                trend_data[f'{var}_trend'] = None

        results.append(trend_data)

    return pd.DataFrame(results)



def summarize_trends(trend_df, variables):
    """
    Summarizes the number of HUCs showing increasing, decreasing, or no trend 
    for each variable based on Mann-Kendall results.

    Parameters
    ----------
    trend_df : pandas.DataFrame
        DataFrame containing trend results. Must include `{var}_trend` columns.
    
    variables : list of str
        List of variable name prefixes (e.g., ['ppt', 'et', 'tmax']).

    Returns
    -------
    summary_df : pandas.DataFrame
        DataFrame with columns: Variable, Increasing, Decreasing, No Trend
    """
    summary = {
        'Variable': [],
        'Increasing': [],
        'Decreasing': [],
        'No Trend': []
    }

    for var in variables:
        col = f'{var}_trend'
        counts = trend_df[col].value_counts()
        summary['Variable'].append(var)
        summary['Increasing'].append(counts.get('increasing', 0))
        summary['Decreasing'].append(counts.get('decreasing', 0))
        summary['No Trend'].append(counts.get('no trend', 0))

    return pd.DataFrame(summary)



# def plot_trend_map(
#     gdf,
#     slope_col,
#     pval_col,
#     title="Trend Map",
#     cbar_label="Sen's Slope",
#     vmin=None,
#     vmax=None,
#     hatch_pattern='///',
#     significance_level=0.05,
#     figsize=(12, 8),
#     cmap='coolwarm',
#     save_path=None
# ):
#     """
#     Plot a spatial trend map from a GeoDataFrame, with hatching to indicate non-significant trends.

#     Parameters
#     ----------
#     gdf : geopandas.GeoDataFrame
#         Input GeoDataFrame with slope and p-value columns.

#     slope_col : str
#         Name of the column containing Sen's slope values (used for color mapping).

#     pval_col : str
#         Name of the column containing p-values from the Mann-Kendall test.

#     title : str, optional
#         Title of the plot. Default is "Trend Map".

#     cbar_label : str, optional
#         Label for the colorbar. Default is "Sen's Slope".

#     vmin : float or None, optional
#         Minimum value for colormap normalization. If None, inferred from data.

#     vmax : float or None, optional
#         Maximum value for colormap normalization. If None, inferred from data.

#     hatch_pattern : str, optional
#         Hatching pattern used for non-significant regions. Default is '///'.

#     significance_level : float, optional
#         P-value threshold below which a trend is considered statistically significant. Default is 0.05.

#     figsize : tuple of int, optional
#         Figure size in inches. Default is (12, 8).

#     cmap : str, optional
#         Colormap for slope values. Default is 'coolwarm'.

#     save_path : str or None, optional
#         If provided, saves the figure to this file path.

#     Returns
#     -------
#     None
#         Displays the plot and optionally saves it to file.

#     Notes
#     -----
#     - Areas where the trend is not significant (p > significance_level) will be hatched with the specified pattern.
#     - Only polygons with valid `slope_col` values will be colored.
#     """
#     fig, ax = plt.subplots(1, 1, figsize=figsize)

#     # Determine significance mask
#     sig_mask = gdf[pval_col] <= significance_level
#     not_sig_mask = ~sig_mask

#     # Colormap normalization
#     norm = Normalize(vmin=vmin, vmax=vmax) if vmin is not None and vmax is not None else None

#     # Plot significant polygons
#     plot = gdf.plot(
#         column=slope_col,
#         cmap=cmap,
#         linewidth=0.5,
#         edgecolor='black',
#         legend=True,
#         ax=ax,
#         norm=norm
#     )

#     # Add hatching for non-significant areas
#     if sig_mask.any():
#         gdf[sig_mask].plot(
#             color='none',
#             edgecolor='black',
#             hatch='.',
#             ax=ax
#         )

#     # Access and label colorbar
#     cbar = plot.get_figure().get_axes()[-1]
#     cbar.set_ylabel(cbar_label, fontsize=12)

#     # Title and formatting
#     ax.set_title(title, fontsize=16)
#     ax.axis('off')
#     plt.tight_layout()

#     # Save the figure
#     if save_path:
#         plt.savefig(save_path, dpi=300, bbox_inches='tight')
#         print(f"Figure saved to {save_path}")

#     plt.show()



def plot_trend_map(
    gdf,
    slope_col,
    pval_col,
    title="Trend Map",
    cbar_label="Sen's Slope",
    vmin=None,
    vmax=None,
    center_zero=True,
    hatch_non_significant=False,
    show_significance_border=True,
    show_significance_marker=False,
    significance_level=0.05,
    figsize=(12, 8),
    cmap='RdBu',
    save_path=None,
    basemap=False
):
    """
    Plot spatial Sen's Slope trends with significance marking.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame containing Sen's slope and p-value.

    slope_col : str
        Column name for slope values.

    pval_col : str
        Column name for p-values (Mann-Kendall).

    title : str
        Plot title.

    cbar_label : str
        Colorbar label.

    vmin, vmax : float or None
        Min and max for color scale.

    center_zero : bool
        Center colormap at 0 (TwoSlopeNorm). Recommended for slope maps.

    hatch_non_significant : bool
        If True, hatch polygons with non-significant trends.

    show_significance_border : bool
        If True, draw bold borders for significant polygons.

    show_significance_marker : bool
        If True, plot centroid markers for significant polygons.

    significance_level : float
        P-value threshold.

    figsize : tuple
        Size of the figure.

    cmap : str
        Colormap name (e.g., 'RdBu_r', 'coolwarm').

    save_path : str or None
        If provided, saves the figure.

    basemap : bool
        If True, reproject to Web Mercator and add basemap.

    Returns
    -------
    None
    """

    # Copy and optionally reproject
    plot_gdf = gdf.copy()
    if basemap and plot_gdf.crs.to_epsg() != 3857:
        plot_gdf = plot_gdf.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=figsize)

    # Significance mask
    sig_mask = plot_gdf[pval_col] <= significance_level
    not_sig_mask = ~sig_mask

    # Compute bounds from data if not provided
    if vmin is None:
        vmin = plot_gdf[slope_col].min()
    if vmax is None:
        vmax = plot_gdf[slope_col].max()

    # Colormap normalization
    if center_zero:
        # Check if diverging normalization is valid
        if vmin < 0 and vmax > 0:
            norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
        else:
            print(f"Warning: Data range ({vmin:.2f}, {vmax:.2f}) does not cross 0. Using linear Normalize instead.")
            norm = Normalize(vmin=vmin, vmax=vmax) # Fallback to standard Normalize
            center_zero = False  # fallback case
            cmap = 'Blues' if vmax > 0 else 'Reds'  # Adjust cmap if not diverging
    else:
        norm = Normalize(vmin=vmin, vmax=vmax)

    # Base plot (all polygons colored)
    plot_gdf.plot(
        column=slope_col,
        cmap=cmap,
        linewidth=0.5,
        edgecolor='gray',
        legend=True,
        norm=norm,
        ax=ax
    )

    # Hatch or highlight non-significant
    if hatch_non_significant and not_sig_mask.any():
        plot_gdf[not_sig_mask].plot(
            color='none',
            edgecolor='gray',
            hatch='...',
            ax=ax
        )

    if show_significance_border and sig_mask.any():
        plot_gdf[sig_mask].plot(
            color='none',
            edgecolor='black',
            linewidth=1.2,
            ax=ax
        )

    if show_significance_marker and sig_mask.any():
        plot_gdf[sig_mask].geometry.centroid.plot(
            ax=ax,
            marker='*',
            color='black',
            markersize=30
        )

    # Basemap
    if basemap:
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')

    # Title and formatting
    ax.set_title(title, fontsize=15)
    # # Aesthetics
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_facecolor('white')
    plt.tight_layout()

    # Colorbar label
    cbar = fig.get_axes()[-1]
    cbar.set_ylabel(cbar_label, fontsize=12)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    plt.show()

def plot_gdf(
    gdf,
    column,
    cmap='Blues',
    edgecolor='gray',
    linewidth=0.5,
    legend_label=None,
    basemap=False,
    basemap_source=ctx.providers.CartoDB.Positron,
    figsize=(12, 10),
    title=None,
    save_path=None,
    dpi=300
):
    """
    Plot a GeoDataFrame with optional basemap and save.

    Parameters:
    - gdf: GeoDataFrame to plot.
    - column: Name of the numeric column to visualize.
    - cmap: Matplotlib colormap name.
    - edgecolor, linewidth: styling for polygon outlines.
    - legend_label: Label for the colorbar (e.g. 'Mean Precipitation (mm)').
    - basemap: If True, reproject to EPSG:3857 and add a base map.
    - basemap_source: contextily tile provider.
    - figsize: Figure size.
    - title: Plot title (string).
    - save_path: PNG filename to save the figure. If None, does not save.
    - dpi: Resolution when saving.
    """

    # Prepare GeoDataFrame (copy to avoid side effects)
    plot_gdf = gdf.copy()

    fig, ax = plt.subplots(figsize=figsize)

    # Reproject and plot
    if basemap and plot_gdf.crs.to_epsg() != 3857:
        plot_gdf = plot_gdf.to_crs(epsg=3857)

    plot_gdf.plot(
        column=column,
        cmap=cmap,
        linewidth=linewidth,
        edgecolor=edgecolor,
        legend=True,
        legend_kwds={'label': legend_label, 'shrink': 0.8},
        ax=ax
    )
    if basemap:
        # Add basemap
        ctx.add_basemap(ax, source=basemap_source, alpha=0.8)
        #ax.set_axis_off()
        ax.set_xticks([])
        ax.set_yticks([])
    else:
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
    # # Aesthetics
    ax.set_axisbelow(True)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5)
    ax.set_facecolor('white')

    if title:
        ax.set_title(title, fontsize=14)

    plt.tight_layout()

    # Save if requested
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')

    plt.show()
