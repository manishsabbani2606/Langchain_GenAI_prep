from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()


#Intialize th LLM

llm = ChatOpenAI(model="gpt-4-0613", temperature=0.7, max_tokens=1000)


#tesla information

telsa_info = """
Tesla was incorporated in July 2003 by Martin Eberhard and Marc Tarpenning as Tesla Motors. Its name is a tribute to the inventor and electrical engineer Nikola Tesla. In February 2004, Elon Musk led Tesla's first funding round and became the company's chairman, subsequently claiming to be a co-founder; in 2008, he was named chief executive officer. The company began production of its first car model, the Roadster sports car, in 2008; the Model S sedan in 2012; the Model X SUV in 2015; the Model 3 sedan in 2017; the Model Y crossover in 2020; the Tesla Semi truck in 2022; and the Cybertruck pickup truck in 2023.

Tesla is one of the world's most valuable companies in terms of market capitalization. Starting in July 2020, it has been the world's most valuable automaker. From October 2021 to March 2022, Tesla was a US$1 trillion company, the sixth US company to reach that valuation. In 2023, the company was ranked 69th in the Forbes Global 2000.[5] In 2024, the company led the battery electric vehicle market, with 17.6% share.

Tesla exceeded $1 trillion in market capitalization again between November 2024[6] and February 2025,[7] and since May 2025.[8] In November 2025, Tesla approved a pay package worth $1 trillion for Musk, which he is to receive over 10 years if he meets specific goals.[9] In January 2026, the company would lose its status as world's lead manufacturer of electric vehicles.[10]

Tesla has been the subject of lawsuits, boycotts, government scrutiny, and journalistic criticism, stemming from allegations of multiple cases of whistleblower retaliation, worker rights violations such as sexual harassment and anti-union activities, safety defects leading to dozens of recalls, the lack of a public relations department, and controversial statements from Musk, including overpromising on the company's driving assist technology and product release timelines.

"""


#creating the prompt for chunking

prompt = f"""

You are a helpful assistant that can chunk the information provided to you.
Here is the information:
{telsa_info}
Please chunk the information into 3 parts and provide a summary for each part.

return the text with <<SPLIT>> as the separator between the chunks and summaries.

"""

print("Asking the LLM to chunk the information and provide summaries...")

response = llm.invoke(prompt)
print("Response from the LLM:")
print(response)

marked_chunks = response.split("<<SPLIT>>")

for i, chunk in enumerate(marked_chunks):
    print(f"Chunk {i+1}:")
    print(chunk.strip())
    print("\n" + "="*50 + "\n")
    