# 教科书分析器 - 智能学习材料助手

一款使用Yandex云人工智能技术分析和解释教育材料的应用程序。

## 功能
- 从教科书图像中识别文本（OCR）
- 教育材料的智能分析和详细解释
- 回答有关教科书内容的问题
- 生成示例和额外的学习材料

## 技术
- Python 3.9+
- Flask
- Yandex Cloud Vision API（OCR）
- YandexGPT API
- Bootstrap 5

## 安装和启动

### 前提条件
- Python 3.9或更高版本
- 拥有配置好服务账户的Yandex云账户
- IAM令牌和Yandex云文件夹ID

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/username/textbook-analyzer.git
cd textbook-analyzer
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 设置环境变量
```bash
export YANDEX_IAM_TOKEN=your_token
export YANDEX_FOLDER_ID=your_folder_id
```

4. 启动应用
```bash
flask run
```

启动后，应用将可在http://localhost:5000访问
