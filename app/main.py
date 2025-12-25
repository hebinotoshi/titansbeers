from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from typing import Optional

from .line_handler import verify_signature, process_webhook

app = FastAPI(
    title="Titans Beers Line Bot",
    description="Line bot for Titans Craft Beer Bar",
    version="1.0.0",
)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Titans Beers Bot is running!"}


@app.post("/webhook")
async def webhook(
    request: Request,
    x_line_signature: Optional[str] = Header(None),
):
    """Handle Line webhook events."""
    body = await request.body()

    # Verify signature
    if x_line_signature:
        if not verify_signature(body, x_line_signature):
            raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse and process the webhook
    try:
        body_json = await request.json()
        process_webhook(body_json)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        # Still return 200 to Line to prevent retries
        pass

    return JSONResponse(content={"status": "ok"})


@app.get("/test-scrape")
async def test_scrape():
    """Test endpoint to verify scraping works."""
    from .scraper import scrape_beers

    beers = scrape_beers()
    return {
        "count": len(beers),
        "beers": beers[:3] if beers else [],  # Return first 3 for testing
    }
