# 雷达点云数据可视化程序

这是一个专门为雷达点云数据设计的可视化程序，支持多种数据格式和可视化方式。

## 功能特性

- 📊 **多格式支持**: 支持CSV、PCD、PLY格式的点云数据
- 🎨 **多种可视化方式**: 
  - Matplotlib 3D静态可视化
  - Plotly 交互式3D可视化  
  - Open3D 高质量3D可视化
  - Web浏览器交互式界面
- 🎯 **灵活的着色方案**: 支持按高度、强度、距离着色
- 📈 **数据分析**: 自动统计和分析点云数据特征
- ⚡ **性能优化**: 支持数据采样以提高大数据集的渲染性能

## 安装依赖

### 方式1: 使用pip安装
```bash
pip install -r requirements.txt
```

### 方式2: 手动安装
```bash
pip install numpy pandas matplotlib plotly dash dash-bootstrap-components
pip install open3d scikit-learn opencv-python
```

## 使用方法

### 1. 命令行交互式程序
```bash
python lidar_visualizer.py
```

这将启动交互式命令行界面，提供以下选项：
- 自动扫描并加载点云文件
- 选择不同的可视化方式
- 调整采样率和着色方案
- 查看数据统计分析

### 2. Web界面程序
```bash
python web_visualizer.py
```

然后在浏览器中访问 `http://localhost:8050`

Web界面提供：
- 直观的图形用户界面
- 实时交互式3D可视化
- 多种投影视图
- 详细的数据统计图表

## 数据格式说明

### CSV格式
程序期望CSV文件包含以下列：
- `Points_m_XYZ:0`: X坐标 (米)
- `Points_m_XYZ:1`: Y坐标 (米)  
- `Points_m_XYZ:2`: Z坐标 (米)
- `intensity`: 反射强度
- `distance`: 距离 (米)
- `timestamp`: 时间戳

### PCD/PLY格式
标准的点云数据格式，程序会自动解析XYZ坐标和颜色信息。

## 可视化选项

### 着色方式
- **高度着色**: 根据Z坐标值着色，适合显示地形起伏
- **强度着色**: 根据反射强度着色，适合区分不同材质
- **距离着色**: 根据距离传感器的距离着色，适合分析探测范围

### 采样率
为了提高大数据集的渲染性能，可以调整采样率：
- 0.01 (1%): 快速预览
- 0.1 (10%): 平衡性能和质量  
- 1.0 (100%): 完整显示（小数据集推荐）

## 程序结构

```
├── lidar_visualizer.py    # 主要的命令行可视化程序
├── web_visualizer.py      # Web界面版本
├── requirements.txt       # 依赖库列表
└── README.md             # 说明文档
```

## 主要类和方法

### LiDARVisualizer 类
- `load_csv_data()`: 加载CSV格式数据
- `load_pcd_data()`: 加载PCD格式数据  
- `load_ply_data()`: 加载PLY格式数据
- `visualize_matplotlib_3d()`: Matplotlib 3D可视化
- `visualize_plotly_3d()`: Plotly交互式可视化
- `visualize_open3d()`: Open3D高质量可视化
- `analyze_data()`: 数据统计分析

### WebLiDARVisualizer 类
- 基于Dash的Web应用
- 提供图形用户界面
- 实时交互式可视化

## 使用示例

### 快速开始
1. 将点云数据文件放在指定目录
2. 运行程序: `python lidar_visualizer.py`
3. 选择文件和可视化选项
4. 享受交互式3D可视化体验

### Web界面使用
1. 运行: `python web_visualizer.py`
2. 打开浏览器访问 `http://localhost:8050`
3. 在界面中选择文件和参数
4. 点击"加载并可视化"按钮

## 性能建议

- 对于大数据集（>100万点），建议使用0.01-0.1的采样率
- Web界面在处理大数据时可能需要更长加载时间
- Open3D可视化提供最佳的3D交互体验

## 故障排除

### 常见问题
1. **导入错误**: 确保所有依赖库已正确安装
2. **文件读取失败**: 检查文件路径和格式是否正确
3. **内存不足**: 减少采样率或处理较小的数据文件
4. **Web界面无法访问**: 确保端口8050未被占用

### 调试模式
在代码中设置 `debug=True` 可以获得更详细的错误信息。

## 系统要求

- Python 3.7+
- 8GB+ RAM (推荐，处理大数据集时)
- 支持OpenGL的显卡 (Open3D可视化)

## 更新日志

### v1.0
- 支持CSV、PCD、PLY格式
- 多种可视化方式
- 交互式Web界面
- 数据统计分析功能 