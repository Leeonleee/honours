import os
from rank_bm25 import BM25Okapi
import nltk
nltk.download('punkt')



# Get all files in a directory
def get_all_cc_files(directory):
    cc_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.cc'):  # Only .cc files
                full_path = os.path.join(root, file)
                cc_files.append(full_path)
    return cc_files

# Read file contents
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
    
# Preprocess and tokenize document contents
def preprocess(text):
    return nltk.tokenize.word_tokenize(text.lower())  # You can extend this with stopword removal, etc.

def main(directory):
    # 1. Get all .cc files
    cc_files = get_all_cc_files(directory)
    print(f"Found {len(cc_files)} .cc files in {directory}.")

    # 2. Read and tokenize file contents
    tokenized_docs = []
    for file in cc_files:
        content = read_file(file)
        tokenized_docs.append(preprocess(content))

    # 3. Initialize BM25 with tokenized documents
    bm25 = BM25Okapi(tokenized_docs)

    # 4. Query Example (for demonstration)
    query = "Blob files were not reclaimed after deleting all the SST files"
    tokenized_query = preprocess(query)

    # 5. Rank documents based on query
    scores = bm25.get_scores(tokenized_query)

    # 6. Output the ranked documents based on the query
    print(f"\nQuery: {query}")
    for idx, score in enumerate(scores):
        print(f"Doc {idx+1}: {cc_files[idx]} (Score: {score})")

    # Optionally: Retrieve the most relevant document
    best_match_idx = scores.index(max(scores))
    print("\nMost relevant document:", cc_files[best_match_idx])

# Run the script
if __name__ == "__main__":
    directory = "/Users/leonlee/Documents/University/Y4/honours/rocksdb"  # Set the directory containing your .cc files
    main(directory)