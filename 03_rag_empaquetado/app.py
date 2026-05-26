from flask import Flask, render_template, request, jsonify
import os
import chromadb
import ollama

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class OllamaEmbeddings:
    def __call__(self, input):
        embeddings = []
        for text in input:
            response = ollama.embed(model='nomic-embed-text', input=text)
            embeddings.append(response['embeddings'][0])
        return embeddings

    def name(self):
        return "ollama-nomic"

    def embed_query(self, input):
        return self.__call__(input)

    def embed_documents(self, input):
        return self.__call__(input)

client = chromadb.PersistentClient(path='./chroma_rag_empaquetado')

def chunk_text(text, chunk_size=300, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += chunk_size - overlap
    return chunks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    collection_name = request.form.get('collection_name', 'default_collection')
    
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
        
    if file and file.filename.endswith('.txt'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = chunk_text(text)
        
        # Guardar en ChromaDB
        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=OllamaEmbeddings()
        )
        
        # Necesitamos IDs únicos. Buscamos el count actual.
        current_count = collection.count()
        ids = [f"doc_{current_count + i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)
        
        return jsonify({"message": f"Archivo procesado. {len(chunks)} chunks añadidos a la colección '{collection_name}'."}), 200
        
    return jsonify({"error": "Solo se permiten archivos .txt"}), 400

@app.route('/api/collections', methods=['GET'])
def get_collections():
    cols = client.list_collections()
    col_list = [{"name": c.name, "count": c.count()} for c in cols]
    return jsonify(col_list)

@app.route('/api/collections/<name>', methods=['DELETE'])
def delete_collection(name):
    try:
        client.delete_collection(name)
        return jsonify({"message": "Colección borrada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query():
    data = request.get_json()
    question = data.get('question', '')
    collection_name = data.get('collection_name', '')
    
    if not question or not collection_name:
        return jsonify({"error": "Pregunta o colección no proporcionada"}), 400
        
    try:
        collection = client.get_collection(name=collection_name, embedding_function=OllamaEmbeddings())
        results = collection.query(query_texts=[question], n_results=3)
        chunks = results['documents'][0]
        distances = results['distances'][0]
        
        # Format for UI
        raw_chunks = [{"text": c, "score": d} for c, d in zip(chunks, distances)]
        
        # IA Response
        context = '\n---\n'.join(chunks)
        prompt = f"Basándote en el siguiente contexto, responde la pregunta.\n\nContexto:\n{context}\n\nPregunta: {question}"
        response = ollama.chat(model='qwen2.5:3b', messages=[
            {'role': 'system', 'content': 'Eres un asistente que responde en español basándose en el contexto proporcionado.'},
            {'role': 'user', 'content': prompt}
        ])
        
        return jsonify({
            "chunks": raw_chunks,
            "answer": response['message']['content']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
