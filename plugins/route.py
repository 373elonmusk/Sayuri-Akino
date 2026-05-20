import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

# Bot client reference - set in bot.py start()
bot_client = None


def set_client(client):
    global bot_client
    bot_client = client


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({
        "status": "running",
        "bot": "File Sharing Bot",
        "endpoints": ["/stream/{msg_id}", "/download/{msg_id}"]
    })


@routes.get("/stream/{msg_id}")
async def stream_handler(request):
    """Stream a Telegram file directly in browser"""
    msg_id = request.match_info.get("msg_id")
    return await _serve_file(request, msg_id, inline=True)


@routes.get("/download/{msg_id}")
async def download_handler(request):
    """Force download a Telegram file"""
    msg_id = request.match_info.get("msg_id")
    return await _serve_file(request, msg_id, inline=False)


async def _serve_file(request: web.Request, msg_id: str, inline: bool):
    if bot_client is None:
        return web.Response(status=503, text="Bot not ready yet.")

    try:
        msg_id = int(msg_id)
    except ValueError:
        return web.Response(status=400, text="Invalid message ID.")

    try:
        message = await bot_client.get_messages(
            chat_id=bot_client.db_channel.id,
            message_ids=msg_id
        )
    except Exception as e:
        logger.error(f"get_messages error: {e}")
        return web.Response(status=404, text="File not found.")

    if not message or not message.media:
        return web.Response(status=404, text="No media in this message.")

    # Get file info
    media = (
        message.video or
        message.document or
        message.audio or
        message.photo or
        message.animation
    )
    if not media:
        return web.Response(status=404, text="Unsupported media type.")

    file_name = getattr(media, "file_name", None) or f"file_{msg_id}"
    file_size = getattr(media, "file_size", 0)
    mime_type = getattr(media, "mime_type", "application/octet-stream")

    # Range request support (needed for video seeking)
    range_header = request.headers.get("Range", None)
    offset = 0
    end    = file_size - 1

    if range_header:
        try:
            range_val = range_header.replace("bytes=", "")
            parts     = range_val.split("-")
            offset    = int(parts[0]) if parts[0] else 0
            end       = int(parts[1]) if parts[1] else file_size - 1
        except Exception:
            pass

    chunk_size    = min(1024 * 1024, end - offset + 1)  # 1MB chunks
    content_range = f"bytes {offset}-{end}/{file_size}"

    disposition = "inline" if inline else f'attachment; filename="{file_name}"'

    response = web.StreamResponse(
        status=206 if range_header else 200,
        headers={
            "Content-Type":        mime_type,
            "Content-Disposition": disposition,
            "Content-Range":       content_range,
            "Content-Length":      str(end - offset + 1),
            "Accept-Ranges":       "bytes",
        }
    )
    await response.prepare(request)

    # Stream file from Telegram
    try:
        async for chunk in bot_client.stream_media(message, offset=offset, limit=chunk_size):
            await response.write(chunk)
            if response.task is None or response.task.done():
                break
    except Exception as e:
        logger.error(f"Streaming error: {e}")

    await response.write_eof()
    return response


# Jishu Developer
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
