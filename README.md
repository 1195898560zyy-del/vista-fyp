# VISTA Project

## English

VISTA is an image library and AI-related application, including frontend and backend components.

### Project Structure

- `vista-backend/`: Node.js Express backend (legacy)
- `vista-backend-python/`: Python FastAPI backend (migration target)
- `vistapj/`: Frontend HTML/CSS/JavaScript application
- `docs/`: Backend refactor plan and API contract
- `bin/`: Tools and binaries (ignored)
- `.ssh/`: SSH keys (ignored)

### Installation and Running

#### Python backend (recommended)

```bash
cd vista-backend-python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 3000
```

See `docs/BACKEND_REFACTOR_PLAN.md` for migration details.

#### Node backend (legacy)

```bash
cd vista-backend
npm install
node server.js
```

#### Frontend

Open `vistapj/index.html` in the browser (defaults to `http://localhost:3000` on localhost).

### License

ISC

## 中文

VISTA 是一个图像库与AI相关的应用，包括前端和后端组件。

### 项目结构

- `vista-backend/`：Node.js Express 后端（旧版）
- `vista-backend-python/`：Python FastAPI 后端（迁移目标）
- `vistapj/`：前端 HTML/CSS/JavaScript 应用
- `docs/`：后端重构计划与 API 契约
- `bin/`：工具和二进制文件（已忽略）
- `.ssh/`：SSH 密钥（已忽略）

### 安装和运行

#### Python 后端（推荐）

```bash
cd vista-backend-python
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 3000
```

详见 `docs/BACKEND_REFACTOR_PLAN.md`。

#### Node 后端（旧版）

```bash
cd vista-backend
npm install
node server.js
```

#### 前端

打开 `vistapj/index.html` 在浏览器中（本地默认连接 `http://localhost:3000`）。

#### 许可证

ISC