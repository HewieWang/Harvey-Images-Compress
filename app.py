import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="图片转换 & 压缩", layout="wide")
st.title("🖼️ 图片格式转换 & 压缩工具")
st.markdown("上传图片，选择目标格式和压缩质量，一键转换并下载。")

with st.sidebar:
    st.header("⚙️ 转换设置")
    output_format = st.selectbox("目标格式", ["WebP", "JPEG", "PNG"], index=0)
    quality = st.slider("压缩质量", 1, 100, 80)
    if output_format == "PNG":
        st.info("💡 PNG 为无损格式，质量滑块仅影响压缩率。")
        quality = min(quality, 100)

uploaded_file = st.file_uploader("📁 选择图片文件", type=["png", "jpg", "jpeg", "bmp", "tiff", "webp"])

if uploaded_file is not None:
    original = Image.open(uploaded_file)
    original_format = original.format
    original_size = uploaded_file.size          # ✅ 修正点
    original_dims = original.size

    # 透明处理（JPEG 不支持透明）
    if output_format == "JPEG" and original.mode in ("RGBA", "LA", "P"):
        st.warning("⚠️ 原图包含透明通道，已用白色背景填充。")
        background = Image.new("RGB", original.size, (255, 255, 255))
        if original.mode == "P":
            original = original.convert("RGBA")
        background.paste(original, mask=original.split()[-1])
        processed = background
    else:
        processed = original.copy()

    output_buffer = BytesIO()
    save_kwargs = {"format": output_format}
    if output_format == "JPEG":
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif output_format == "WebP":
        save_kwargs["quality"] = quality
        save_kwargs["method"] = 6
    elif output_format == "PNG":
        png_compress = max(1, min(9, round((100 - quality) / 100 * 9)))
        save_kwargs["compress_level"] = png_compress

    try:
        processed.save(output_buffer, **save_kwargs)
        output_buffer.seek(0)
        converted_bytes = output_buffer.getvalue()
        converted_size = len(converted_bytes)
    except Exception as e:
        st.error(f"转换失败: {e}")
        st.stop()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📷 原始图片")
        st.image(original, use_container_width=True)
        st.caption(f"格式: {original_format} | 尺寸: {original_dims[0]}×{original_dims[1]}")
        st.caption(f"文件大小: {original_size/1024:.1f} KB")
    with col2:
        st.subheader("✨ 转换后")
        st.image(converted_bytes, use_container_width=True)
        st.caption(f"格式: {output_format} | 尺寸: {processed.size[0]}×{processed.size[1]}")
        st.caption(f"文件大小: {converted_size/1024:.1f} KB")

    if original_size > 0:
        reduction = (1 - converted_size / original_size) * 100
        if reduction > 0:
            st.success(f"📉 体积减少了 {reduction:.1f}%")
        elif reduction < 0:
            st.warning(f"📈 体积增加了 {-reduction:.1f}%，请调整质量参数。")

    st.download_button(
        label=f"⬇️ 下载 {output_format} 文件",
        data=converted_bytes,
        file_name=f"converted.{output_format.lower()}",
        mime=f"image/{output_format.lower()}"
    )

st.caption("仅浏览器端处理，图片不会上传到服务器。")
