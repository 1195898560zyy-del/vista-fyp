"""Run the VISTA backend with uvicorn."""

import uvicorn

from app.config import get_settings


def _print_startup_hints(settings) -> None:
    print()
    print("=" * 42)
    print("  VISTA Backend")
    print("=" * 42)
    print(f"  浏览器打开: http://localhost:{settings.port}")
    print(f"  API 文档:   http://localhost:{settings.port}/docs")
    print()

    keys = {
        "UNSPLASH": bool(settings.unsplash_key),
        "PEXELS": bool(settings.pexels_key),
        "PIXABAY": bool(settings.pixabay_key),
        "WEATHER": bool(settings.weather_api_key),
        "OPENAI": bool(settings.resolved_openai_key),
        "REPLICATE": bool(settings.resolved_replicate_token),
    }
    loaded = [name for name, ok in keys.items() if ok]
    missing = [name for name, ok in keys.items() if not ok]

    if loaded:
        print(f"  已加载 Key: {', '.join(loaded)}")
    else:
        print("  [警告] .env 里没有 API Key，搜图/AI 会失败")
        print("         编辑 vista-backend/.env 填入 Key 后重启")

    if not keys["UNSPLASH"] and keys["PIXABAY"]:
        print("  [提示] 没配 UNSPLASH 时，前端搜图请选 Pixabay")
    if missing and loaded:
        print(f"  未配置: {', '.join(missing)}")
    print()


if __name__ == "__main__":
    settings = get_settings()
    _print_startup_hints(settings)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False,
    )
