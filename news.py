import requests
from bs4 import BeautifulSoup
import pandas as pd
from gensim.summarization import summarize
import nltk

nltk.download('punkt')


def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch URL: {url}, Status Code: {response.status_code}")
        return None
    return response.content


def text_summarizer(text):
    # Tokenize the text into sentences
    sentences = nltk.sent_tokenize(text)
    
    # Check if the text has less than 2 sentences
    if len(sentences) < 2:
        return text
    
    try:
        # Summarize the text
        summary = summarize(text)
        return summary
    except ValueError:
        # Handle the case where the text is too short to summarize
        return text


def parse_bollywood_hungama():
    url = 'https://www.bollywoodhungama.com/'
    content = fetch_url_content(url)
    if content is None:
        return pd.DataFrame()

    soup = BeautifulSoup(content, 'html.parser')
    headlines = soup.find_all(class_="large-6 medium-6 small-12 columns no-bullet")
    result = pd.DataFrame()

    for headline in headlines:
        items = headline.find_all('li', class_='clearfix')
        for item in items:
            a_tag = item.find('a')
            if a_tag:
                href = a_tag['href']
                title = a_tag['title']
                result = result.append({'title': title, 'link': href}, ignore_index=True)

    for i in range(len(result)):
        url = result['link'][i]
        content = fetch_url_content(url)
        if content is None:
            continue
        
        soup = BeautifulSoup(content, 'html.parser')
        entry_content = soup.find('div', class_='entry-content post-content clearfix')
        article_content = ''
        
        if entry_content:
            content_paragraphs = entry_content.find_all('p')
            article_content = ' '.join([para.get_text() for para in content_paragraphs])
            article_content = text_summarizer(article_content)
        
        result.loc[i, 'content'] = article_content

    result.to_csv('bollywood_hungama.csv', index=False)
    return result


def parse_indian_express():
    url = 'https://indianexpress.com/section/entertainment/bollywood/'
    content = fetch_url_content(url)
    if content is None:
        return pd.DataFrame()

    soup = BeautifulSoup(content, 'html.parser')
    headlines = soup.find_all(class_="nation")
    result = pd.DataFrame()

    for headline in headlines:
        items = headline.find_all(class_=['title'])
        for item in items:
            a_tag = item.find('a')
            if a_tag:
                href = a_tag['href']
                title = a_tag['title']
                result = result.append({'title': title, 'link': href}, ignore_index=True)

    for i in range(len(result)):
        url = result['link'][i]
        content = fetch_url_content(url)
        if content is None:
            continue
        
        soup = BeautifulSoup(content, 'html.parser')
        entry_content = soup.find('div', class_='story_details')
        article_content = ''
        
        if entry_content:
            content_paragraphs = entry_content.find_all('p')
            article_content = ' '.join([para.get_text() for para in content_paragraphs])
            article_content = text_summarizer(article_content)
        
        result.loc[i, 'content'] = article_content

    result.to_csv('indian_express.csv', index=False)
    return result


def main():
    bollywood_hungama_df = parse_bollywood_hungama()
    indian_express_df = parse_indian_express()

    final_df = pd.concat([bollywood_hungama_df, indian_express_df], ignore_index=True)
    final_df.to_csv('combined_movies.csv', index=False)


if __name__ == "__main__":
    main()
