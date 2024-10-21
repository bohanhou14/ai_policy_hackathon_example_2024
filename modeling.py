from data_utils import read_jsonl
import argparse
from top2vec import Top2Vec
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


def model_papers(abstracts):
    # Model the papers
    model = Top2Vec(documents=abstracts, speed="learn", workers=4)
    return model


def generate_summary(texts, max_length=20):
    summaries = []
    tokenizer = AutoTokenizer.from_pretrained("microsoft/Phi-3.5-mini-instruct")
    model = AutoModelForCausalLM.from_pretrained(
        "microsoft/Phi-3.5-mini-instruct", 
        device_map="cpu", 
        torch_dtype="auto", 
        trust_remote_code=True, 
    )
    sys_prompt = "You are an academic expert in LLM agents, and you are helping to do literature review on the topics."
    def input_prompt(words):
        return f"Based on the list of input words {str(words)}, only output 1-5 words to describe the academic topic:"
    
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

    for text in tqdm(texts, desc="Generating summaries"):
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": input_prompt(text)},
        ]
        message = pipe(text, messages=messages, max_new_tokens=max_length)
        summaries.append(message[0]["generated_text"])
    return summaries


if __name__ == "__main__":
    # Read data from the JSONL file
    parser = argparse.ArgumentParser(description='Model arXiv agent papers into different categories')
    parser.add_argument('--input', type=str, default="data.jsonl", help='input file')
    args = parser.parse_args()
    data = read_jsonl(args.input)
    abstracts = [paper["abstract"] for paper in data]
    dates = [paper["date"] for paper in data]
    model = model_papers(abstracts)
    topic_sizes, topic_nums = model.get_topic_sizes()
    breakpoint()
    all_topic_words = []
    for topic in topic_nums:
        words, word_scores = model.get_topics(topic)
        all_topic_words.append(words)
    summaries = generate_summary(all_topic_words)


    

