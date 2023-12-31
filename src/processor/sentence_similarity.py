import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load the pre-trained SentenceTransformer model for generating sentence embeddings.
models = [
    'sentence-transformers/all-mpnet-base-v2', # 0.6 / 0.5
    'sentence-transformers/all-MiniLM-L12-v2', # 0.4
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', # 10
    'sentence-transformers/all-MiniLM-L6-v2', # 0.4
    
    'multi-qa-MiniLM-L6-cos-v1', #tensor([[0.2033, 0.1526, 0.5856, 0.2388]])
    'sentence-transformers/xlm-r-100langs-bert-base-nli-stsb-mean-tokens', #tensor([[191.1041, 219.5202, 126.4406,  72.7892]])
    'sentence-transformers/distiluse-base-multilingual-cased-v2', # tensor([[0.2931, 0.4783, 0.2947, 0.0468]])
    'dean-ai/legal_heBERT_ft', #tensor([[221.9029, 287.2466, 288.1569, 188.1941]])
    'intfloat/multilingual-e5-large',
    ]

model_name = 'sentence-transformers/all-mpnet-base-v2'
default_threshold = 0.7

def verify_model(model_name):
    model = SentenceTransformer(model_name, device="cpu")
    import time
    start = time.time()
    query_embedding = model.encode(arr[0])
    passage_embedding = model.encode(arr[1:])
    end = time.time()
    print(f"mode {model_name} score: {util.dot_score(query_embedding, passage_embedding)}, took {end - start}")
 
def text_similarity_check(text_to_match, compare_list, threshold=default_threshold):
    if len(compare_list) == 0:
      return False
    if len(text_to_match) == 0:
      return False
    model = SentenceTransformer(model_name, device="cpu")
    query_embedding = model.encode(text_to_match)
    passage_embedding = model.encode(compare_list)
    
    scores = util.dot_score(query_embedding, passage_embedding)
    
    scores = scores[0].tolist()
    idx_text_score_list = [(i, compare_list[i], score) for i, score in enumerate(scores)]
    #TODO: take the max and compare to threshold
    idx_text_score_list.sort(key=lambda x: x[2],reverse=True)
    top_text_with_scores = idx_text_score_list[0]
    max_score = idx_text_score_list[0][2]
    print(f"text_to_match:\n\t {text_to_match}\ntop_text_with_scores:\n\t {top_text_with_scores[1]}, \nscore: {max_score}, returning {max_score > threshold}")
    return max_score > threshold
    
    
if __name__ == '__main__':
  from googletrans import Translator
  trans = Translator()
  arr = [
    "Arab report: pro-Iranian militias attacked the base of American forces in Syria",
    "The air force attacks in southern Lebanon,",
    
      """Amit Segal reports:

The security measure being tested in Israel in coordination with Egypt: placing our security personnel on the Egyptian side of the Rafah crossing, to prevent the escape of Hamas leaders and the smuggling of hostages
""",
      """☄️ Heavy exchanges of fire in the Gaza Strip -
At the same time, the IDF is in a wave of attacks."""]
  
#     """   The damage to the ship near Bab Almandav - near the coast of Yemen

# US Central Command updates: The tanker Strinda was hit by a cruise missile fired at it from territory controlled by the Houthis while it was passing by the Bab Almandab Straits.
# A fire broke out on board the tanker following the attack, but there were no reports of casualties.
# The attack was carried out while there were no US Navy vessels in the area, but the destroyer USS Mason responded to the tanker's distress call.
# Abu Ali
# top_text_with_scores:""",
#     """The damage to the ship near Bab Almandav - near the coast of Yemen

# US Central Command updates: The tanker Strinda was hit by a cruise missile fired at it from territory controlled by the Houthis while it was passing by the Bab Almandab Straits.
# A fire broke out on board the tanker following the attack, but there were no reports of casualties.
# The attack was carried out while there were no US Navy vessels in the area, but the destroyer USS Mayson responded to the tanker's distress call., """

  #   'זה אדם שמח',
  #   'האיש הזה לא מפסיק לחייך', 
  #   'הוא מאושר',
  #   'איזה אדם אגדה',
  #   'חבר יקר ביקש לשאול לשלומך',
  #   'עוד אחד שבא להרים',
  #   'אח שלי אוהב שוקולד'
  # ]
  arr = [t.text for t in trans.translate(arr, src='he', dest='en')]
  for model_name in models:   
      # Expected is: #  Highest, Highest, Low, Lowest, Lowest, Lowest
      verify_model(model_name)



"""    
import torch.nn.functional as F

from torch import Tensor
from transformers import AutoTokenizer, AutoModel


def average_pool(last_hidden_states: Tensor,
                 attention_mask: Tensor) -> Tensor:
    last_hidden = last_hidden_states.masked_fill(~attention_mask[..., None].bool(), 0.0)
    return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]


# Each input text should start with "query: " or "passage: ", even for non-English texts.
# For tasks other than retrieval, you can simply use the "query: " prefix.
input_texts = ['query: how much protein should a female eat',
               'query: 南瓜的家常做法',
               "passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.",
               "passage: 1.清炒南瓜丝 原料:嫩南瓜半个 调料:葱、盐、白糖、鸡精 做法: 1、南瓜用刀薄薄的削去表面一层皮,用勺子刮去瓤 2、擦成细丝(没有擦菜板就用刀慢慢切成细丝) 3、锅烧热放油,入葱花煸出香味 4、入南瓜丝快速翻炒一分钟左右,放盐、一点白糖和鸡精调味出锅 2.香葱炒南瓜 原料:南瓜1只 调料:香葱、蒜末、橄榄油、盐 做法: 1、将南瓜去皮,切成片 2、油锅8成热后,将蒜末放入爆香 3、爆香后,将南瓜片放入,翻炒 4、在翻炒的同时,可以不时地往锅里加水,但不要太多 5、放入盐,炒匀 6、南瓜差不多软和绵了之后,就可以关火 7、撒入香葱,即可出锅"]

tokenizer = AutoTokenizer.from_pretrained('intfloat/multilingual-e5-large')
model = AutoModel.from_pretrained('intfloat/multilingual-e5-large')

# Tokenize the input texts
batch_dict = tokenizer(input_texts, max_length=512, padding=True, truncation=True, return_tensors='pt')

outputs = model(**batch_dict)
embeddings = average_pool(outputs.last_hidden_state, batch_dict['attention_mask'])

# normalize embeddings
embeddings = F.normalize(embeddings, p=2, dim=1)
scores = (embeddings[:2] @ embeddings[2:].T) * 100
print(scores.tolist())

"""
    
"""
def generate_embedding(text):
    response = model.encode([text])  # Encode the text using the pre-trained model
    return np.array(response[0])  # Return the generated embedding as a NumPy array


## 

# import numpy as np
class VectorStore:
  def __init__(self):
    self.documents = []
    self.embeddings = np.empty((0,384))  # Initialize as empty array

  def add_to_store(self, document):
    # Append the document to the list of documents
    self.documents.append(document)

    # Generate the embedding for the document
    embedding = generate_embedding(document.content)

    # Concatenate the response with the existing embeddings vertically
    self.embeddings = np.vstack((self.embeddings, embedding))

## 

def generate_vector_store():
  store = VectorStore()

  for i in range(len(docs)):
    print(f"Processing {i}...")
    store.add_to_store(docs[i])

  return store



##

import faiss

def create_index(embeddings):
  # Create an index with the same dimension as the embeddings
  index = faiss.IndexFlatL2(embeddings.shape[1])

  # Add the embeddings to the index
  index.add(embeddings)

  # Return the created index
  return index

##

import faiss
faiss.write_index(store.create_index(), 'index.faiss')

##

import numpy as np

# Generate embedding for the given query
query_embedding = generate_embedding("healthiest types of meat")

# Search for similar embeddings in the index
distances, results = index.search(np.array([query_embedding]), k=3)

# Print the content of the documents
for i in results[0]:
  print(docs[i].content)


##

# Import required libraries
import numpy as np

# Set the similarity threshold
similarityThreshold = 1

# Generate embedding for the given query
query_embedding = generate_embedding("healthiest types of meat")

# Search for similar embeddings in the index
distances, results = index.search(np.array([query_embedding]), k=3)

# Filter the results based on the similarity threshold
filtered_results = []
for i, distance in zip(results[0], distances[0]):
  if distance <= similarityThreshold:
    filtered_results.append(i)

# Print the content of the documents
for i in filtered_results:
  print(docs[i].content)
"""