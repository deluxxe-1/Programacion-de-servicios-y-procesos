import chromadb
import ollama
import textwrap

# 1. Texto largo sobre el espacio
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

# 2. Función para dividir el texto en chunks
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

# 3. Embedding personalizado con Ollama
class OllamaEmbeddings:
    def __call__(self, input):
        embeddings = []
        for text in input:
            response = ollama.embed(model='nomic-embed-text', input=text)
            embeddings.append(response['embeddings'][0])
        return embeddings

def inicializar_bd():
    print("Inicializando Base de Datos Vectorial...")
    client = chromadb.PersistentClient(path='./chroma_rag_basico')
    
    # Creamos o recuperamos la colección
    collection = client.get_or_create_collection(
        name='espacio',
        embedding_function=OllamaEmbeddings()
    )
    
    # Si está vacía, añadimos los documentos
    if collection.count() == 0:
        print("Procesando texto y generando embeddings...")
        chunks = chunk_text(texto_espacio)
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids)
        print(f"✅ Se han procesado e insertado {len(chunks)} fragmentos.")
    else:
        print(f"✅ Colección lista. Contiene {collection.count()} fragmentos.")
        
    return collection

# 4. Bucle principal
def main():
    print("\n" + "="*50)
    print(" RAG Básico - Búsqueda Vectorial sobre el Espacio")
    print("="*50)
    
    collection = inicializar_bd()
    
    print("\nEscribe tu pregunta (o 'salir' para terminar).")
    while True:
        query = input("\n👉 Pregunta: ")
        if query.lower() in ['salir', 'exit', 'quit']:
            break
            
        if not query.strip():
            continue
            
        print("\nBuscando en la base de datos...")
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        
        print("\n--- Resultados Encontrados (Chunks Crudos) ---")
        for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"\n[Relevancia: {dist:.4f}] Chunk {i+1}:")
            # Envolvemos el texto para que se lea mejor en la terminal
            wrapped_text = textwrap.fill(doc, width=80)
            print(wrapped_text)
            print("-" * 40)

if __name__ == '__main__':
    main()
