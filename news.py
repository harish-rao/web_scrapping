import requests
from bs4 import BeautifulSoup
import pandas as pd
from gensim.summarization import summarize
import nltk
nltk.download('punkt')

# Function to summarize text using Gensim's summarize function
def summarize_text(text):
    sentences = nltk.sent_tokenize(text)
    if len(sentences) < 2:
        return text
    try:
        summary = summarize(text)
        return summary
    except ValueError:
        return text

# Function to fetch content from a given URL
def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        return None
    return response.text

# Function to fetch content from a given URL
def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        return None
    return response.text

# Function to extract headlines and their corresponding links from parsed headlines
def extract_headlines_links(headlines, class_headers):
    result = pd.DataFrame(columns=['title', 'link'])
    for headline in headlines:
        items = headline.find_all(class_=class_headers)
        for item in items:
            a_tag = item.find('a')
            if a_tag:
                href = a_tag.get('href')
                title = a_tag.get('title', 'No title available')
                result = result.append({'title': title, 'link': href}, ignore_index=True)
    return result

# Function to retrieve and summarize article content from a list of URLs
def retrieve_summarize_articles(df, class_headers):
    for i, row in df.iterrows():
        url = row['link']
        content = fetch_url_content(url)
        if content is None:
            continue
        
        soup = BeautifulSoup(content, 'html.parser')
        entry_content = soup.find('div', class_=class_headers)
        article_content = ''
        
        if entry_content:
            content_paragraphs = entry_content.find_all('p')
            article_content = ' '.join([para.get_text() for para in content_paragraphs])
            article_content = summarize_text(article_content)
        
        df.loc[i, 'content'] = article_content
    return df

# Function to fetch Bollywood news from Bollywood Hungama website
def fetch_bollywoodhungama_news():
    url = 'https://www.bollywoodhungama.com/'
    response = fetch_url_content(url)
    headlines = parse_website(response, "large-6 medium-6 small-12 columns no-bullet")
    df = extract_headlines_links(headlines, 'clearfix')
    bollywoodhungama_news = retrieve_summarize_articles(df, 'entry-content post-content clearfix')
    return bollywoodhungama_news

# Function to fetch Bollywood news from Indian Express website
def fetch_indianexpress_news():
    url = 'https://indianexpress.com/section/entertainment/bollywood/'
    response = fetch_url_content(url)
    headlines = parse_website(response, "nation")
    df = extract_headlines_links(headlines, 'title')
    indianexpress_news = retrieve_summarize_articles(df, 'story_details')
    return indianexpress_news

# Main function to orchestrate the entire process
def main():
    bollywood_hungama_df = fetch_bollywoodhungama_news()
    indian_express_df = fetch_indianexpress_news()
    final_df = pd.concat([bollywood_hungama_df, indian_express_df], ignore_index=True)
    final_df.to_csv('top_trending_bollywood_news.csv', index=False)

# Entry point of the script
if __name__ == "__main__":
    main()
