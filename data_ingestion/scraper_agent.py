import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ScrapeRequest(BaseModel):
    query: str

@app.post("/scrape_earnings")
async def scrape_earnings(request: ScrapeRequest):
    """Scrape earnings news from Yahoo Finance."""
    url = f"https://finance.yahoo.com/quote/{request.query}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('h3', class_='Mb(5px)')
    
    earnings = []
    for article in articles[:5]:  # Limit to top 5 articles
        title = article.text
        if "earnings" in title.lower():
            earnings.append({"title": title, "source": "Yahoo Finance"})
    
    return {"earnings_news": earnings}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)