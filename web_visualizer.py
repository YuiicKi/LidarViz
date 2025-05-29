#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Web的雷达点云数据可视化程序
使用Dash创建交互式Web界面
"""

import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import open3d as o3d
from pathlib import Path
import glob
import base64
import io

class WebLiDARVisualizer:
    """Web版雷达点云可视化器"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.setup_callbacks()
        
    def get_available_files(self):
        """获取可用文件列表"""
        files = []
        for ext in ['csv', 'pcd', 'ply']:
            pattern = self.data_path / f"*.{ext}"
            found_files = glob.glob(str(pattern))
            for file in found_files:
                files.append({
                    'label': Path(file).name,
                    'value': file
                })
        return files
    
    def load_csv_data(self, csv_file: str):
        """加载CSV数据"""
        df = pd.read_csv(csv_file)
        
        # 过滤有效点
        valid_mask = df['distance'] > 0
        df_valid = df[valid_mask].copy()
        
        return df_valid
    
    def load_pcd_data(self, pcd_file: str):
        """加载PCD数据"""
        pcd = o3d.io.read_point_cloud(pcd_file)
        points = np.asarray(pcd.points)
        
        df = pd.DataFrame({
            'Points_m_XYZ:0': points[:, 0],
            'Points_m_XYZ:1': points[:, 1], 
            'Points_m_XYZ:2': points[:, 2],
            'intensity': np.zeros(len(points)),
            'distance': np.linalg.norm(points, axis=1),
            'timestamp': np.zeros(len(points))
        })
        
        return df
    
    def setup_layout(self):
        """设置Web界面布局"""
        self.app.layout = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("雷达点云数据可视化系统", className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            dbc.Row([
                # 控制面板
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("控制面板"),
                        dbc.CardBody([
                            # 文件选择
                            html.Label("选择数据文件:"),
                            dcc.Dropdown(
                                id='file-dropdown',
                                options=self.get_available_files(),
                                value=None,
                                placeholder="请选择一个文件..."
                            ),
                            html.Br(),
                            
                            # 采样率控制
                            html.Label("采样率:"),
                            dcc.Slider(
                                id='sample-rate-slider',
                                min=0.01,
                                max=1.0,
                                step=0.01,
                                value=0.1,
                                marks={i/10: f'{i/10:.1f}' for i in range(1, 11, 2)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.Br(),
                            
                            # 点大小控制
                            html.Label("点大小:"),
                            dcc.Slider(
                                id='point-size-slider',
                                min=0.5,
                                max=5.0,
                                step=0.1,
                                value=1.5,
                                marks={i: f'{i}' for i in range(1, 6)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.Br(),
                            
                            # 透明度控制
                            html.Label("透明度:"),
                            dcc.Slider(
                                id='opacity-slider',
                                min=0.1,
                                max=1.0,
                                step=0.05,
                                value=0.6,
                                marks={i/10: f'{i/10:.1f}' for i in range(1, 11, 2)},
                                tooltip={"placement": "bottom", "always_visible": True}
                            ),
                            html.Br(),
                            
                            # 着色方式选择
                            html.Label("着色方式:"),
                            dcc.RadioItems(
                                id='color-by-radio',
                                options=[
                                    {'label': '高度', 'value': 'height'},
                                    {'label': '强度', 'value': 'intensity'},
                                    {'label': '距离', 'value': 'distance'}
                                ],
                                value='height',
                                inline=True
                            ),
                            html.Br(),
                            
                            # 可视化类型选择
                            html.Label("可视化类型:"),
                            dcc.RadioItems(
                                id='viz-type-radio',
                                options=[
                                    {'label': '3D散点图', 'value': '3d'},
                                    {'label': 'XY平面投影', 'value': 'xy'},
                                    {'label': 'XZ平面投影', 'value': 'xz'},
                                    {'label': 'YZ平面投影', 'value': 'yz'}
                                ],
                                value='3d',
                                inline=False
                            ),
                            html.Br(),
                            
                            # 实时更新开关
                            html.Label("实时更新:"),
                            dcc.Checklist(
                                id='auto-update-checkbox',
                                options=[{'label': '自动更新可视化', 'value': 'auto'}],
                                value=['auto']
                            ),
                            html.Br(),
                            
                            # 加载按钮
                            dbc.Button(
                                "加载并可视化",
                                id="load-button",
                                color="primary",
                                size="lg",
                                className="w-100"
                            ),
                            html.Br(),
                            html.Br(),
                            
                            # 提示信息
                            dbc.Alert([
                                html.H6("💡 使用提示:", className="alert-heading"),
                                html.P("• 开启实时更新后，调节滑块会立即更新图表"),
                                html.P("• 关闭实时更新可避免频繁计算，手动点击加载按钮更新"),
                                html.P("• 大数据集建议调低采样率以提高响应速度")
                            ], color="info", className="mt-3")
                        ])
                    ])
                ], width=3),
                
                # 主要显示区域
                dbc.Col([
                    # 数据信息卡片
                    dbc.Card([
                        dbc.CardHeader("数据信息"),
                        dbc.CardBody([
                            html.Div(id="data-info", children="请先选择并加载数据文件...")
                        ])
                    ], className="mb-3"),
                    
                    # 可视化图表
                    dbc.Card([
                        dbc.CardHeader("点云可视化"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="point-cloud-graph",
                                style={'height': '600px'}
                            )
                        ])
                    ])
                ], width=9)
            ]),
            
            # 统计信息行
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("统计分析"),
                        dbc.CardBody([
                            dcc.Graph(id="stats-graph", style={'height': '400px'})
                        ])
                    ])
                ])
            ], className="mt-3")
            
        ], fluid=True)
    
    def setup_callbacks(self):
        """设置回调函数"""
        
        @self.app.callback(
            [Output('point-cloud-graph', 'figure'),
             Output('data-info', 'children'),
             Output('stats-graph', 'figure')],
            [Input('load-button', 'n_clicks'),
             Input('point-size-slider', 'value'),
             Input('opacity-slider', 'value'),
             Input('sample-rate-slider', 'value'),
             Input('color-by-radio', 'value'),
             Input('viz-type-radio', 'value')],
            [dash.dependencies.State('file-dropdown', 'value'),
             dash.dependencies.State('auto-update-checkbox', 'value')]
        )
        def update_visualization(n_clicks, point_size, opacity, sample_rate, color_by, viz_type, selected_file, auto_update):
            # 获取触发回调的输入
            ctx = dash.callback_context
            if not ctx.triggered:
                trigger_id = 'load-button'
            else:
                trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            # 如果不是加载按钮触发且未开启自动更新，则不处理
            if trigger_id != 'load-button' and 'auto' not in (auto_update or []):
                # 返回当前图表不变
                return dash.no_update, dash.no_update, dash.no_update
            
            # 检查是否有文件被选中
            if selected_file is None:
                empty_fig = go.Figure()
                empty_fig.add_annotation(
                    text="请选择文件并点击加载按钮",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16)
                )
                return empty_fig, "请先选择并加载数据文件...", empty_fig
            
            try:
                # 加载数据
                file_ext = Path(selected_file).suffix.lower()
                if file_ext == '.csv':
                    df = self.load_csv_data(selected_file)
                elif file_ext in ['.pcd', '.ply']:
                    df = self.load_pcd_data(selected_file)
                else:
                    raise ValueError(f"不支持的文件格式: {file_ext}")
                
                # 采样
                n_points = len(df)
                sample_size = int(n_points * sample_rate)
                if sample_size > 0:
                    df_sampled = df.sample(n=min(sample_size, n_points)).copy()
                else:
                    df_sampled = df.copy()
                
                # 准备数据信息
                info_text = [
                    html.P(f"文件: {Path(selected_file).name}"),
                    html.P(f"总点数: {n_points:,}"),
                    html.P(f"采样点数: {len(df_sampled):,}"),
                    html.P(f"采样率: {sample_rate:.2%}"),
                    html.P(f"点大小: {point_size}"),
                    html.P(f"透明度: {opacity:.2f}"),
                ]
                
                if 'Points_m_XYZ:0' in df_sampled.columns:
                    x_range = f"[{df['Points_m_XYZ:0'].min():.3f}, {df['Points_m_XYZ:0'].max():.3f}]"
                    y_range = f"[{df['Points_m_XYZ:1'].min():.3f}, {df['Points_m_XYZ:1'].max():.3f}]"
                    z_range = f"[{df['Points_m_XYZ:2'].min():.3f}, {df['Points_m_XYZ:2'].max():.3f}]"
                    
                    info_text.extend([
                        html.P(f"X范围: {x_range} m"),
                        html.P(f"Y范围: {y_range} m"),
                        html.P(f"Z范围: {z_range} m"),
                    ])
                
                # 创建可视化图表
                fig = self.create_visualization(df_sampled, color_by, viz_type, point_size, opacity)
                
                # 创建统计图表
                stats_fig = self.create_stats_chart(df)
                
                return fig, info_text, stats_fig
                
            except Exception as e:
                error_fig = go.Figure()
                error_fig.add_annotation(
                    text=f"加载失败: {str(e)}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False, font=dict(size=16, color='red')
                )
                return error_fig, f"错误: {str(e)}", error_fig
    
    def create_visualization(self, df, color_by, viz_type, point_size, opacity):
        """创建可视化图表"""
        x = df['Points_m_XYZ:0']
        y = df['Points_m_XYZ:1']
        z = df['Points_m_XYZ:2']
        
        # 确定着色数据
        if color_by == 'height':
            colors = z
            color_label = 'Height (m)'
        elif color_by == 'intensity' and 'intensity' in df.columns:
            colors = df['intensity']
            color_label = 'Intensity'
        elif color_by == 'distance' and 'distance' in df.columns:
            colors = df['distance']
            color_label = 'Distance (m)'
        else:
            colors = z
            color_label = 'Height (m)'
        
        # 创建图表
        if viz_type == '3d':
            fig = go.Figure(data=[go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                marker=dict(
                    size=point_size,
                    color=colors,
                    colorscale='Viridis',
                    opacity=opacity,
                    colorbar=dict(title=color_label)
                ),
                text=[f'X: {x.iloc[i]:.3f}<br>Y: {y.iloc[i]:.3f}<br>Z: {z.iloc[i]:.3f}<br>{color_label}: {colors.iloc[i]:.3f}' 
                      for i in range(len(x))],
                hovertemplate='%{text}<extra></extra>'
            )])
            
            fig.update_layout(
                title='3D点云可视化',
                scene=dict(
                    xaxis_title='X (m)',
                    yaxis_title='Y (m)',
                    zaxis_title='Z (m)',
                    aspectmode='data'
                )
            )
            
        elif viz_type == 'xy':
            fig = px.scatter(x=x, y=y, color=colors, 
                           color_continuous_scale='Viridis',
                           labels={'x': 'X (m)', 'y': 'Y (m)', 'color': color_label},
                           title='XY平面投影')
            fig.update_traces(marker=dict(size=point_size, opacity=opacity))
            
        elif viz_type == 'xz':
            fig = px.scatter(x=x, y=z, color=colors,
                           color_continuous_scale='Viridis', 
                           labels={'x': 'X (m)', 'y': 'Z (m)', 'color': color_label},
                           title='XZ平面投影')
            fig.update_traces(marker=dict(size=point_size, opacity=opacity))
            
        elif viz_type == 'yz':
            fig = px.scatter(x=y, y=z, color=colors,
                           color_continuous_scale='Viridis',
                           labels={'x': 'Y (m)', 'y': 'Z (m)', 'color': color_label}, 
                           title='YZ平面投影')
            fig.update_traces(marker=dict(size=point_size, opacity=opacity))
        
        return fig
    
    def create_stats_chart(self, df):
        """创建统计图表"""
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('X坐标分布', 'Y坐标分布', 'Z坐标分布', '距离分布'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # X坐标分布
        fig.add_trace(
            go.Histogram(x=df['Points_m_XYZ:0'], name='X', nbinsx=30, opacity=0.7),
            row=1, col=1
        )
        
        # Y坐标分布  
        fig.add_trace(
            go.Histogram(x=df['Points_m_XYZ:1'], name='Y', nbinsx=30, opacity=0.7),
            row=1, col=2
        )
        
        # Z坐标分布
        fig.add_trace(
            go.Histogram(x=df['Points_m_XYZ:2'], name='Z', nbinsx=30, opacity=0.7),
            row=2, col=1
        )
        
        # 距离分布
        if 'distance' in df.columns:
            valid_distances = df[df['distance'] > 0]['distance']
            fig.add_trace(
                go.Histogram(x=valid_distances, name='Distance', nbinsx=30, opacity=0.7),
                row=2, col=2
            )
        
        fig.update_layout(
            title_text="数据分布统计",
            showlegend=False,
            height=400
        )
        
        return fig
    
    def run(self, debug=True, port=8050):
        """运行Web应用"""
        print(f"启动Web可视化服务器...")
        print(f"请在浏览器中访问: http://localhost:{port}")
        self.app.run(debug=debug, port=port, host='0.0.0.0')


def main():
    """主函数"""
    data_path = "/Users/yuii/Windows/temp"
    
    visualizer = WebLiDARVisualizer(data_path)
    visualizer.run(debug=False, port=8050)


if __name__ == "__main__":
    main() 