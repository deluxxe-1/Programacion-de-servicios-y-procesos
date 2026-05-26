import chromadb
import ollama
import textwrap

# 1. Texto largo sobre el espacio (Mismo que el ejercicio 1)
texto_espacio = """
El universo es la totalidad del espacio y del tiempo, de todas las formas de la materia, la energía, el impulso, las leyes y constantes físicas que las gobiernan. Sin embargo, el término también se utiliza en sentidos contextuales ligeramente diferentes y alude a conceptos como cosmos, mundo o naturaleza.
El sistema solar es el sistema planetario que liga gravitacionalmente a un conjunto de objetos astronómicos que giran directa o indirectamente en una órbita alrededor de una única estrella conocida con el nombre de Sol. La estrella concentra el 99.86 % de la masa del sistema solar, y la mayor parte de la masa restante se concentra en ocho planetas cuyas órbitas son prácticamente circulares y transitan dentro de un disco casi llano llamado plano eclíptico.
Mercurio es el planeta del sistema solar más cercano al Sol y el más pequeño. Forma parte de los denominados planetas interiores y carece de satélites naturales.
Venus es el segundo planeta del sistema solar en orden de proximidad al Sol y el tercero en cuanto a tamaño en orden ascendente después de Mercurio y Marte.
La Tierra es un planeta del sistema solar que gira alrededor de su estrella —el Sol— en la tercera órbita más interna. Es el más denso y el quinto mayor de los ocho planetas del sistema solar. También es el mayor de los cuatro terrestres o rocosos.
Marte es el cuarto planeta en orden de distancia al Sol y el segundo más pequeño del sistema solar, después de Mercurio. Recibió su nombre en homenaje al dios de la guerra de la mitología romana, y también es conocido como "el planeta rojo" debido a la apariencia rojiza que le confiere el óxido de hierro predominante en su superficie.
Júpiter es el planeta más grande del sistema solar y el quinto en orden de lejanía al Sol. Se trata de un gigante gaseoso que forma parte de los denominados planetas exteriores.
Saturno es el sexto planeta del sistema solar contando desde el Sol, el segundo en tamaño y masa después de Júpiter y el único con un sistema de anillos visible desde la Tierra.
Urano es el séptimo planeta del sistema solar, el tercero de mayor tamaño, y el cuarto más masivo. Se llama así en honor de la divinidad griega del cielo Urano.
Neptuno es el octavo planeta en distancia respecto al Sol y el más lejano del sistema solar. Forma parte de los denominados planetas exteriores, y dentro de estos, es uno de los gigantes helados, y es el primero que fue descubierto gracias a predicciones matemáticas.
Los agujeros negros son regiones finitas del espacio en cuyo interior existe una concentración de masa lo suficientemente elevada como para generar un campo gravitatorio tal que ninguna partícula material, ni siquiera la luz, puede escapar de ella.
La Vía Láctea es una galaxia espiral donde se encuentra el sistema solar y a su vez se encuentra la Tierra. Según las observaciones, posee una masa de 10^12 masas solares y es una espiral barrada.
La Estación Espacial Internacional (ISS) es un centro de investigación en la órbita terrestre, cuya administración, gestión y desarrollo están a cargo de la cooperación internacional. El proyecto funciona como una estación espacial permanentemente tripulada, en la que rotan equipos de astronautas e investigadores de las cinco agencias espaciales participantes.
El Big Bang o gran explosión es el modelo cosmológico predominante para los períodos conocidos más antiguos del universo y su posterior evolución a gran escala.
Los exoplanetas son aquellos planetas que orbitan una estrella diferente al Sol y que, por lo tanto, no pertenecen al sistema solar.
La materia oscura es un tipo de materia que se estima corresponde aproximadamente al 27% de la materia del universo, y que no es energía oscura, materia bariónica (materia ordinaria) ni neutrinos. Su nombre hace referencia a que se considera que no emite ningún tipo de radiación electromagnética.
"""

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

def inicializar_bd():
    client = chromadb.PersistentClient(path='./chroma_rag_ia')
    collection = client.get_or_create_collection(
        name='espacio',
        embedding_function=OllamaEmbeddings()
    )
    if collection.count() == 0:
        chunks = chunk_text(texto_espacio)
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)
    return collection

def main():
    print("\n" + "="*50)
    print(" RAG + IA - Procesamiento de Fragmentos Crudos")
    print("="*50)
    
    collection = inicializar_bd()
    
    print("\nEscribe tu pregunta (o 'salir' para terminar).")
    while True:
        query = input("\n Pregunta: ")
        if query.lower() in ['salir', 'exit', 'quit']:
            break
            
        if not query.strip():
            continue
            
        # 1. Recuperar contexto (chunks crudos)
        print("\n[Buscando en la BD...]")
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        chunks = results['documents'][0]
        
        print("\n" + "="*40)
        print("  CHUNKS CRUDOS RECUPERADOS")
        print("="*40)
        for i, chunk in enumerate(chunks):
            print(f"--- Chunk {i+1} ---")
            print(textwrap.fill(chunk, width=80))
        
        # 2. Generar respuesta con IA
        print("\n" + "="*40)
        print("  RESPUESTA PROCESADA POR IA")
        print("="*40)
        
        context = '\n---\n'.join(chunks)
        prompt = f"""Basándote ÚNICAMENTE en el siguiente contexto, responde la pregunta del usuario.
Si la información no está en el contexto, indica que no tienes información suficiente.
Responde de forma clara, natural y en español.

Contexto:
{context}

Pregunta: {query}"""
        
        # Usamos qwen2.5:3b para redactar la respuesta humana
        print("[Generando respuesta humana con qwen2.5:3b...]")
        response = ollama.chat(model='qwen2.5:3b', messages=[
            {'role': 'system', 'content': 'Eres un asistente experto en astronomía que responde basándose estrictamente en el contexto proporcionado.'},
            {'role': 'user', 'content': prompt}
        ])
        
        print("\n" + textwrap.fill(response['message']['content'], width=80))
        print("\n" + "-"*50)

if __name__ == '__main__':
    main()
