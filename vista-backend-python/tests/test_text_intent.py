from app.utils.text_intent import infer_tool_from_text


def test_greeting():
    result = infer_tool_from_text("hello", {})
    assert result == {"reply": "Hi! What would you like to do—search images, generate, or check weather?"}


def test_search_intent():
    result = infer_tool_from_text("show me cats", {"preferred_ratio": "16:9"})
    assert result is not None
    assert result["tools"][0]["name"] == "search_library"
    assert result["tools"][0]["args"]["query"] == "cats"
    assert result["tools"][0]["args"]["ratio"] == "16:9"


def test_refine_without_image():
    result = infer_tool_from_text("refine this image", {})
    assert result == {"reply": "Please open an image in the gallery first so I can refine it."}
