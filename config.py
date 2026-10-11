import os
import dotenv

dotenv.load_dotenv()
# --- API Keys ---
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

# --- Model Settings ---
LLM_MODEL="openai/gpt-oss-120b"
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=1024
EMBEDDINGS_MODEL="sentence-transformers/all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL="cross-encoder/ms-marco-MiniLM-L-6-v2"
EVALUATOR_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
EVAL_EMBEDDING="all-MiniLM-L6-v2"

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_FOLDERS = [
    os.path.join(BASE_DIR, "datasets", "kebo1dd"),
    os.path.join(BASE_DIR, "datasets", "lebo1dd"),
]
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "index", "neet_bio_faiss_index")

# --- Retriever Settings ---
BM25_K=5
FAISS_K=5
ENSEMBLE_WEIGHTS=[0.35,0.65]
TOP_K_RERANK=3

# --- Chapter Map ---
_K = os.path.join(BASE_DIR, "datasets", "kebo1dd")
_L = os.path.join(BASE_DIR, "datasets", "lebo1dd")
CHAPTER_MAP={
    os.path.join(_K, "kebo101.pdf"): "Class 11 The Living World",
    os.path.join(_K, "kebo102.pdf"): "Class 11 Biological Classification",
    os.path.join(_K, "kebo103.pdf"): "Class 11 Plant Kingdom",
    os.path.join(_K, "kebo104.pdf"): "Class 11 Animal Kingdom",
    os.path.join(_K, "kebo105.pdf"): "Class 11 Morphology of Flowering Plants",
    os.path.join(_K, "kebo106.pdf"): "Class 11 Anatomy of Flowering Plants",
    os.path.join(_K, "kebo107.pdf"): "Class 11 Structural Organisation in Animals",
    os.path.join(_K, "kebo108.pdf"): "Class 11 Cell: The Unit of Life",
    os.path.join(_K, "kebo109.pdf"): "Class 11 Biomolecules",
    os.path.join(_K, "kebo110.pdf"): "Class 11 Cell Cycle and Cell Division",
    os.path.join(_K, "kebo111.pdf"): "Class 11 Photosynthesis in Higher Plants",
    os.path.join(_K, "kebo112.pdf"): "Class 11 Respiration in Plants",
    os.path.join(_K, "kebo113.pdf"): "Class 11 Plant Growth and Development",
    os.path.join(_K, "kebo114.pdf"): "Class 11 Breathing and Exchange of Gases",
    os.path.join(_K, "kebo115.pdf"): "Class 11Body Fluids and Circulation",
    os.path.join(_K, "kebo116.pdf"): "Class 11 Excretory Products and their Elimination",
    os.path.join(_K, "kebo117.pdf"): "Class 11 Locomotion and Movement",
    os.path.join(_K, "kebo118.pdf"): "Class 11Neural Control and Coordination",
    os.path.join(_K, "kebo119.pdf"): "Class 11 Chemical Coordination and Integration",
    os.path.join(_K, "kebo1ps.pdf"): "Class 11 Book Back Answers",
    os.path.join(_L, "lebo101.pdf"): "Class 12 Sexual Reproduction in Flowering Plants",
    os.path.join(_L, "lebo102.pdf"): "Class 12 Human Reproduction",
    os.path.join(_L, "lebo103.pdf"): "Class 12 Reproductive Health",
    os.path.join(_L, "lebo104.pdf"): "Class 12 Principles of Inheritance and Variation",
    os.path.join(_L, "lebo105.pdf"): "Class 12 Molecular Basis of Inheritance",
    os.path.join(_L, "lebo106.pdf"): "Class 12 Evolution",
    os.path.join(_L, "lebo107.pdf"): "Class 12 Human Health and Disease",
    os.path.join(_L, "lebo108.pdf"): "Class 12 Microbes in Human Welfare",
    os.path.join(_L, "lebo109.pdf"): "Class 12 Biotechnology: Principles and Processes",
    os.path.join(_L, "lebo110.pdf"): "Class 12 Biotechnology and its Applications",
    os.path.join(_L, "lebo111.pdf"): "Class 12 Organisms and Populations",
    os.path.join(_L, "lebo112.pdf"): "Class 12 Ecosystem",
    os.path.join(_L, "lebo113.pdf"): "Class 12 Biodiversity and Conservation",
    os.path.join(_L, "lebo1ps.pdf"): "Class 12 Class 12 Book Back Answers",
}