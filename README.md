# VISTA Project

## English

VISTA is an image library and AI-related application, including frontend and backend components.

### Project Structure

- `vista-backend/`: Python FastAPI backend server
- `vistapj/`: Frontend HTML/CSS/JavaScript application
- `bin/`: Tools and binaries (ignored)
- `.ssh/`: SSH keys (ignored)

### Installation and Running

#### Backend

```bash
cd vista-backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
copy .env.example .env        # add your API keys
python run.py
```

Open http://localhost:3000 — backend serves the frontend automatically.

API documentation: http://localhost:3000/docs

#### Frontend (standalone)

You can also open `vistapj/index.html` directly; it defaults to `http://localhost:3000` for API calls.

### License

ISC

## 中文

VISTA 是一个图像库与AI相关的应用，包括前端和后端组件。

### 项目结构

- `vista-backend/`: Python FastAPI 后端服务器
- `vistapj/`: 前端 HTML/CSS/JavaScript 应用
- `bin/`: 工具和二进制文件（已忽略）
- `.ssh/`: SSH 密钥（已忽略）

### 安装和运行

#### 后端

```bash
cd vista-backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # 填入 API Key
python run.py
```

浏览器打开 http://localhost:3000 即可（后端会自动托管前端）。

API 文档：http://localhost:3000/docs

#### 前端（独立运行）

也可以直接打开 `vistapj/index.html`；默认 API 地址为 `http://localhost:3000`。

#### 许可证

ISC